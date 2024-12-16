# Copyright (c) 2023, Aquiq and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from datetime import datetime, timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    tree_data = build_tree(data)
    return columns, tree_data

def get_data(filters):
    cost_center_filter = filters.get("cost_center")
    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d") if filters.get("from_date") else None
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d") if filters.get("to_date") else None
    sales_data = get_sales_data(cost_center_filter, from_date, to_date)

    # Initialize data for DataFrame
    data = []
    for row in sales_data:
        data.append({
            "cost_center": row["cost_center"],
            "item_code": row["item_code"],
            "daily_sales": row["grand_total"] / ((to_date - from_date).days + 1),
            "weekly_sales": row["grand_total"] / ((to_date - from_date).days + 1) * 7,
            "monthly_sales": row["grand_total"] / ((to_date - from_date).days + 1) * 30,
            "yearly_sales": row["grand_total"] / ((to_date - from_date).days + 1) * 365
        })

    return data

def build_tree(data):
    tree_data = []
    current_parent = None
    grand_total_sum = 0
    daily_sales_sum = 0
    weekly_sales_sum = 0
    monthly_sales_sum = 0
    yearly_sales_sum = 0

    for row in data:
        cost_center = row['cost_center']
        item_code = row['item_code']
        daily_sales = row['daily_sales']
        weekly_sales = row['weekly_sales']
        monthly_sales = row['monthly_sales']
        yearly_sales = row['yearly_sales']

        if cost_center != current_parent:
            if current_parent is not None:
                tree_data.append({
                    "cost_center": current_parent,
                    "item_code": "<b>Total</b>",
                    "daily_sales": daily_sales_sum,
                    "weekly_sales": weekly_sales_sum,
                    "monthly_sales": monthly_sales_sum,
                    "yearly_sales": yearly_sales_sum
                })
                grand_total_sum += daily_sales_sum
                daily_sales_sum = 0
                weekly_sales_sum = 0
                monthly_sales_sum = 0
                yearly_sales_sum = 0

            current_parent = cost_center
            tree_data.append({
                "cost_center": "<b>{}</b>".format(cost_center),
                "item_code": "",
                "daily_sales": "",
                "weekly_sales": "",
                "monthly_sales": "",
                "yearly_sales": ""
            })

        tree_data.append({
            "cost_center": "",
            "item_code": "<b>{}</b>".format(frappe.db.get_value("Item", item_code, 'item_name')),
            "daily_sales": daily_sales,
            "weekly_sales": weekly_sales,
            "monthly_sales": monthly_sales,
            "yearly_sales": yearly_sales
        })

        grand_total_sum += daily_sales
        daily_sales_sum += daily_sales
        weekly_sales_sum += weekly_sales
        monthly_sales_sum += monthly_sales
        yearly_sales_sum += yearly_sales

    if current_parent is not None:
        tree_data.append({
            "cost_center": current_parent,
            "item_code": "<b>Total</b>",
            "daily_sales": daily_sales_sum,
            "weekly_sales": weekly_sales_sum,
            "monthly_sales": monthly_sales_sum,
            "yearly_sales": yearly_sales_sum
        })
        grand_total_sum += daily_sales_sum

    tree_data.append({
        "cost_center": "",
        "item_code": "<b>Grand Total</b>",
        "daily_sales": grand_total_sum,
        "weekly_sales": grand_total_sum * 7,
        "monthly_sales": grand_total_sum * 30,
        "yearly_sales": grand_total_sum * 365
    })

    return tree_data

def get_sales_data(cost_center_filter=None, from_date=None, to_date=None):
    sql_query = f"""
        SELECT
            si.cost_center,
            sii.item_code,
            SUM(si.grand_total) as grand_total
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii
        ON
            si.name = sii.parent
        WHERE
            si.docstatus = 1
            AND (si.posting_date >= '{from_date}' AND si.posting_date <= '{to_date}')
    """

    if cost_center_filter:
        sql_query += f" AND si.cost_center = '{cost_center_filter}'"

    sql_query += " GROUP BY si.cost_center, sii.item_code"

    sales_data = frappe.db.sql(sql_query, as_dict=True)
    return sales_data

def get_columns():
    return [
        {"fieldname": "cost_center", "label": "<b>Cost Center</b>", "fieldtype": "Link", "options": "Cost Center", "width": 170, "align": "left"},
        {"fieldname": "item_code", "label": "<b>Item Name</b>", "fieldtype": "Data", "options": "Item", "width": 300, "align": "left"},
        {"fieldname": "daily_sales", "label": "<b>Daily Sales</b>", "fieldtype": "Currency", "options": "", "width": 150, "align": "left", "precision": 2},
        {"fieldname": "weekly_sales", "label": "<b>Weekly Sales</b>", "fieldtype": "Currency", "options": "", "width": 150, "align": "left", "precision": 2},
        {"fieldname": "monthly_sales", "label": "<b>Monthly Sales</b>", "fieldtype": "Currency", "options": "", "width": 140, "align": "left", "precision": 2},
        {"fieldname": "yearly_sales", "label": "<b>Yearly Sales</b>", "fieldtype": "Currency", "options": "", "width": 150, "align": "left", "precision": 2}
    ]
