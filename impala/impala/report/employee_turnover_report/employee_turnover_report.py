# Import the required modules
import frappe

# Define the execute function for the report
def execute(filters=None):
    # Define the columns for the report
    columns = [
        {"label": "Employee Number", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Employee Full Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Employee Type", "fieldname": "employment_type", "fieldtype": "Data", "width": 120},
        {"label": "Employee Group", "fieldname": "employee_group", "fieldtype": "Link", "options": "Employee Group", "width": 120},
        {"label": "Manual Shift Price List", "fieldname": "manual_shift_price_list", "fieldtype": "Link", "options": "Price List", "width": 150},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "National ID", "fieldname": "national_id", "fieldtype": "Data", "width": 120},
        {"label": "Employee Pin", "fieldname": "employee_pin", "fieldtype": "Data", "width": 100},
        {"label": "Type Of Employee", "fieldname": "type_of_employee", "fieldtype": "Data", "width": 120},
        {"label": "Date of Retirement", "fieldname": "date_of_retirement", "fieldtype": "Date", "width": 120},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 120},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 120},
        {"label": "Relieving Date", "fieldname": "relieving_date", "fieldtype": "Date", "width": 120},
    ]

    # Fetch data from the tabEmployee table based on the filters
    data = fetch_data(filters)

    return columns, data

# Define the function to fetch data from the tabEmployee table
def fetch_data(filters):
    # Base SQL query
    sql_query = """
        SELECT
            `name` AS employee,
            `employee_name`,
            `employment_type`,
            `employee_group`,
            `manual_shift_price_list`,
            `date_of_joining`,
            `status`,
            `national_id`,
            `employee_pin`,
            `type_of_employee`,
            `date_of_retirement`,
            `department`,
            `designation`,
            `relieving_date`
        FROM
            `tabEmployee`
    """

    # Apply filters if present
    conditions = []
    if filters.get("employee"):
        conditions.append(f"`employee` = '{filters['employee']}'")
    if filters.get("status"):
        conditions.append(f"`status` = '{filters['status']}'")
    if filters.get("left"):
        # Check if the checkbox is clicked
        if filters["left"]:
            # Add a condition to filter out employees with a relieving_date
            conditions.append("`relieving_date` IS NOT NULL")
    # Add more conditions for other filters as needed

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    result = frappe.db.sql(sql_query, as_dict=True)

    return result
