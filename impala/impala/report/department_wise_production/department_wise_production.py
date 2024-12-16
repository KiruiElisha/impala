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
        row["workstation"] = od.get("workstation")
        # row["department"] = od.get("department", "")
        row["total_completed_qty"] = od.get("tcq")
        data.append(row)
    return columns, data


def get_operation_details(conditions):
    details = frappe.db.sql(
        f"""SELECT woo.workstation, SUM(woo.completed_qty) as tcq 
        FROM `tabWork Order` wo inner join `tabWork Order Operation` woo on woo.parent = wo.name
        WHERE wo.status='Completed' {conditions} group by woo.workstation""",
        as_dict=1,
        # debug=True,
    )
    return details


def get_columns():
    columns = [
        {
            "fieldname": "workstation",
            "label": _("Workstation"),
            "fieldtype": "Data",
            "width": 200,
        },
        # {
        #     "fieldname": "department",
        #     "label": _("Department"),
        #     "fieldtype": "Data",
        #     "width": 200,
        # },
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
        conditions += (
            f" and DATE(woo.actual_start_time) >= '{filters.get('from_date')}'"
        )
    if filters.get("to_date"):
        conditions += f" and DATE(woo.actual_start_time) <= '{filters.get('to_date')}'"
    if filters.get("workstation"):
        conditions += f" and woo.workstation = '{filters.get('workstation')}'"
    # if filters.get("department"):
    #     conditions += f" and woo.department = '{filters.get('department')}'"

    return conditions
