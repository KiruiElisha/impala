import frappe
from frappe import _
from frappe.utils import nowdate

def fetch_opening_balances(party_type=None, party=None, from_date=None, filters=None):
    condition = "party_type = 'Supplier'"
    if party:
        condition += f" AND party = '{party}'"
    
    # Add party group condition
    party_group = filters.get('party_group')
    if party_group:
        condition += """ AND party IN (
            SELECT name FROM `tabSupplier` 
            WHERE supplier_group = %(party_group)s
        )"""
    
    gl_entries = frappe.db.sql("""
        SELECT 
            party,
            IFNULL(SUM(IF(posting_date < %(from_date)s, debit_in_account_currency - credit_in_account_currency, 0)), 0) AS opening_balance_ac,
            IFNULL(SUM(IF(posting_date < %(from_date)s, debit - credit, 0)), 0) AS opening_balance_bc
        FROM `tabGL Entry`
        WHERE {0}
        GROUP BY party
    """.format(condition), {
        'from_date': from_date,
        'party_group': party_group
    }, as_dict=True)

    return {entry['party']: entry for entry in gl_entries}

def fetch_aging(party_type=None, party=None, filters=None):
    if not filters or not filters.get('party_group'):
        frappe.throw(_("Party Group is mandatory"))

    # Prepare filters for summary report
    summary_filters = {
        "company": filters.get("company"),
        "report_date": filters.get("to_date"),
        "ageing_based_on": filters.get("ageing_based_on", "Posting Date"),
        "range1": 30,
        "range2": 60,
        "range3": 90,
        "range4": 120,
        "party_type": "Supplier"
    }

    if filters.get('party_group'):
        summary_filters["supplier_group"] = filters['party_group']

    if party:
        summary_filters["supplier"] = party

    # Get data from existing reports
    from erpnext.accounts.report.accounts_payable_summary.accounts_payable_summary import execute
    
    _, summary_data = execute(summary_filters)

    # Convert the data into our required format
    aging_data = {}
    for row in summary_data:
        aging_data[row.party] = {
            'party': row.party,
            'party_type': 'Supplier',
            'aging_0_30': row.range1,
            'aging_31_60': row.range2,
            'aging_61_90': row.range3,
            'aging_91_120': row.range4,
            'aging_121_above': row.range5
        }
    
    return aging_data

def fetch_party_names_and_groups(party_group):
    supplier_query = """
        SELECT 
            name AS party_id, 
            supplier_name AS party_name,
            supplier_group AS party_group
        FROM `tabSupplier`
        WHERE supplier_group = %s
    """
    
    supplier_names = frappe.db.sql(supplier_query, [party_group], as_dict=True)
    return {entry['party_id']: {
        'party_name': entry['party_name'], 
        'party_group': entry['party_group']
    } for entry in supplier_names}

def fetch_data(party_type=None, party=None, from_date=None, to_date=None, filters=None):
    if not filters or not filters.get('party_group'):
        frappe.throw(_("Party Group is mandatory"))

    opening_balances = fetch_opening_balances(party_type, party, from_date, filters)
    aging_data = fetch_aging(party_type, party, filters)  
    party_info = fetch_party_names_and_groups(filters.get('party_group'))

    condition = """
        party_type = 'Supplier'
        AND party IN (
            SELECT name FROM `tabSupplier` 
            WHERE supplier_group = %(party_group)s
        )
    """
    
    if party:
        condition += f" AND party = '{party}'"

    query = f"""
        SELECT 
            party,
            department,
            cost_center,
            account_currency,
            SUM(debit) AS total_debit_bc,
            SUM(credit) AS total_credit_bc,
            SUM(debit) AS paid_amount_bc,
            SUM(debit_in_account_currency) AS total_debit_ac,
            SUM(debit_in_account_currency) AS paid_amount_ac,
            SUM(credit_in_account_currency) AS total_credit_ac,
            SUM(IF(posting_date <= %(to_date)s, debit_in_account_currency - credit_in_account_currency, 0)) AS closing_balance_ac,
            SUM(IF(posting_date <= %(to_date)s, debit - credit, 0)) AS closing_balance_bc
        FROM `tabGL Entry`
        WHERE {condition} 
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY party, account_currency
    """
    
    values = {
        'from_date': from_date,
        'to_date': to_date,
        'party_group': filters.get('party_group', '3rd Party Supplier')
    }
    
    gl_entries = frappe.db.sql(query, values, as_dict=True)
    
    for entry in gl_entries:
        entry.update(opening_balances.get(entry['party'], {}))
        entry.update(aging_data.get(entry['party'], {}))
        party_details = party_info.get(entry['party'], {
            'party_name': entry['party'], 
            'party_group': filters.get('party_group', '3rd Party Supplier')
        })
        entry['party_name'] = party_details['party_name']
        entry['party_group'] = party_details['party_group']
    
    return gl_entries

