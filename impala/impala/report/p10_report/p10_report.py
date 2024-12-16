import frappe

def execute(filters=None):
    columns = [
        # {
        #     "label": "EMPLOYEE",
        #     "fieldname": "employee",
        #     "fieldtype": "Link",
        #     "options": "Employee",
        #     "width": 150
        # },
        {
            "label": "EMPLOYEE'S PIN",
            "fieldname": "employee_pin",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "EMPLOYEE`S NAME",
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "TOTAL EMOLUMENTS",
            "fieldname": "deductions",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "TOTAL DEDUCTED",
            "fieldname": "earnings",
            "fieldtype": "Currency",
            "width": 120
        }
    ]

    data = fetch_data(filters)

    # Add a row for the totals at the beginning
    totals_row = calculate_totals(data)
    data.insert(0, totals_row)

    return columns, data

def fetch_data(filters):
    sql_query = f"""
        SELECT
            ss.employee AS employee,
            e.employee_pin AS employee_pin,
            e.employee_name AS employee_name,
            SUM(CASE WHEN sd.parentfield = 'deductions' THEN sd.amount ELSE 0 END) AS deductions,
            SUM(CASE WHEN sd.parentfield = 'earnings' THEN sd.amount ELSE 0 END) AS earnings
        FROM
            `tabSalary Slip` ss
        LEFT JOIN
            `tabSalary Detail` sd ON ss.name = sd.parent
        LEFT JOIN
            `tabEmployee` e ON ss.employee = e.name
        WHERE
            ss.start_date BETWEEN '{filters.get('year')}-01-01' AND '{filters.get('year')}-12-31'
            AND (ss.end_date IS NULL OR ss.end_date BETWEEN '{filters.get('year')}-01-01' AND '{filters.get('year')}-12-31')
    """

    if filters.get("employee"):
        sql_query += f" AND ss.employee = '{filters.get('employee')}'"

    sql_query += """
        GROUP BY
            ss.employee
    """

    data = frappe.db.sql(sql_query, as_dict=True)

    return data

def calculate_totals(data):
    totals = {
        "employee": "",
        "employee_pin": "",
        "employee_name": "Total B/F from prev List",
        "deductions": sum(item["deductions"] for item in data),
        "earnings": sum(item["earnings"] for item in data),
    }
    return totals
