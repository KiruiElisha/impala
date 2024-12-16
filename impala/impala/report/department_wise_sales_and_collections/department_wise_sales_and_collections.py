# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, today
import datetime


def execute(filters=None):
    select_group = ""
    groupby = ""
    group_doctype = "Department"
    select_details = "name as details"
    if filters.get("groupby") == "Department":
        select_group = "department as details"
        groupby = "GROUP BY department ORDER BY department"
        group_doctype = "Department"

    if filters.get("groupby") == "Division":
        select_group = "cost_center as details"
        groupby = "GROUP BY cost_center ORDER BY cost_center"
        group_doctype = "Cost Center"
    data = []
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    daily_sales = get_daily_sales(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales(select_group, conditions, groupby)
    daily_collections = get_daily_collections(select_group, conditions, groupby)
    weekly_collections = get_weekly_collections(select_group, conditions, groupby)
    monthly_collections = get_monthly_collections(select_group, conditions, groupby)
    master = get_details(select_details, group_doctype, filters)
    for d in master:
        row = {}
        row["details"] = d.get("details")
        if daily_sales:
            for ds in daily_sales:
                if ds.get("details") == d.get("details"):
                    row["daily_sales"] = ds.get("sales")
                    break
                else:
                    row["daily_sales"] = 0.0
        else:
            row["daily_sales"] = 0.0

        if weekly_sales:
            for ws in weekly_sales:
                if ws.get("details") == d.get("details"):
                    row["weekly_sales"] = ws.get("sales")
                    break
                else:
                    row["weekly_sales"] = 0.0
        else:
            row["weekly_sales"] = 0.0

        if monthly_sales:
            for ms in monthly_sales:
                if ms.get("details") == d.get("details"):
                    row["monthly_sales"] = ms.get("sales")
                    break
                else:
                    row["monthly_sales"] = 0.0
        else:
            row["monthly_sales"] = 0.0

        if daily_collections:
            for dc in daily_collections:
                if dc.get("details") == d.get("details"):
                    row["daily_collections"] = dc.get("collection")
                    break
                else:
                    row["daily_collections"] = 0.0
        else:
            row["daily_collections"] = 0.0

        if weekly_collections:
            for wc in weekly_collections:
                if wc.get("details") == d.get("details"):
                    row["weekly_collections"] = wc.get("collection")
                    break
                else:
                    row["weekly_collections"] = 0.0
        else:
            row["weekly_collections"] = 0.0

        if monthly_collections:
            for mc in monthly_collections:
                if mc.get("details") == d.get("details"):
                    row["monthly_collections"] = mc.get("collection")
                    break
                else:
                    row["monthly_collections"] = 0.0
        else:
            row["monthly_collections"] = 0.0

        data.append(row)
    data = sorted(
        data,
        key=lambda i: (
            i.get("daily_sales"),
            i.get("daily_collections"),
            i.get("weekly_sales"),
            i.get("weekly_collections"),
            i.get("monthly_sales"),
            i.get("monthly_collections"),
        ),
        reverse=True,
    )

    return columns, data


def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and company = '{}'".format(filters.get("company"))
    if filters.get("from_date"):
        conditions += " and posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details(select_details, group_doctype, filters):
    details = frappe.db.sql(
        """SELECT {} FROM `tab{}`
			WHERE disabled=0 and company='{}'""".format(
            select_details, group_doctype, filters.get("company")
        ),
        as_dict=1,
        debug=True,
    )

    return details


def get_daily_sales(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and posting_date= '{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections(select_group, conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and payment_type='Receive'  and posting_date='{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and payment_type='Receive'  and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and payment_type='Receive'  and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_columns(filters):
    dept_div_label = ""
    if filters.get("groupby") == "Department":
        dept_div_label = "Department"
    if filters.get("groupby") == "Division":
        dept_div_label = "Division"

    columns = [
        {
            "fieldname": "details",
            "label": _(dept_div_label),
            "fieldtype": "Data",
            "width": 260,
        },
        {
            "fieldname": "daily_sales",
            "label": _("Daily Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "daily_collections",
            "label": _("Daily Collection"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "weekly_sales",
            "label": _("Weekly Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "weekly_collections",
            "label": _("Weekly Collection"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "monthly_sales",
            "label": _("Monthly Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "monthly_collections",
            "label": _("Monthly Collection"),
            "fieldtype": "Currency",
            "width": 150,
        },
    ]

    return columns
