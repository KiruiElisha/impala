# Import the required modules
import frappe
from datetime import datetime

# Define the execute function for the report
def execute(filters=None):
    # Define the columns for the report
    columns = [
        {"label": "Loan Name", "fieldname": "name", "fieldtype": "Link", "options": "Loan", "width": 120},
        {"label": "Applicant", "fieldname": "applicant", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Applicant Type", "fieldname": "applicant_type", "fieldtype": "Data", "width": 120},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Repay From Salary", "fieldname": "repay_from_salary", "fieldtype": "Check", "width": 120},
        {"label": "Loan Type", "fieldname": "loan_type", "fieldtype": "Data", "width": 120},
        {"label": "Loan Amount", "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Repayment Method", "fieldname": "repayment_method", "fieldtype": "Data", "width": 120},
        {"label": "Repayment Period (Months)", "fieldname": "repayment_period", "fieldtype": "Int", "width": 120},
        {"label": "Monthly Repayment Amount", "fieldname": "monthly_repayment_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Repayment Start Date", "fieldname": "repayment_start_date", "fieldtype": "Date", "width": 120},
        {"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 120},
        {"label": "Loan Account", "fieldname": "loan_account", "fieldtype": "Link", "options": "Account", "width": 120},
        {"label": "Payment Account", "fieldname": "payment_account", "fieldtype": "Link", "options": "Account", "width": 120},
        {"label": "Interest Income Account", "fieldname": "interest_income_account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": "Penalty Income Account", "fieldname": "penalty_income_account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": "Total Payment", "fieldname": "total_payment", "fieldtype": "Currency", "width": 120},
        {"label": "Balance Loan", "fieldname": "balance_loan", "fieldtype": "Currency", "width": 120},
        {"label": "Loan Installment Status", "fieldname": "pending", "fieldtype": "Data", "width": 120},
    ]

    # Fetch data from the tabLoan and tabRepayment Schedule tables based on the filters
    data = fetch_data(filters)

    return columns, data

# Define the function to fetch data from the tabLoan and tabRepayment Schedule tables
# Modify the SQL query in the fetch_data function
def fetch_data(filters):
    # Base SQL query
    sql_query = """
        SELECT
            `tabLoan`.`name`,
            `tabLoan`.`applicant_type`,
            `tabLoan`.`company`,
            `tabLoan`.`applicant`,
            `tabLoan`.`posting_date`,
            `tabLoan`.`status`,
            `tabLoan`.`repay_from_salary`,
            `tabLoan`.`loan_type`,
            `tabLoan`.`loan_amount`,
            `tabLoan`.`repayment_method`,
            `tabLoan`.`repayment_periods`,
            `tabLoan`.`monthly_repayment_amount`,
            `tabLoan`.`repayment_start_date`,
            `tabLoan`.`mode_of_payment`,
            `tabLoan`.`loan_account`,
            `tabLoan`.`payment_account`,
            `tabLoan`.`interest_income_account`,
            `tabLoan`.`penalty_income_account`,
            `tabRepayment Schedule`.`total_payment` as total_payment,
            `tabRepayment Schedule`.`balance_loan_amount` as balance_loan,
            CASE
                WHEN `tabRepayment Schedule`.`payment_date` <= CURDATE() THEN 'Paid'
                ELSE 'Pending'
            END as pending
        FROM
            `tabLoan`
        LEFT JOIN
            `tabRepayment Schedule` ON `tabLoan`.`name` = `tabRepayment Schedule`.`parent`
    """

    # Apply filters if present
    conditions = []

    # Filter by 'name'
    if filters.get("name"):
        conditions.append(f"`tabLoan`.`name` = '{filters['name']}'")
    if filters.get("applicant_type"):
        conditions.append(f"`tabLoan`.`applicant_type` = '{filters['applicant_type']}'")
    if filters.get("status"):
        conditions.append(f"`tabLoan`.`status` = '{filters['status']}'")

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)
    sql_query += " ORDER BY `tabRepayment Schedule`.`payment_date` ASC"
    # sql_query += " GROUP BY `tabLoan`.`name`"

    result = frappe.db.sql(sql_query, as_dict=True)

    return result
