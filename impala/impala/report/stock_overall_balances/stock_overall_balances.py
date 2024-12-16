
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import cstr, cint, date_diff, flt, getdate
from impala.stock_balance_report_custom import execute as execute_stock_balance

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    data = []

    stock_balance_report = execute_stock_balance(filters)
    group_field = None
    doctype = None
    group_by_list = []

    if filters.get("group_by") == "Item Group":
        group_field = "item_group"
        doctype = "Item Group"
        group_by_list = frappe.db.get_list(doctype, pluck = "name")

    if filters.get("group_by") == "Warehouse":
        group_field = "warehouse"
        doctype = "Warehouse"
        group_by_list = frappe.db.get_list(doctype, filters={"docstatus" : ['<', 2]}, pluck = "name")

    total_bal_qty = 0.0
    total_bal_val = 0.0
    has_value = False
    for group in group_by_list:
        group_dict = frappe._dict()
        group_dict.setdefault(filters.get("group_by").lower().replace(" ","_").replace("-", "_"), group)
        group_dict.setdefault("bal_qty", 0.0)
        group_dict.setdefault("bal_val", 0.0)

        for entry in stock_balance_report[1]:
            if entry.get(group_field) == group:
                group_dict["bal_qty"] += entry.get("bal_qty")
                group_dict["bal_val"] += entry.get("bal_val")
                total_bal_qty += entry.get("bal_qty")
                total_bal_val += entry.get("bal_val")

        if group_dict["bal_qty"] > 0.05 or group_dict["bal_val"] > 0.05:
            has_value = True
            data.append(group_dict)


    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": filters.get("group_by").lower().replace(" ","_").replace("-", "_"),
            "label": _(filters.get("group_by")),
            "fieldtype": "Link",
            "options": filters.get("group_by"),
            "width": "360",
        },
        {
            "fieldname": "bal_qty",
            "label": _("Balance Qty"),
            "fieldtype": "Float",
            "width": "220",
        },
        {
            "fieldname": "bal_val",
            "label": _("Balance Value"),
            "fieldtype": "Float",
            "width": "220",
        },
    ]
    
    return columns
