from collections import OrderedDict
import frappe
from frappe import _, scrub
from frappe.utils import cint, cstr, flt, getdate, nowdate
from erpnext.accounts.utils import get_currency_precision

def execute(filters=None):
    if not filters:
        filters = {}
    
    if not filters.get('company'):
        frappe.throw(_("Company is mandatory"))
    
    if not filters.get('party_type'):
        filters.party_type = "Customer"
        
    if not filters.get('to_date'):
        filters.to_date = nowdate()

    return NetOutstandingReport(filters).run()

class NetOutstandingReport:
    def __init__(self, filters):
        self.filters = frappe._dict(filters)
        self.filters.report_date = getdate(self.filters.to_date)
        self.currency_precision = get_currency_precision() or 2

    def run(self):
        self.get_columns()
        self.get_data()
        return self.columns, self.data

    def get_data(self):
        # Get aging data from summary report
        summary_filters = {
            "company": self.filters.company,
            "report_date": self.filters.report_date,
            "ageing_based_on": self.filters.ageing_based_on,
            "range1": 30,
            "range2": 60,
            "range3": 90,
            "range4": 120,
            "party_type": self.filters.party_type
        }

        if self.filters.get("party"):
            if self.filters.party_type == "Customer":
                summary_filters["customer"] = self.filters.party
            else:
                summary_filters["supplier"] = self.filters.party

        if self.filters.get("party_group"):
            if self.filters.party_type == "Customer":
                summary_filters["customer_group"] = self.filters.party_group
            else:
                summary_filters["supplier_group"] = self.filters.party_group

        # Get summary data
        summary_data = get_summary(summary_filters)[1]

        if not summary_data:
            self.data = []
            return

        # Get party names
        parties = [d.party for d in summary_data]
        party_names = {}
        
        if parties:
            # Get party names based on party type
            if self.filters.party_type == "Customer":
                party_names = dict(frappe.db.sql("""
                    SELECT name, customer_name as party_name 
                    FROM `tabCustomer` 
                    WHERE name IN %s
                """, [parties]))
            else:
                party_names = dict(frappe.db.sql("""
                    SELECT name, supplier_name as party_name 
                    FROM `tabSupplier` 
                    WHERE name IN %s
                """, [parties]))

        # Get PD cheques for all parties in summary_data
        pd_cheques = frappe.db.sql("""
            SELECT 
                party, 
                SUM(base_amount) as amount
            FROM `tabPosted Dated Cheques`
            WHERE 
                status = 'Pending' 
                AND docstatus = 1
                AND party IN %(parties)s
            GROUP BY party
        """, {'parties': parties}, as_dict=1)
        pd_cheques_map = {d.party: d.amount for d in pd_cheques}

        # Get GL Entry balances in account currency
        gl_entries = frappe.db.sql("""
            SELECT 
                party,
                account_currency,
                SUM(debit_in_account_currency - credit_in_account_currency) as balance_in_account_currency
            FROM `tabGL Entry`
            WHERE 
                party_type = %s
                AND party IN (%s)
                AND posting_date <= %s
                AND is_cancelled = 0
            GROUP BY party, account_currency
        """ % ('%s', ', '.join(['%s']*len(parties)), '%s'), 
        tuple([self.filters.party_type] + parties + [self.filters.report_date]), as_dict=1)

        # Create a mapping of party to GL balances and account currency
        gl_balances = {entry.party: entry for entry in gl_entries}

        # Format final data
        self.data = []
        for row in summary_data:
            pd_amount = pd_cheques_map.get(row.party, 0)
            
            # Add balance in account currency and account currency from GL entries
            gl_balance = gl_balances.get(row.party, {})
            balance_in_account_currency = gl_balance.get('balance_in_account_currency', 0.0)
            account_currency = gl_balance.get('account_currency', '')

            formatted_row = frappe._dict({
                "party": row.party,
                "party_name": party_names.get(row.party, ''),
                "party_group": row.get("customer_group" if self.filters.party_type == "Customer" else "supplier_group"),
                "department": row.get("department"),
                "cost_center": row.get("cost_center"),
                "outstanding": row.outstanding,
                "pd_cheques": pd_amount,
                "net_outstanding": row.outstanding - pd_amount,
                "range1": row.range1,
                "range2": row.range2,
                "range3": row.range3,
                "range4": row.range4,
                "range5": row.range5,
                "account_currency": account_currency,
                "balance_in_account_currency": balance_in_account_currency
            })

            if abs(formatted_row.net_outstanding) > (1.0/10 ** self.currency_precision):
                self.data.append(formatted_row)

    def get_columns(self):
        self.columns = [
            {
                "label": _("Party"),
                "fieldname": "party",
                "fieldtype": "Link",
                "options": self.filters.party_type,
                "width": 180
            },
            {
                "label": _("Party Name"),
                "fieldname": "party_name",
                "fieldtype": "Data",
                "width": 180
            },
            {
                "label": _("Party Group"),
                "fieldname": "party_group",
                "fieldtype": "Link",
                "options": self.filters.party_type == "Customer" and "Customer Group" or "Supplier Group",
                "width": 180
            },
            
            {
                "label": _("Account Currency"),
                "fieldname": "account_currency",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": _("Balance (AC)"),
                "fieldname": "balance_in_account_currency",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 180
            },           
            {
                "label": _("Balance"),
                "fieldname": "outstanding",
                "fieldtype": "Currency",
                "width": 150
            },
            {
                "label": _("PD Cheques"),
                "fieldname": "pd_cheques",
                "fieldtype": "Currency",
                "width": 150
            },
            {
                "label": _("Net Outstanding"),
                "fieldname": "net_outstanding",
                "fieldtype": "Currency",
                "width": 150
            },
            {
                "label": _("0-30"),
                "fieldname": "range1",
                "fieldtype": "Currency",
                "width": 130
            },
            {
                "label": _("31-60"),
                "fieldname": "range2",
                "fieldtype": "Currency",
                "width": 130
            },
            {
                "label": _("61-90"),
                "fieldname": "range3",
                "fieldtype": "Currency",
                "width": 130
            },
            {
                "label": _("91-120"),
                "fieldname": "range4",
                "fieldtype": "Currency",
                "width": 130
            },
            {
                "label": _("120+"),
                "fieldname": "range5",
                "fieldtype": "Currency",
                "width": 130
            }
        ]

@frappe.whitelist()
def get_summary(filters):
    if filters.get("party_type") == "Customer":
        from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import execute
        return execute(filters)
    if filters.get("party_type") == "Supplier":
        from erpnext.accounts.report.accounts_payable_summary.accounts_payable_summary import execute
        return execute(filters)