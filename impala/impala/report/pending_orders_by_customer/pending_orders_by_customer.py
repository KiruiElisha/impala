# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    # Define columns for the report
    columns = [
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "pending_qty", "label": "Pending Quantity", "fieldtype": "Float", "width": 200},
    ]

    # Define the SQL query as a single string with conditional parts
    sql_query = """
        SELECT
            `tabSales Order`.customer,
            `tabCustomer`.customer_name,
            SUM(`tabSales Order Item`.qty - `tabSales Order Item`.delivered_qty) AS pending_qty
        FROM
            `tabSales Order Item`
        INNER JOIN
            `tabSales Order` ON `tabSales Order`.name = `tabSales Order Item`.parent
        INNER JOIN
            `tabCustomer` ON `tabCustomer`.name = `tabSales Order`.customer
        WHERE
            `tabSales Order`.docstatus = 1
            AND `tabSales Order`.status != 'Closed'
            AND `tabSales Order`.transaction_date BETWEEN %s AND %s
    """

    # Define the initial parameters for the SQL query
    sql_params = [filters.from_date, filters.to_date]

    # Conditionally add cost_center filter to the SQL query
    if filters.cost_center:
        sql_query += " AND `tabSales Order`.cost_center = %s"
        sql_params.append(filters.cost_center)

    # Complete the SQL query with GROUP BY and ORDER BY clauses
    sql_query += " GROUP BY `tabSales Order`.customer ORDER BY pending_qty DESC"

    # Execute the SQL query
    result = frappe.db.sql(sql_query, sql_params, as_dict=True)

    # Prepare data for the report
    data = []
    for row in result:
        data.append({
            "customer": row.customer,
            "customer_name": row.customer_name,
            "pending_qty": row.pending_qty,
        })

    return columns, data