def add_closing_balance(data):
    for row in data:
        opening_balance_ac = row.get("opening_balance_ac", 0)
        closing_balance_ac = row.get("closing_balance_ac", 0)
        row["closing_balance_ac"] = opening_balance_ac + closing_balance_ac

        opening_balance_bc = row.get("opening_balance_bc", 0)
        closing_balance_bc = row.get("closing_balance_bc", 0)
        row["closing_balance_bc"] = opening_balance_bc + closing_balance_bc

    return data

def execute(filters=None):
    if not filters:
        filters = {}
    
    # Enforce mandatory filters
    if not filters.get('party_group'):
        filters['party_group'] = '3rd Party Supplier'
    
    # Validate party group
    if not frappe.db.exists("Supplier Group", filters.get('party_group')):
        frappe.throw(_("Invalid Supplier Group"))
    
    # Set other default filters
    filters['party_type'] = 'Supplier'  # Always supplier
    
    if not filters.get('to_date'):
        filters.to_date = nowdate()
    
    if not filters.get('company'):
        filters['company'] = frappe.defaults.get_user_default('Company')
        
    return get_columns(), get_data(filters)

def get_columns():
    columns = [
        {"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": 150},
        {"label": "Party Name", "fieldname": "party_name", "fieldtype": "Data", "width": 150},
        {"label": "Party Group", "fieldname": "party_group", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": "Division", "fieldname": "cost_center", "fieldtype": "Data", "width": 150},
        {"label": "AC", "fieldname": "account_currency", "fieldtype": "Data", "width": 50},
        {"label": "Total Debit (BC)", "fieldname": "total_debit_bc", "fieldtype": "Currency", "width": 150},
        {"label": "Total Credit (BC)", "fieldname": "total_credit_bc", "fieldtype": "Currency", "width": 150},
        {"label": "Paid Amount (BC)", "fieldname": "paid_amount_bc", "fieldtype": "Currency", "width": 150},
        {"label": "Total Debit (AC)", "fieldname": "total_debit_ac", "fieldtype": "Currency", "width": 150},
        {"label": "Total Credit (AC)", "fieldname": "total_credit_ac", "fieldtype": "Currency", "width": 150},
        {"label": "Closing Balance (AC)", "fieldname": "closing_balance_ac", "fieldtype": "Currency", "width": 150},
        {"label": "Closing Balance (BC)", "fieldname": "closing_balance_bc", "fieldtype": "Currency", "width": 150},
        {"label": "Aging 0-30", "fieldname": "aging_0_30", "fieldtype": "Currency", "width": 150},
        {"label": "Aging 31-60", "fieldname": "aging_31_60", "fieldtype": "Currency", "width": 150},
        {"label": "Aging 61-90", "fieldname": "aging_61_90", "fieldtype": "Currency", "width": 150},
        {"label": "Aging 91-120", "fieldname": "aging_91_120", "fieldtype": "Currency", "width": 150},
        {"label": "Aging 121+", "fieldname": "aging_121_above", "fieldtype": "Currency", "width": 150},
    ]
    
    return columns

def get_data(filters):
    data = fetch_data(
        party_type=filters.get('party_type'),
        party=filters.get('party'),
        from_date=filters['from_date'],
        to_date=filters['to_date'],
        filters=filters
    )

    data = add_closing_balance(data)

    return data