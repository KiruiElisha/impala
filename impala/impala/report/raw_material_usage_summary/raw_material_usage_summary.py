# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import calendar
import datetime


def execute(filters=None):
    columns = get_columns(filters)
    data = []
    conditions = get_conditions(filters)
    operation_details = get_operation_details(conditions, filters.get("year"))
    for od in operation_details:
        b = 1
        row = {}
        row["item_code"] = od.get("item_code")
        row["item_name"] = od.get("item_name")
        if filters.get("month"):
            monthly_operation_details = get_monthly_operation_details(
                od.get("item_code"), filters.get("month"), filters.get("year")
            )
            if monthly_operation_details:
                # frappe.msgprint(str(monthly_operation_details))
                row[filters.get("month") + "_bom_qty"] = monthly_operation_details[
                    0
                ].get("req_qty")
                row[filters.get("month") + "_actual_qty"] = monthly_operation_details[
                    0
                ].get("con_qty")
            else:
                row[filters.get("month") + "_bom_qty"] = 0
                row[filters.get("month") + "_actual_qty"] = 0
        else:
            for i in range(12):
                monthly_operation_details = get_monthly_operation_details(
                    od.get("item_code"), calendar.month_name[b], filters.get("year")
                )
                if monthly_operation_details:
                    # frappe.msgprint(str(monthly_operation_details))
                    row[
                        calendar.month_name[b] + "_bom_qty"
                    ] = monthly_operation_details[0].get("req_qty")
                    row[
                        calendar.month_name[b] + "_actual_qty"
                    ] = monthly_operation_details[0].get("con_qty")
                else:
                    row[calendar.month_name[b] + "_bom_qty"] = 0
                    row[calendar.month_name[b] + "_actual_qty"] = 0
                b = b + 1
                if b == 13:
                    b = b - 12
        data.append(row)
    return columns, data


def get_operation_details(conditions, year):
    details = frappe.db.sql(
        f"""SELECT woi.item_code,woi.item_name 
        FROM `tabWork Order` wo inner join `tabWork Order Item` woi on woi.parent = wo.name
        WHERE wo.status='Completed' {conditions} and YEAR(DATE(wo.actual_start_date)) = '{year}' group by woi.item_code""",
        as_dict=1,
        # debug=True,
    )
    return details


def get_monthly_operation_details(item_code, month_name, year):
    details = frappe.db.sql(
        f"""SELECT woi.item_code,woi.item_name, SUM(woi.required_qty) as req_qty, SUM(woi.consumed_qty) as con_qty 
        FROM `tabWork Order` wo inner join `tabWork Order Item` woi on woi.parent = wo.name
        WHERE wo.status='Completed' and woi.item_code = '{item_code}' and MONTHNAME(DATE(wo.actual_start_date)) = '{month_name}' and YEAR(DATE(wo.actual_start_date)) = '{year}' group by woi.item_code """,
        as_dict=1,
        # debug=True,
    )
    return details


def get_columns(filters):
    columns = [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 140,
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 250,
        },
    ]
    if filters.get("month"):
        columns.append(
            {
                "fieldname": filters.get("month") + "_bom_qty",
                "label": _(filters.get("month") + " BOM Qty"),
                "fieldtype": "Float",
                "width": 140,
            }
        )
        columns.append(
            {
                "fieldname": filters.get("month") + "_actual_qty",
                "label": _(filters.get("month") + " Actual Qty"),
                "fieldtype": "Float",
                "width": 140,
            }
        )
    else:
        b = 1
        for i in range(12):
            columns.append(
                {
                    "fieldname": calendar.month_name[b] + "_bom_qty",
                    "label": _(calendar.month_name[b] + " BOM Qty"),
                    "fieldtype": "Float",
                    "width": 140,
                }
            )
            columns.append(
                {
                    "fieldname": calendar.month_name[b] + "_actual_qty",
                    "label": _(calendar.month_name[b] + " Actual Qty"),
                    "fieldtype": "Float",
                    "width": 140,
                }
            )
            b = b + 1
            if b == 13:
                b = b - 12
    return columns


def get_conditions(filters):
    conditions = ""
    # if filters.get("from_date"):
    #     conditions += f" and DATE(wo.actual_start_date) >= '{filters.get('from_date')}'"
    # if filters.get("to_date"):
    #     conditions += f" and DATE(wo.actual_start_date) <= '{filters.get('to_date')}'"
    if filters.get("item_code"):
        conditions += f" and woi.item_code = '{filters.get('item_code')}'"
    # if filters.get("workstation"):
    #     conditions += f" and woi.workstation = '{filters.get('workstation')}'"
    # if filters.get("department"):
    #     conditions += f" and woi.department = '{filters.get('department')}'"

    return conditions
