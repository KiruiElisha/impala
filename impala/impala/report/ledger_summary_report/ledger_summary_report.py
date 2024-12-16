import frappe
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import execute as execute_receivable
from erpnext.accounts.report.accounts_payable_summary.accounts_payable_summary import execute as execute_payable

def fetch_opening_balances(party_type=None, party=None, from_date=None):
    """
    Fetches opening balances for parties.

    Args:
        party_type (str): Type of party.
        party (str): Party name.
        from_date (str): Start date.

    Returns:
        dict: Opening balances for parties.
    """
    limit_clause = "LIMIT 1000"
    condition = ""
    if party_type:
        condition += f" AND party_type = '{party_type}'"
    if party:
        condition += f" AND party = '{party}'"
    
    gl_entries = frappe.db.sql(f"""
        SELECT 
            party,
            IFNULL(SUM(IF(posting_date < %s, debit_in_account_currency - credit_in_account_currency, 0)), 0) AS opening_balance_ac,
            IFNULL(SUM(IF(posting_date < %s, debit - credit, 0)), 0) AS opening_balance_bc
        FROM `tabGL Entry`
        WHERE 1=1 {condition} 
        GROUP BY party
        {limit_clause}
    """, (from_date, from_date), as_dict=True)

    return {entry['party']: entry for entry in gl_entries}

def fetch_data(party_type=None, party=None, from_date=None, to_date=None):
    """
    Fetches financial data for parties based on given parameters.

    Args:
        party_type (str): Type of party.
        party (str): Party name.
        from_date (str): Start date.
        to_date (str): End date.

    Returns:
        list: Financial data for parties.
    """
    limit_clause = "LIMIT 1000"
    voucher_type = 'Payment Entry'
    opening_balances = fetch_opening_balances(party_type, party, from_date)
    condition = ""
    if party_type:
        condition += f" AND party_type = '{party_type}'"
    if party:
        condition += f" AND party = '{party}'"

    gl_entries = frappe.db.sql(f"""
        SELECT 
            party,
            account_currency,            
            SUM(debit) AS total_debit_bc,
            SUM(credit) AS total_credit_bc,
            SUM(debit) AS paid_amount_bc,
            SUM(debit_in_account_currency) AS total_debit_ac,
            SUM(debit_in_account_currency) AS paid_amount_ac,
            SUM(credit_in_account_currency) AS total_credit_ac,
            SUM(IF(posting_date <= %s, debit_in_account_currency - credit_in_account_currency, 0)) AS closing_balance_ac,
            SUM(IF(posting_date <= %s, debit - credit, 0)) AS closing_balance_bc
        FROM `tabGL Entry`
        WHERE 1=1 {condition} AND posting_date BETWEEN %s AND %s AND voucher_type=%s
        GROUP BY party
        {limit_clause}
    """, (to_date, to_date, from_date, to_date, voucher_type), as_dict=True)
    
    # Fetch aging data from external report
    aging_data = get_aging_data({
        "party_type": party_type,
        "party": party,
        "to_date": to_date
    })

    for entry in gl_entries:
        opening_balance = opening_balances.get(entry['party'])
        if opening_balance:
            entry.update(opening_balance)
        
        # Update entry with aging data
        aging_entry = aging_data.get(entry['party'], {})
        entry.update(aging_entry)

    return gl_entries

def get_aging_data(filters):
    """
    Fetches aging data from an external report.

    Args:
        filters (dict): Filters for the aging report.

    Returns:
        dict: Aging data keyed by party.
    """
    # Ensure the filters include the necessary aging ranges
    filters.update({
        "range1": 30,
        "range2": 60,
        "range3": 90,
        "range4": 120
    })

    if filters.get("party_type") == "Customer":
        summary_data = execute_receivable(filters)[1]
    elif filters.get("party_type") == "Supplier":
        summary_data = execute_payable(filters)[1]
    else:
        return {}

    aging_data = {}
    for row in summary_data:
        aging_data[row.party] = {
            "aging_0_30": row.range1,
            "aging_31_60": row.range2,
            "aging_61_90": row.range3,
            "aging_91_120": row.range4,
            "aging_121_above": row.range5
        }
    return aging_data

def add_closing_balance(data):
    """
    Adds closing balances to the financial data.

    Args:
        data (list): List of financial data.

    Returns:
        list: List of financial data with closing balances added.
    """
    for row in data:
        opening_balance_ac = row.get("opening_balance_ac") or 0
        closing_balance_ac = row.get("closing_balance_ac") or 0
        row["closing_balance_ac"] = opening_balance_ac + closing_balance_ac

        opening_balance_bc = row.get("opening_balance_bc") or 0
        closing_balance_bc = row.get("closing_balance_bc") or 0
        row["closing_balance_bc"] = opening_balance_bc + closing_balance_bc

    return data

def execute(filters=None):
    """
    Fetches financial data based on given filters.

    Args:
        filters (dict): Filters for the data.

    Returns:
        tuple: Columns and data fetched from the database.
    """
    columns = [
        {"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": 150},
        {"label": "AC", "fieldname": "account_currency", "fieldtype": "Data", "width": 50},        
        {"label": "Opening Balance (Account Currency)", "fieldname": "opening_balance_ac", "fieldtype": "Data", "width": 200},
        {"label": "Debit (Account Currency)", "fieldname": "total_debit_ac", "fieldtype": "Data", "width": 200},
        {"label": "Credit (Account Currency)", "fieldname": "total_credit_ac", "fieldtype": "Data", "width": 200},
        {"label": "Closing Balance (Account Currency)", "fieldname": "closing_balance_ac", "fieldtype": "Data", "width": 100},
        {"label": "Paid Amount(Account Currecy)", "fieldname": "paid_amount_ac", "fieldtype": "Data", "width": 100},
        {"label": "Opening Balance (Base Currency)", "fieldname": "opening_balance_bc", "fieldtype": "Data", "width": 200},
        {"label": "Total Debit (Base Currency)", "fieldname": "total_debit_bc", "fieldtype": "Data", "width": 200},
        {"label": "Total Credit (Base Currency)", "fieldname": "total_credit_bc", "fieldtype": "Data", "width": 200},
        {"label": "Closing Balance (Base Currency)", "fieldname": "closing_balance_bc", "fieldtype": "Data", "width": 150},
        {"label": "Paid Amount(Base Currency)", "fieldname": "paid_amount_bc", "fieldtype": "Data", "width": 100},
        {"label": "0-30 Days", "fieldname": "aging_0_30", "fieldtype": "Data", "width": 150},
        {"label": "31-60 Days", "fieldname": "aging_31_60", "fieldtype": "Data", "width": 150},
        {"label": "61-90 Days", "fieldname": "aging_61_90", "fieldtype": "Data", "width": 150},
        {"label": "91-120 Days", "fieldname": "aging_91_120", "fieldtype": "Data", "width": 150},
        {"label": "121+ Days", "fieldname": "aging_121_above", "fieldtype": "Data", "width": 150},
    ]
    data = fetch_data(filters.get("party_type"), filters.get("party"), filters.get("from_date"), filters.get("to_date"))
    data = add_closing_balance(data)
    
    return columns, data

