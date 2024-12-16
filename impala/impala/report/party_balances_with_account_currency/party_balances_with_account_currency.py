# Copyright (c) 2024, Codes Soft and contributors
# For license information, please see license.txt

# import frappe

from collections import defaultdict
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    if not filters:
        filters = {}
    
    validate_filters(filters)
    columns = get_columns()
    data = get_party_balances(filters)
    
    return columns, data

def validate_filters(filters):
    if not filters.get('company'):
        frappe.throw(_("Company is mandatory"))
    
    if not filters.get('party_type'):
        frappe.throw(_("Party Type is mandatory"))
        
    if not filters.get('to_date'):
        filters.to_date = frappe.datetime.get_today()
    
    if not filters.get('ageing_based_on'):
        filters.ageing_based_on = "Due Date"

def get_columns():
    return [
        {"label": _("Party"), "fieldname": "party", "fieldtype": "Dynamic Link", "options": "party_type", "width": 150},
        {"label": _("Party Name"), "fieldname": "party_name", "fieldtype": "Data", "width": 150},
        {"label": _("Party Group"), "fieldname": "party_group", "fieldtype": "Data", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"label": _("Division"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Account Currency"), "fieldname": "account_currency", "fieldtype": "Link", "options": "Currency", "width": 100},
        {"label": _("Balance (BC)"), "fieldname": "closing_balance_bc", "fieldtype": "Currency", "width": 150},
        {"label": _("Balance (AC)"), "fieldname": "closing_balance_ac", "fieldtype": "Currency", "options": "account_currency", "width": 150},
        {"label": _("PD Cheques"), "fieldname": "pd_cheques", "fieldtype": "Currency", "width": 150},
        {"label": _("Net Outstanding"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("0-30"), "fieldname": "range1", "fieldtype": "Currency", "width": 150},
        {"label": _("31-60"), "fieldname": "range2", "fieldtype": "Currency", "width": 150},
        {"label": _("61-90"), "fieldname": "range3", "fieldtype": "Currency", "width": 150},
        {"label": _("91-120"), "fieldname": "range4", "fieldtype": "Currency", "width": 150},
        {"label": _("120+"), "fieldname": "range5", "fieldtype": "Currency", "width": 150}
    ]

def get_gl_entries(filters):
    conditions = [
        "gle.docstatus = 1",
        "gle.company = %(company)s",
        "gle.posting_date <= %(to_date)s",
        "gle.party_type = %(party_type)s",
        "gle.is_cancelled = 0",
        "gle.party IS NOT NULL",
        "gle.party != ''"
    ]
    
    if filters.get("party"):
        conditions.append("gle.party = %(party)s")
    if filters.get("department"):
        conditions.append("gle.department = %(department)s")
    if filters.get("division"):
        conditions.append("gle.cost_center = %(division)s")

    return frappe.db.sql("""
        SELECT
            gle.party,
            gle.debit,
            gle.credit,
            gle.debit_in_account_currency,
            gle.credit_in_account_currency,
            gle.account_currency,
            gle.cost_center,
            gle.department,
            gle.posting_date,
            gle.voucher_type,
            CASE 
                WHEN gle.voucher_type = 'Sales Invoice' THEN si.due_date
                WHEN gle.voucher_type = 'Purchase Invoice' THEN pi.due_date
                WHEN gle.voucher_type = 'Journal Entry' THEN je.posting_date
                ELSE gle.posting_date
            END as due_date,
            CASE
                WHEN gle.voucher_type = 'Sales Invoice' THEN si.is_return
                WHEN gle.voucher_type = 'Purchase Invoice' THEN pi.is_return
                ELSE 0
            END as is_return,
            CASE
                WHEN gle.voucher_type = 'Journal Entry' THEN je.voucher_type
                ELSE NULL
            END as journal_entry_type
        FROM `tabGL Entry` gle
        LEFT JOIN `tabSales Invoice` si ON 
            gle.voucher_no = si.name AND 
            gle.voucher_type = 'Sales Invoice'
        LEFT JOIN `tabPurchase Invoice` pi ON 
            gle.voucher_no = pi.name AND 
            gle.voucher_type = 'Purchase Invoice'
        LEFT JOIN `tabJournal Entry` je ON 
            gle.voucher_no = je.name AND 
            gle.voucher_type = 'Journal Entry'
        WHERE {conditions}
        ORDER BY gle.posting_date
    """.format(conditions=" AND ".join(conditions)), filters, as_dict=1)

def get_pd_cheques():
    """Fetch pending post-dated cheques for all parties"""
    return frappe.cache().get_value(
        'party_pd_cheques',
        lambda: _get_pd_cheques_data()
    )

def _get_pd_cheques_data():
    """Helper function to fetch PD cheques data with caching"""
    query = """
        SELECT 
            party,
            SUM(amount) AS pd_cheques
        FROM `tabPosted Dated Cheques`
        WHERE status = 'Pending' 
        AND party IS NOT NULL 
        AND party != ''
        GROUP BY party
    """
    pd_cheques = frappe.db.sql(query, as_dict=True)
    return {entry.party: entry.pd_cheques for entry in pd_cheques}

# Cache party docs to avoid repeated DB calls
party_doc_cache = {}

def get_party_doc(party_type, party):
    """Get cached party document"""
    cache_key = f"{party_type}::{party}"
    if cache_key not in party_doc_cache:
        party_doc_cache[cache_key] = frappe.get_cached_doc(party_type, party)
    return party_doc_cache[cache_key]

def get_party_balances(filters):
    gl_entries = get_gl_entries(filters)
    pd_cheques_dict = get_pd_cheques()
    
    # Pre-calculate to_date
    to_date = getdate(filters.to_date)
    
    data = defaultdict(lambda: {
        "party": "",
        "party_name": "",
        "party_group": "",
        "department": "",
        "cost_center": "",
        "account_currency": "",
        "closing_balance_bc": 0,
        "closing_balance_ac": 0,
        "pd_cheques": 0,
        "net_amount": 0,
        "range1": 0,
        "range2": 0,
        "range3": 0,
        "range4": 0,
        "range5": 0
    })

    for gle in gl_entries:
        try:
            party = gle.party
            if not data[party]["party"]:
                initialize_party_data(data, party, gle, filters, pd_cheques_dict)

            update_balances_and_aging(data, party, gle, filters, to_date)

        except Exception as e:
            frappe.log_error(
                title="Party Balances Report Error",
                message=f"Error processing entry: {str(e)}"
            )

    return filter_zero_balances(data)

def initialize_party_data(data, party, gle, filters, pd_cheques_dict):
    party_doc = get_party_doc(filters.party_type, party)
    data[party].update({
        "party": party,
        "party_name": party_doc.customer_name if filters.party_type == "Customer" else party_doc.supplier_name,
        "party_group": party_doc.customer_group if filters.party_type == "Customer" else party_doc.supplier_group,
        "department": gle.department,
        "cost_center": gle.cost_center,
        "account_currency": gle.account_currency,
        "pd_cheques": pd_cheques_dict.get(party, 0)
    })

def update_balances_and_aging(data, party, gle, filters, to_date):
    # Calculate balance in both base currency and account currency
    balance_bc = flt(gle.debit) - flt(gle.credit)
    balance_ac = flt(gle.debit_in_account_currency) - flt(gle.credit_in_account_currency)
    
    if (gle.is_return or 
        (gle.journal_entry_type and "Credit Note" in gle.journal_entry_type)):
        balance_bc = -balance_bc
        balance_ac = -balance_ac

    data[party]["closing_balance_bc"] += balance_bc
    data[party]["closing_balance_ac"] += balance_ac

    aging_date = (
        gle.due_date if filters.ageing_based_on == "Due Date" and gle.due_date 
        else gle.posting_date
    )
    age = (to_date - getdate(aging_date)).days

    # Update aging buckets (in base currency)
    if age <= 30:
        data[party]["range1"] += balance_bc
    elif age <= 60:
        data[party]["range2"] += balance_bc
    elif age <= 90:
        data[party]["range3"] += balance_bc
    elif age <= 120:
        data[party]["range4"] += balance_bc
    else:
        data[party]["range5"] += balance_bc

def filter_zero_balances(data):
    filtered_data = []
    for party_data in data.values():
        party_data["net_amount"] = party_data["closing_balance_bc"] - party_data["pd_cheques"]
        if party_data["net_amount"] != 0:
            filtered_data.append(party_data)
    return filtered_data

