# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import cstr, cint, date_diff, flt, getdate
from six import iteritems


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    query_data = get_stock_ledger_entries(filters, conditions)
    data = []
    if filters.get("group_by") == "Warehouse":
        for row in query_data:
            data_row = {}
            data_row["item_code"] = row.get("item_code")
            data_row["item_name"] = row.get("item_name")
            data_row["warehouse"] = row.get("warehouse")
            data_row["stock_value"] = row.get("stock_value")
            data_row["actual_qty"] = row.get("actual_qty")
            data.append(data_row)
    elif filters.get("group_by") == "Item Group":
        for row in query_data:
            data_row = {}
            # data_row["item_group"] = row.get("item_group")
            data_row["item_group"] = row.get("item_group")
            data_row["warehouse"] = row.get("warehouse")
            data_row["stock_value"] = row.get("stock_value")
            data_row["actual_qty"] = row.get("actual_qty")
            data.append(data_row)

    return columns, data


def get_columns(filters):
    columns = []
    if filters.get("group_by") == "Warehouse":
        columns.append(
            {
                "label": _("Item"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 150,
            }
        )
        columns.append(
            {
                "label": _("Item Name"),
                "fieldname": "item_name",
                "width": 200,
                "fieldtype": "data",
            }
        )
    elif filters.get("group_by") == "Item Group":
        columns.append(
            {
                "label": _("Item Group"),
                "fieldname": "item_group",
                "fieldtype": "Link",
                "options": "Item Group",
                "width": 200,
            }
        )

    columns_main = [
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 160,
        },
        {
            "label": _("Stock Value"),
            "fieldname": "stock_value",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Actual Qty"),
            "fieldname": "actual_qty",
            "fieldtype": "Float",
            "width": 120,
        },
    ]

    columns.extend(columns_main)
    return columns


def get_conditions(filters):
    conditions = ""

    if filters.get("warehouse"):
        conditions += " and sle.warehouse = '{}' ".format(filters.get("warehouse"))
    if filters.get("item_group"):
        conditions += " and i.item_group = '{}' ".format(filters.get("item_group"))
    if filters.get("item_code"):
        conditions += " and sle.item_code = '{}' ".format(filters.get("item_code"))
    if filters.get("group_by") == "Item Group":
        conditions += " Group by i.item_group"
    if filters.get("group_by") == "Warehouse":
        conditions += " Group by sle.warehouse"

    return conditions


def get_stock_ledger_entries(filters, conditions):
    data = []
    if filters.get("group_by") == "Item Group":
        data = frappe.db.sql(
            """Select 
            sle.warehouse,i.item_group, sle.stock_value, sle.actual_qty 
            from `tabStock Ledger Entry` sle inner join `tabItem` i on sle.item_code = i.name 
            where sle.docstatus = 1 {} """.format(
                conditions
            ),
            as_dict=True,
            debug=True,
        )
    elif filters.get("group_by") == "Warehouse":
        data = frappe.db.sql(
            """Select 
            sle.item_code, sle.warehouse,i.item_name, sle.stock_value, sle.actual_qty 
            from `tabStock Ledger Entry` sle inner join `tabItem` i on sle.item_code = i.name 
            where sle.docstatus = 1 {} """.format(
                conditions
            ),
            as_dict=True,
            debug=True,
        )

    return data
