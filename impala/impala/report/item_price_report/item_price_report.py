# Copyright (c) 2024, Codes Soft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = frappe._dict(filters or {})

    # Define columns for the report
    columns = [
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Valid From", "fieldname": "valid_from", "fieldtype": "Date", "width": 120},
        {"label": "Price List", "fieldname": "price_list", "fieldtype": "Link", "options": "Price List", "width": 150},
        {"label": "Rate", "fieldname": "price_list_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 100},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
        {"label": "Item Category", "fieldname": "item_category", "fieldtype": "Data", "width": 150},
    ]

    # Build SQL query with filters
    conditions = []
    if filters.get("item_code"):
        conditions.append("ip.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
    if filters.get("price_list"):
        conditions.append("ip.price_list = %(price_list)s")
    if filters.get("item_category"):
        conditions.append("i.item_category = %(item_category)s")
    
    conditions = " AND ".join(conditions)
    if conditions:
        conditions = "WHERE " + conditions

    # If the "show_all_prices" checkbox is checked (value = 1), show all prices
    if filters.get("show_all_prices") == 1:
        data = frappe.db.sql(f"""
            SELECT
                ip.item_name,
                ip.valid_from,
                ip.price_list,
                ip.price_list_rate,
                ip.currency,
                ip.item_code,
                i.item_group,
                i.item_category
            FROM
                `tabItem Price` ip
            LEFT JOIN
                `tabItem` i ON ip.item_code = i.item_code
            {conditions}
            ORDER BY
                ip.item_name, ip.valid_from DESC
        """, filters, as_dict=True)
    else:  # Show only the latest price for each item when the checkbox is unchecked (value = 0)
        data = frappe.db.sql(f"""
            SELECT
                ip.item_name,
                ip.valid_from,
                ip.price_list,
                ip.price_list_rate,
                ip.currency,
                ip.item_code,
                i.item_group,
                i.item_category
            FROM
                `tabItem Price` ip
            LEFT JOIN
                `tabItem` i ON ip.item_code = i.item_code
            INNER JOIN (
                SELECT 
                    item_code, MAX(valid_from) as latest_date 
                FROM 
                    `tabItem Price` 
                GROUP BY 
                    item_code
            ) as latest_prices ON ip.item_code = latest_prices.item_code AND ip.valid_from = latest_prices.latest_date
            {conditions}
            ORDER BY
                ip.item_name
        """, filters, as_dict=True)

    return columns, data



