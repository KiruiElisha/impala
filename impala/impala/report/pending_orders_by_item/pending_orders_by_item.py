# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 200},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "pending_qty", "label": "Pending Quantity", "fieldtype": "Float", "width": 200},
    ]

    # Define additional filters based on user input
    filter_dict = {}
    
    if filters.get("cost_center"):
        filter_dict["cost_center"] = filters.get("cost_center")

    # Define the SQL query as a single string with conditional parts
    sql_query = """
        SELECT
            `tabItem`.item_code,
            `tabItem`.item_name,
            SUM(`tabSales Order Item`.qty - `tabSales Order Item`.delivered_qty) AS pending_qty
        FROM
            `tabSales Order`
        INNER JOIN
            `tabSales Order Item` ON `tabSales Order`.name = `tabSales Order Item`.parent
        INNER JOIN
            `tabItem` ON `tabItem`.name = `tabSales Order Item`.item_code
        WHERE
            `tabSales Order`.docstatus = 1
            AND `tabSales Order`.status != 'Closed'
    """

    # Add cost_center filter if provided
    if "cost_center" in filter_dict:
        sql_query += " AND `tabSales Order`.cost_center = %(cost_center)s"

    sql_query += """
        GROUP BY
            `tabItem`.item_code
        HAVING
            pending_qty > 0
        ORDER BY pending_qty DESC
    """

    # Fetch data from the database using the constructed query and filters
    result = frappe.db.sql(sql_query, filter_dict, as_dict=True)

    data = []
    for row in result:
        data.append({
            "item_code": row.item_code,
            "item_name": row.item_name,
            "pending_qty": row.pending_qty,
        })

    return columns, data
