# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = []
    conditions = get_conditions(filters)
    operation_details = get_operation_details(conditions)
    # frappe.msgprint(str(operation_details))
    for od in operation_details:
        row = {}
        row["bom"] = od.get("bom_no")
        row["item"] = od.get("production_item")
        row["item_name"] = od.get("item_name")
        alternate_item = get_alternative_item_details(od.get("production_item"))
        if alternate_item:
            if len(alternate_item) == 1:
                row["alternate_item"] = alternate_item[0].get("alternative_item_code")
                row["alternate_item_name"] = alternate_item[0].get(
                    "alternative_item_name"
                )
            else:
                for ai in alternate_item:
                    row = {}
                    row["bom"] = od.get("bom_no")
                    row["item"] = od.get("production_item")
                    row["item_name"] = od.get("item_name")
                    row["alternate_item"] = ai.get("alternative_item_code")
                    row["alternate_item_name"] = ai.get("alternative_item_name")
                    data.append(row)
        else:
            row["alternate_item"] = ""
            row["alternate_item_name"] = ""
        # row["total_completed_qty"] = od.get("tcq")
        data.append(row)
    return columns, data


# def get_operation_details():
#     details = frappe.db.sql(  # SUM(woo.completed_qty) as tcq
#         """SELECT wo.bom_no, wo.production_item, ia.item_name, ia.alternative_item_name, ia.alternative_item_code
#         FROM `tabWork Order` wo inner join `tabItem Alternative` ia on wo.production_item = ia.item_code
#         WHERE wo.allow_alternative_item=1 group by wo.bom_no""",
#         as_dict=1,
#         # debug=True,
#     )
#     return details


def get_operation_details(conditions):
    details = frappe.db.sql(  # SUM(woo.completed_qty) as tcq
        f"""SELECT bom_no, production_item, item_name 
        FROM `tabWork Order` WHERE allow_alternative_item=1 {conditions} """,
        as_dict=1,
        debug=True,
    )
    return details


def get_alternative_item_details(item_code):
    details = frappe.db.sql(  # SUM(woo.completed_qty) as tcq
        f"""SELECT alternative_item_name, alternative_item_code
        FROM `tabItem Alternative` 
        where item_code = '{item_code}' """,
        as_dict=1,
        debug=True,
    )
    return details


def get_columns():
    columns = [
        {
            "fieldname": "bom",
            "label": _("BOM"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "item",
            "label": _("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "alternate_item",
            "label": _("Alternate Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "fieldname": "alternate_item_name",
            "label": _("Alternate Item Name"),
            "fieldtype": "Data",
            "width": 200,
        },
        # {
        #     "fieldname": "total_completed_qty",
        #     "label": _("Total Completed Qty"),
        #     "fieldtype": "Float",
        #     "width": 200,
        # },
    ]
    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += f" and DATE(actual_start_date) >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" and DATE(actual_start_date) <= '{filters.get('to_date')}'"
    #     # if filters.get("workstation"):
    #     #     conditions += f" and woo.workstation = '{filters.get('workstation')}'"
    #     # if filters.get("department"):
    #     #     conditions += f" and woo.department = '{filters.get('department')}'"

    return conditions
