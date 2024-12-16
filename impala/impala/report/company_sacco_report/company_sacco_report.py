# Import the frappe module
import frappe

# Define the function to execute the report
def extract_numeric_part(employee):
    # Find the numeric part in the employee field
    numeric_part = ''.join(filter(str.isdigit, employee))
    return numeric_part
def execute(filters=None):
    # Define the columns for the report
    columns = [
    {
            "label": "Employee Number",
            "fieldname": "employee",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Employee Name",
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Department",
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 150
        },
        {
            "label": "Impala Sacco",
            "fieldname": "impala_sacco",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Category Name",
            "fieldname": "employment_type",
            "fieldtype": "Data",
            "width": 150
        }
    ]

    # Fetch data from the 'tabSalary Slip' table with details from 'tabSalary Detail' and 'tabEmployee'
    sql_query = """
        SELECT
            s.`name` AS salary_slip_no,
            s.`employee`,
            s.`employee_name`,
            s.`department`,
            sd.`amount` AS impala_sacco,
            e.`employment_type`
        FROM
            `tabSalary Slip` s
        LEFT JOIN
            `tabSalary Detail` sd ON s.`name` = sd.`parent`
        LEFT JOIN
            `tabEmployee` e ON s.`employee` = e.`name`
        WHERE
            sd.`salary_component` = 'COOP/SACCO'
    """

    # Apply filters to the query
    conditions = []
    if filters.get("employee"):
        conditions.append(f"s.`employee` = '{filters['employee']}'")
    if filters.get("company"):
        conditions.append(f"s.`company` = '{filters['company']}'")
    if filters.get("docstatus"):
        conditions.append(f"s.`docstatus` = '{filters['docstatus']}'")
    if filters.get("from_date"):
        conditions.append(f"s.`start_date` >= '{filters['from_date']}'")
    if filters.get("to_date"):
        conditions.append(f"s.`end_date` <= '{filters['to_date']}'")

    if conditions:
        sql_query += " AND " + " AND ".join(conditions)

    data = frappe.db.sql(sql_query, as_dict=True)
    for record in data:
        record['employee'] = extract_numeric_part(record['employee'])
    return columns, data

