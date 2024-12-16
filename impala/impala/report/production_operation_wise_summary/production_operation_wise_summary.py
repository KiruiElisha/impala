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
    for od in operation_details:
        row = {}
        row["operation"] = od.get("operation")
        row["total_completed_qty"] = od.get("tcq")
        data.append(row)
    return columns, data


def get_operation_details(conditions):
    details = frappe.db.sql(
        f"""SELECT operation, SUM(total_completed_qty) as tcq 
        FROM `tabJob Card` WHERE status='Completed' {conditions} group by operation""",
        as_dict=1,
        debug=False,
    )
    return details


def get_columns():
    columns = [
        {
            "fieldname": "operation",
            "label": _("Operation"),
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "total_completed_qty",
            "label": _("Total Completed Qty"),
            "fieldtype": "Float",
            "width": 200,
        },
    ]
    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += f" and posting_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" and posting_date <= '{filters.get('to_date')}'"

    if not(filters.get("from_date") and filters.get("to_date")):
        conditions += f" and posting_date = '{frappe.utils.today()}'"        
    if filters.get("workstation"):
        conditions += f" and workstation = '{filters.get('workstation')}'"

    return conditions
