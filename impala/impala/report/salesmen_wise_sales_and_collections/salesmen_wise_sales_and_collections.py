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
    group_doctype = "Sales Person"
    select_details = "name as details"
    # if filters.get("groupby") == "Department":
    # 	select_group = "department as details"
    # 	groupby = "GROUP BY department ORDER BY department"
    # 	group_doctype = "Department"

    select_group = "st.sales_person as details"
    groupby = "GROUP BY st.sales_person ORDER BY st.sales_person"
    data = []
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    daily_sales = get_daily_sales(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales(select_group, conditions, groupby)
    conditions = get_conditions2(filters)
    daily_collections = get_daily_collections(conditions, groupby)
    weekly_collections = get_weekly_collections(conditions, groupby)
    monthly_collections = get_monthly_collections(conditions, groupby)

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
                    row["daily_sales"] =  "KES " + str(0.0)
        else:
            row["daily_sales"] = "KES " + str(0.0)

        if weekly_sales:
            for ws in weekly_sales:
                if ws.get("details") == d.get("details"):
                    row["weekly_sales"] = ws.get("sales")
                    break
                else:
                    row["weekly_sales"] = "KES " + str(0.0)
        else:
            row["weekly_sales"] = "KES " + str(0.0)

        if monthly_sales:
            for ms in monthly_sales:
                if ms.get("details") == d.get("details"):
                    row["monthly_sales"] = ms.get("sales")
                    break
                else:
                    row["monthly_sales"] = "KES " + str(0.0)
        else:
            row["monthly_sales"] = "KES " + str(0.0)

        if daily_collections:
            for dc in daily_collections:
                if dc.get("details") == d.get("details"):
                    row["daily_collections"] = dc.get("collection")
                    break
                else:
                    row["daily_collections"] = "KES " + str(0.0)
        else:
            row["daily_collections"] = "KES " + str(0.0)

        if weekly_collections:
            for wc in weekly_collections:
                if wc.get("details") == d.get("details"):
                    row["weekly_collections"] = wc.get("collection")
                    break
                else:
                    row["weekly_collections"] = "KES " + str(0.0)
        else:
            row["weekly_collections"] = "KES " + str(0.0)

        if monthly_collections:
            for mc in monthly_collections:
                if mc.get("details") == d.get("details"):
                    row["monthly_collections"] = mc.get("collection")
                    break
                else:
                    row["monthly_collections"] = "KES " + str(0.0)
        else:
            row["monthly_collections"] = "KES " + str(0.0)

        data.append(row)
    data = sorted(
        data,
        key=lambda i: (
            i.get("daily_sales").split(" ")[1],
            i.get("daily_collections").split(" ")[1],
            i.get("weekly_sales").split(" ")[1],
            i.get("weekly_collections").split(" ")[1],
            i.get("monthly_sales").split(" ")[1],
            i.get("monthly_collections").split(" ")[1],
        ),
        reverse=True,
    )
    frappe.log_error(data)
    return columns, data


def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and sl.company = '{}'".format(filters.get("company"))
    # if filters.get("customer_groups"):
    # 	conditions += " and customer_group = '{}'".format(filters.get("customer_groups"))
    if filters.get("from_date"):
        conditions += " and sl.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and sl.posting_date <= '{}'".format(filters.get("to_date"))
    return conditions


def get_conditions2(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and pe.company = '{}'".format(filters.get("company"))
    if filters.get("sales_person"):
        conditions += " and st.name = '{}'".format(filters.get("sales_person"))
    if filters.get("from_date"):
        conditions += " and pe.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and pe.posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details(select_details, group_doctype, filters):
    if filters.get("sales_person"):
        details = frappe.db.sql(
            """SELECT {} FROM `tab{}`
                WHERE name = '{}' """.format(
                select_details, group_doctype, filters.get("sales_person")
            ),
            as_dict=1,
            debug=True,
        )
    else:
        details = frappe.db.sql(
            """SELECT {} FROM `tab{}`
                """.format(
                select_details, group_doctype
            ),
            as_dict=1,
            debug=True,
        )
    return details


def get_daily_sales(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, CONCAT(currency, " ", FORMAT(SUM(sl.grand_total), 2)) as sales, SUM(sl.grand_total) as sales_val
            FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
            WHERE sl.docstatus=1 and sl.posting_date='{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, CONCAT(currency, " ", FORMAT(SUM(sl.grand_total), 2)) as sales, SUM(sl.grand_total) as sales_val
            FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
            WHERE sl.docstatus=1 and WEEK(sl.posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, CONCAT(currency, " ", FORMAT(SUM(sl.grand_total),2)) as sales,  SUM(sl.grand_total) as sales_val
            FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
            WHERE sl.docstatus=1 and MONTHNAME(sl.posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections(conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT sales_person as details, CONCAT(paid_from_account_currency, " ", FORMAT(SUM(pe.paid_amount), 2)) as collection,  SUM(pe.paid_amount) as collection_val
        FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
        inner join `tabSales Invoice` si on  per.reference_name = si.name
          inner join `tabSales Team` st on si.name = st.parent
        WHERE pe.docstatus=1 and pe.payment_type='Receive' and pe.posting_date='{}' {} {}""".format(
            today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections(conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    collections = frappe.db.sql(
        """ SELECT sales_person as details, CONCAT(paid_from_account_currency, " ", FORMAT(SUM(pe.paid_amount), 2)) as collection, SUM(pe.paid_amount) as collection_val
        FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
        inner join `tabSales Invoice` si on  per.reference_name = si.name
          inner join `tabSales Team` st on si.name = st.parent
        WHERE pe.docstatus=1 and pe.payment_type='Receive' and WEEK(pe.posting_date)='{}' {} {}""".format(
            current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections(conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """
                            SELECT sales_person as details, CONCAT(paid_from_account_currency, " ", FORMAT(SUM(pe.paid_amount), 2)) as collection, SUM(pe.paid_amount) as collection_val
        FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
        inner join `tabSales Invoice` si on  per.reference_name = si.name
          inner join `tabSales Team` st on si.name = st.parent
        WHERE pe.docstatus=1 and pe.payment_type='Receive' and MONTHNAME(pe.posting_date)='{}' {} {}""".format(
            current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_columns(filters):

    columns = [
        {
            "fieldname": "details",
            "label": _("Sales Person"),
            "fieldtype": "Data",
            "width": 260,
        },
        {
            "fieldname": "daily_sales",
            "label": _("Daily Sales"),
            "fieldtype": "Data",
            "width": 150,
            "align": "right",
        },
        {
            "fieldname": "daily_collections",
            "label": _("Daily Collection"),
            "fieldtype": "Data",
            "width": 150,
            "align": "right",
        },
        {
            "fieldname": "weekly_sales",
            "label": _("Weekly Sales"),
            "fieldtype": "Data",
            "align": "right",
            "width": 150,
        },
        {
            "fieldname": "weekly_collections",
            "label": _("Weekly Collection"),
            "fieldtype": "Data",
            "width": 150,
            "align": "right",
        },
        {
            "fieldname": "monthly_sales",
            "label": _("Monthly Sales"),
            "fieldtype": "Data",
            "width": 150,
            "align": "right",
        },
        {
            "fieldname": "monthly_collections",
            "label": _("Monthly Collection"),
            "fieldtype": "Data",
            "width": 150,
            "align": "right",
        },
    ]

    return columns
