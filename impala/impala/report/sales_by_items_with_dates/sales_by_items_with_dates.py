# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, today, getdate, add_days
import datetime
import calendar


def execute(filters=None):
    data = []
    days_difference = get_diff_days(*filters.get("date_range"))
    diff_days_dates = get_diff_days_dates(*filters.get("date_range"), days_difference)
    columns = get_columns(filters, days_difference, diff_days_dates)
    conditions = get_conditions(filters)
    daily_sales = ""
    master = get_details(conditions)

    # frappe.msgprint(str(daily_sales))
    for d in master:
        row = {}
        row["item"] = d.get("item_name")
        for i in diff_days_dates:
            daily_sales = get_daily_sales(i, d.get("item_code"), conditions)
            if daily_sales:
                row[f"{i}_sales"] = daily_sales[0].get("sales")
            else:
                row[f"{i}_sales"] = 0
        data.append(row)

    return columns, data


def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += f""" and si.company = '{filters.get("company")}'"""
    if filters.get("item"):
        conditions += f""" and sii.item_code = '{filters.get("item")}'"""
    # if filters.get("date_range"):
    #     conditions += f""" and si.posting_date >= '{filters.get("date_range")[0]}' """
    # if filters.get("date_range"):
    #     conditions += f""" and si.posting_date <= '{filters.get("date_range")[1]}'"""
    if filters.get("date_range"):
        conditions += f""" and si.posting_date BETWEEN '{filters.get("date_range")[0]}' AND '{filters.get("date_range")[1]}' """

    return conditions


def get_details(conditions):
    details = frappe.db.sql(
        f"""SELECT SUM(sii.base_net_amount) as sales, sii.item_code, sii.item_name 
		FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.name = sii.parent
		WHERE si.docstatus=1 {conditions} GROUP BY sii.item_code ORDER BY sii.item_code""",
        as_dict=1,
        debug=True,
    )
    return details


def get_daily_sales(date, item, conditions):
    sales = frappe.db.sql(
        f"""SELECT SUM(sii.base_net_amount) as sales, sii.item_code, sii.item_name 
		FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.name = sii.parent
		WHERE si.docstatus=1 and item_code = '{item}' and si.posting_date= '{date}' GROUP BY sii.item_code ORDER BY sii.item_code""",
        as_dict=1,
        debug=True,
    )

    return sales


def get_columns(filters, days_difference, diff_days_dates):

    columns = [
        {
            "fieldname": "item",
            "label": _("Item"),
            "fieldtype": "Data",
            "width": 300,
        },
    ]
    for i in diff_days_dates:
        columns.append(
            {
                "fieldname": f"{i}_sales",
                "label": (f"{calendar.day_name[getdate(i).weekday()]} Sales"),
                "fieldtype": "Currency",
                "width": 150,
            }
        )

    return columns


def get_diff_days(from_date, to_date):
    if from_date and to_date:
        if from_date != to_date:
            diff_days = getdate(to_date) - getdate(from_date)
            days = f"{diff_days}".split()
            number_of_days = int(days[0])
            return number_of_days
        else:
            return 0
    else:
        return "None"


def get_diff_days_dates(from_date, to_date, days_difference):
    get_diff_days_DAtes = []
    if from_date and to_date:
        if from_date != to_date:
            for i in range(days_difference):
                get_diff_days_DAtes.append(add_days(from_date, i))
            get_diff_days_DAtes.append(to_date)
            return get_diff_days_DAtes
        else:
            return [from_date]
    else:
        return "None"
