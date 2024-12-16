
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import cstr, cint, date_diff, flt, getdate
from impala.stock_balance_report_custom import execute as execute_stock_balance

def stock_balance_report(filters):
    frappe.enqueue(execute_stock_balance, queue="long", timeout=None)

def execute(filters=None):
    if not filters:
        filters = {}
    
    stock_balance_report = execute_stock_balance(filters)
    if filters.get("item_group"):
        item_group_list = frappe.db.get_list("Item Group", filters={"company": filters.get("company"), "name": ['in', filters.get("item_group")]}, pluck = "name")
    else:
        item_group_list = frappe.db.get_list("Item Group", filters = {"company": filters.get("company")}, pluck="name")
    
    if filters.get("warehouse"):
        warehouse_list = frappe.db.get_list("Warehouse", filters={"company": filters.get("company"), "name": ["in", filters.get("warehouse")], "docstatus" : ['<', 2]}, pluck = "name")
    else:
        warehouse_list = frappe.db.get_list("Warehouse", filters={"company": filters.get("company"), "docstatus": ['<', 2]}, pluck="name")
    has_value = False
    
    columns = get_columns(filters, warehouse_list)
    data = []

    for ig in item_group_list:
        total_bal_qty = 0.0
        total_bal_val = 0.0
        ig_bal_qty_key = ig.lower().replace(" ","_").replace("-","_") + "_bal_qty"
        ig_bal_val_key = ig.lower().replace(" ","_").replace("-","_") + "_bal_val"

        row = frappe._dict()
        row.setdefault("item_group", ig)
        row.setdefault(ig_bal_qty_key, 0.0)
        row.setdefault(ig_bal_val_key, 0.0)

        for wh in warehouse_list:            
            wh_bal_qty_key = wh.lower().replace(" ","_").replace("-", "_") + "_bal_qty"
            wh_bal_val_key = wh.lower().replace(" ","_").replace("-", "_") + "_bal_val"

            row.setdefault(wh_bal_qty_key, 0.0)
            row.setdefault(wh_bal_val_key, 0.0)
            
            
            for entry in stock_balance_report[1]:
                if entry.get("item_group") == ig:
                    row[ig_bal_qty_key] += entry.get("bal_qty")
                    row[ig_bal_val_key] += entry.get("bal_val")
                    
                if entry.get("item_group") == ig and entry.get("warehouse") == wh:
                    row[wh_bal_qty_key] += entry.get("bal_qty")
                    row[wh_bal_val_key] += entry.get("bal_val")
                    total_bal_qty += entry.get("bal_qty")
                    total_bal_val += entry.get("bal_val")
        row["tot_bal_qty"] = total_bal_qty
        row["tot_bal_val"] = total_bal_val
        
        if row["tot_bal_qty"] > 0.05 or row["tot_bal_val"] > 0.05:
                has_value = True

        if has_value==True:
            data.append(row)

    return columns, data


def get_columns(filters, warehouse_list):

    columns = [
        {
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": "360",
        },
    ]

    for wh in warehouse_list:
        if filters.get("show_qty"): 
            columns.append(
                {
                    "fieldname": wh.lower().replace(" ","_").replace("-", "_") + "_bal_qty",
                    "label": _(wh+" Balance Qty"),
                    "fieldtype": "Float",
                    "width": "220",
                }
            )

        if filters.get("show_val"):
            columns.append(
                {
                    "fieldname": wh.lower().replace(" ","_").replace("-", "_") + "_bal_val",
                    "label": _(wh+" Balance Value"),
                    "fieldtype": "Float",
                    "width": "220",
                }
            )
        # columns.extend(
        #     [{
        #         "fieldname": wh.lower().replace(" ","_").replace("-", "_") + "_bal_qty",
        #         "label": _(wh+" Balance Qty"),
        #         "fieldtype": "Float",
        #         "width": "220",
        #     },
        #     {
        #         "fieldname": wh.lower().replace(" ","_").replace("-", "_") + "_bal_val",
        #         "label": _(wh+" Balance Value"),
        #         "fieldtype": "Float",
        #         "width": "220",
        #     }]
        #     )
    if filters.get("show_qty"):
        columns.append(
                {
                    "fieldname": "tot_bal_qty",
                    "label": _("Total Qty"),
                    "fieldtype": "Float",
                    "width": 120,
                }
            )

    if filters.get("show_val"):
        columns.append(
                {
                    "fieldname": "tot_bal_val",
                    "label": _("Total Val"),
                    "fieldtype": "Float",
                    "width": 120,
                }
            )
    return columns
