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
        department_cost_center = {}
        
        if parties:
            # Get party names based on party type with disabled party condition
            disabled_condition = "" if self.filters.get("disabled_party") else "AND disabled = 0"
            
            if self.filters.party_type == "Customer":
                party_names = dict(frappe.db.sql("""
                    SELECT name, customer_name as party_name 
                    FROM `tabCustomer` 
                    WHERE name IN %s {disabled_condition}
                """.format(disabled_condition=disabled_condition), [parties]))
            else:
                party_names = dict(frappe.db.sql("""
                    SELECT name, supplier_name as party_name 
                    FROM `tabSupplier` 
                    WHERE name IN %s {disabled_condition}
                """.format(disabled_condition=disabled_condition), [parties]))

            # Get latest department and cost center for each party
            dept_cost_results = frappe.db.sql("""
                SELECT 
                    party,
                    department,
                    cost_center
                FROM (
                    SELECT 
                        party,
                        department,
                        cost_center,
                        ROW_NUMBER() OVER(PARTITION BY party ORDER BY posting_date DESC, creation DESC) as rn
                    FROM `tabGL Entry`
                    WHERE 
                        party_type = %s 
                        AND party IN %s
                        AND company = %s
                        AND (department IS NOT NULL OR cost_center IS NOT NULL)
                ) ranked
                WHERE rn = 1
            """, (self.filters.party_type, parties, self.filters.company), as_dict=1)

            # Convert results to the required format
            for result in dept_cost_results:
                department_cost_center[result.party] = {
                    'department': result.department,
                    'cost_center': result.cost_center
                }

        # Get PD cheques
        pd_cheques = frappe.db.sql("""
            SELECT 
                party, 
                SUM(base_amount) as amount
            FROM `tabPosted Dated Cheques`
            WHERE 
                status = 'Pending' 
                AND docstatus = 1
                AND company = %(company)s
                AND party_type = %(party_type)s
                AND posting_date <= %(report_date)s
            GROUP BY party
        """, self.filters, as_dict=1)
        pd_cheques_map = {d.party: d.amount for d in pd_cheques}

        # Format final data
        self.data = []
        for row in summary_data:
            pd_amount = pd_cheques_map.get(row.party, 0)
            party_info = department_cost_center.get(row.party, {})
            
            formatted_row = frappe._dict({
                "party": row.party,
                "party_name": party_names.get(row.party, ''),
                "party_group": row.get("customer_group" if self.filters.party_type == "Customer" else "supplier_group"),
                "department": party_info.get('department'),
                "cost_center": party_info.get('cost_center'),
                "outstanding": row.outstanding,
                "pd_cheques": pd_amount,
                "net_outstanding": row.outstanding - pd_amount,
                "range1": row.range1,
                "range2": row.range2,
                "range3": row.range3,
                "range4": row.range4,
                "range5": row.range5
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
                "label": _("Department"),
                "fieldname": "department",
                "fieldtype": "Link",
                "options": "Department",
                "width": 150
            },
            {
                "label": _("Division"),
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "options": "Cost Center",
                "width": 150
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