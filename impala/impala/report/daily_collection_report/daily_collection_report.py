# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import calendar


def execute(filters=None):
    data = []
    conditions = get_conditions(filters)
    group_tasks = get_group_task_details(filters, conditions)
    all_mode_of_payments = get_all_mode_of_payments(conditions)
    columns = get_columns(conditions, all_mode_of_payments)
    for gt in group_tasks:
        total = 0
        row = {}
        row["account"] = gt.get("name")
        mode_of_payments_child_table_data = get_all_mode_of_payments_child_table_data(
            gt.get("name"), conditions
        )
        for mod in all_mode_of_payments:
            if mode_of_payments_child_table_data:
                for cdt in mode_of_payments_child_table_data:
                    if cdt.get("mode_of_payment") == mod.get("name"):
                        row[mod.get("name").lower()] = cdt.get("base_amount")
                        break
                    else:
                        row[mod.get("name").lower()] = total
            else:
                row[mod.get("name").lower()] = total
        # frappe.msgprint(str(mode_of_payments_child_table_data))

        data.append(row)
    return columns, data


def get_group_task_details(filters, conditions):
    details = frappe.db.sql(
        f"""SELECT a.name 
        FROM `tabSales Invoice Payment` sip 
        Inner JOIN `tabSales Invoice` si on sip.parent = si.name 
        Inner JOIN  `tabAccount` a on sip.account = a.name 
        WHERE sip.parenttype = 'Sales Invoice' and a.account_type in ("Bank", "Cash", "Receivable") and a.is_group=0 and a.company = '{filters.get("company")}' {conditions}
        group by a.name """,
        as_dict=1,
        debug=False,
    )
    return details


def get_all_mode_of_payments(conditions):
    all_mode_of_payments = frappe.db.sql(
        f"""SELECT sip.mode_of_payment as name   
        FROM `tabSales Invoice Payment` sip Inner JOIN `tabSales Invoice` si on sip.parent = si.name 
        WHERE sip.parenttype = 'Sales Invoice' {conditions}
        group by sip.account """,
        as_dict=1,
        debug=False,
    )
    return all_mode_of_payments


def get_all_mode_of_payments_child_table_data(name, conditions):
    all_mode_of_payments = frappe.db.sql(
        f"""SELECT sip.mode_of_payment, SUM(sip.base_amount) as base_amount  
        FROM `tabSales Invoice Payment` sip Inner JOIN `tabSales Invoice` si on sip.parent = si.name 
        WHERE sip.parenttype = 'Sales Invoice' and sip.account = '{name}' {conditions}
        group by sip.account """,
        as_dict=1,
        debug=False,
    )
    return all_mode_of_payments


def get_columns(conditions, all_mode_of_payments):
    columns = [
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 200,
        },
    ]
    for mod in all_mode_of_payments:
        columns.append(
            {
                "fieldname": mod.get("name").lower(),
                "label": _(mod.get("name")),
                "fieldtype": "Currency",
                "width": 150,
                "default": 0,
            }
        )

    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += f" and si.posting_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" and si.posting_date <= '{filters.get('to_date')}'"
    if not(filters.get("from_date") and filters.get("to_date")):
        conditions += f" and si.posting_date = '{frappe.utils.today()}'"
    return conditions
