import frappe

def execute(filters=None):
    conditions = ""
    if filters.get("employee"):
        conditions += f" AND employee = '{filters.get('employee')}'"
    if filters.get("from_date"):
        conditions += f" AND from_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND to_date <= '{filters.get('to_date')}'"
    if filters.get("leave_type"):
        conditions += f" AND leave_type = '{filters.get('leave_type')}'"

    columns = [
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 100},
        {"label": "Employee No", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 250},
        {"label": "Leave Name", "fieldname": "leave_type", "fieldtype": "Link", "options": "Leave Type", "width": 150},
        {"label": "Quota", "fieldname": "quota", "fieldtype": "Data", "width": 100},
        {"label": "Opb Bal", "fieldname": "unused_leaves", "fieldtype": "Data", "width": 100},
        {"label": "Taken", "fieldname": "new_leaves_allocated", "fieldtype": "Data", "width": 100},
        {"label": "Encash", "fieldname": "total_leaves_encashed", "fieldtype": "Data", "width": 100},
        {"label": "Cumulative", "fieldname": "carry_forwarded_leaves_count", "fieldtype": "Data", "width": 100},
        {"label": "Total", "fieldname": "total_leaves_allocated", "fieldtype": "Data", "width": 100}
    ]

    # Fetch data grouped by department
    data = frappe.db.sql(f"""
        SELECT
            la.employee,
            la.employee_name,
            la.leave_type,
            (SELECT max_leaves_allowed FROM `tabLeave Type` WHERE name = la.leave_type) AS quota,
            la.unused_leaves, 
            la.new_leaves_allocated, 
            la.total_leaves_encashed,
            la.carry_forwarded_leaves_count,
            la.total_leaves_allocated,
            la.department
        FROM
            `tabLeave Allocation` la
        WHERE
            1 = 1 {conditions}
        ORDER BY
            la.department, la.employee
    """, as_dict=True)

    # Initialize a list to hold the result
    result = []

    current_department = None

    # Iterate through the data and format it
    for row in data:
        if row['department'] != current_department:
            # Add department heading as a separate row with department name bolded
            department_heading = {"department": f'<b> {row["department"]}</b>'}
            result.append(department_heading)
            current_department = row['department']
        # Add the row data
        employee_row = {
            "employee": row["employee"],
            "employee_name": row["employee_name"],
            "leave_type": row["leave_type"],
            "quota": row["quota"],
            "unused_leaves": row["unused_leaves"],
            "new_leaves_allocated": row["new_leaves_allocated"],
            "total_leaves_encashed": row["total_leaves_encashed"],
            "carry_forwarded_leaves_count": row["carry_forwarded_leaves_count"],
            "total_leaves_allocated": row["total_leaves_allocated"],
            "department": ""
        }
        result.append(employee_row)

    return columns, result
