# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, today
import datetime
def execute(filters=None):
    select_group = "sii.item_code as details"
    groupby = "GROUP BY sii.item_code"
    group_doctype = "Item"
    select_details = "name as details, item_name as name"
    columns = get_columns(filters)
    data = []
    cost_centers = frappe.db.get_list("Cost Center", pluck="name")

    master = get_details(select_details, group_doctype, filters)
    conditions = get_conditions(filters)
    daily_conditions = get_daily_conditions(filters)
    daily_sales = get_daily_sales(select_group, daily_conditions, groupby)
    weekly_sales = get_weekly_sales(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales(select_group, conditions, groupby)
    yearly_sales = get_yearly_sales(select_group, conditions, groupby)

    sales_data_dict = {}

    for cost_center in cost_centers:
        sales_data_dict[cost_center] = {
            "details": [],
            "daily_sales": 0.0,
            "weekly_sales": 0.0,
            "monthly_sales": 0.0,
            "yearly_sales": 0.0
        }

        for entry in daily_sales:
            if entry["details"]:
                sales_data_dict[cost_center]["daily_sales"] += entry.get("sales", 0.0)
                sales_data_dict[cost_center]["details"].append({
                    "details": entry.get("details"),
                    "daily_sales": entry.get("sales", 0.0),
                    "weekly_sales": 0.0,
                    "monthly_sales": 0.0,
                    "yearly_sales": 0.0
                })

        for entry in weekly_sales:
            if entry["details"]:
                sales_data_dict[cost_center]["weekly_sales"] += entry.get("sales", 0.0)
                sales_data_dict[cost_center]["details"].append({
                    "details": entry.get("details"),
                    "daily_sales": 0.0,
                    "weekly_sales": entry.get("sales", 0.0),
                    "monthly_sales": 0.0,
                    "yearly_sales": 0.0
                })

        for entry in monthly_sales:
            if entry["details"]:
                sales_data_dict[cost_center]["monthly_sales"] += entry.get("sales", 0.0)
                sales_data_dict[cost_center]["details"].append({
                    "details": entry.get("details"),
                    "daily_sales": 0.0,
                    "weekly_sales": 0.0,
                    "monthly_sales": entry.get("sales", 0.0),
                    "yearly_sales": 0.0
                })

        for entry in yearly_sales:
            if entry["details"]:
                sales_data_dict[cost_center]["yearly_sales"] += entry.get("sales", 0.0)
                sales_data_dict[cost_center]["details"].append({
                    "details": entry.get("details"),
                    "daily_sales": 0.0,
                    "weekly_sales": 0.0,
                    "monthly_sales": 0.0,
                    "yearly_sales": entry.get("sales", 0.0)
                })

    sales_data = [{"cost_center": key, **value} for key, value in sales_data_dict.items()]

    data = sorted(
        sales_data,
        key=lambda i: (
            i.get("cost_center"),
            i.get("details")[0]["details"] or '',
            i.get("details")[0]["daily_sales"] or 0.0,
            i.get("details")[0]["weekly_sales"] or 0.0,
            i.get("details")[0]["monthly_sales"] or 0.0,
            i.get("details")[0]["yearly_sales"] or 0.0,
        ),
        reverse=True,
    )

    return columns, data

def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and si.company = '{}'".format(filters.get("company"))
    if filters.get("item"):
        conditions += " and sii.item_code = '{}'".format(filters.get("item"))
    if filters.get("cost_center"):
        conditions += " and si.cost_center <= '{}'".format(filters.get("cost_center"))

    return conditions


def get_daily_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and si.company = '{}'".format(filters.get("company"))
    if filters.get("item"):
        conditions += " and sii.item_code = '{}'".format(filters.get("item"))
    if filters.get("cost_center"):
        conditions += " and si.cost_center <= '{}'".format(filters.get("cost_center"))

    if filters.get("from_date"):
        conditions += " and si.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and si.posting_date <= '{}'".format(filters.get("to_date"))
    if not (filters.get("from_date") and filters.get("to_date")):
        conditions += " and si.posting_date = '{}'".format(today())
    return conditions

def get_details(select_details, group_doctype, filters):
    if filters.get("item"):
        details = frappe.db.sql(
            """SELECT {} FROM `tab{}`
                WHERE company = '{}' and name = '{}' """.format(
                select_details,
                group_doctype,
                filters.get("company"),
                filters.get("item"),
            ),
            as_dict=1,
            debug=False,
        )
    else:
        details = frappe.db.sql(
            """SELECT {} FROM `tab{}`
                WHERE company = '{}' """.format(
                select_details, group_doctype, filters.get("company")
            ),
            as_dict=1,
            debug=False,
        )
    return details


def get_daily_sales(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT si.cost_center as cost_center, {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.name = sii.parent
            WHERE si.docstatus=1 {} {}""".format(
            select_group, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT si.cost_center as cost_center, {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on  si.name = sii.parent
            WHERE si.docstatus=1 and WEEK(si.posting_date)= '{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=False,
    )

    return sales


def get_monthly_sales(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    current_year = datetime.date.today().strftime("%Y")
    sales = frappe.db.sql(
        """SELECT si.cost_center as cost_center, {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on  si.name = sii.parent
            WHERE si.docstatus=1 and YEAR(si.posting_date)= '{}' and MONTHNAME(si.posting_date)= '{}' {} {}""".format(
            select_group, current_year, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=False,
    )

    return sales


def get_yearly_sales(select_group, conditions, groupby):
    current_year = datetime.date.today().strftime("%Y")
    sales = frappe.db.sql(
        """SELECT si.cost_center as cost_center, {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on  si.name = sii.parent
            WHERE si.docstatus=1 and YEAR(si.posting_date)= '{}' {} {}""".format(
            select_group, current_year, conditions, groupby
        ),
        as_dict=1,
        debug=False,
    )

    return sales


# def get_daily_collections(conditions, groupby):

#     collections = frappe.db.sql(
#         """ SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
#         FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
#         WHERE pe.docstatus=1 and pe.posting_date='{}' {} {}""".format(
#             today(), conditions, groupby
#         ),
#         as_dict=1,
#         debug=False,
#     )

#     return collections


# def get_weekly_collections(conditions, groupby):
#     current_week = datetime.date.today().isocalendar()[1]
#     collections = frappe.db.sql(
#         """ SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
#         FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
#         WHERE pe.docstatus=1 and WEEK(pe.posting_date)='{}' {} {}""".format(
#             current_week, conditions, groupby
#         ),
#         as_dict=1,
#         debug=False,
#     )

#     return collections


# def get_monthly_collections(conditions, groupby):
#     current_month = datetime.date.today().strftime("%B")

#     collections = frappe.db.sql(
#         """
#                             SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
#         FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
#         WHERE pe.docstatus=1 and MONTHNAME(pe.posting_date)='{}' {} {}""".format(
#             current_month, conditions, groupby
#         ),
#         as_dict=1,
#         debug=False,
#     )

#     return collections


def get_columns(filters):
    # dept_div_label = ""
    # if filters.get("groupby") == "Department":
    # 	dept_div_label = "Department"
    # if filters.get("groupby") == "Division":
    # 	dept_div_label = "Division"

    columns = [
        {
            "fieldname": "cost_center",
            "label": _("Division"),
            "fieldtype": "Data",
            "width": 260,
        },
        {
            "fieldname": "details",
            "label": _("Item"),
            "fieldtype": "Data",
            "width": 260,
        },
        {
            "fieldname": "daily_sales",
            "label": _("Daily Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        # {
        #     "fieldname": "daily_collections",
        #     "label": _("Daily Collection"),
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
        {
            "fieldname": "weekly_sales",
            "label": _("Weekly Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        # {
        #     "fieldname": "weekly_collections",
        #     "label": _("Weekly Collection"),
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
        {
            "fieldname": "monthly_sales",
            "label": _("Monthly Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
        # {
        #     "fieldname": "monthly_collections",
        #     "label": _("Monthly Collection"),
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
        {
            "fieldname": "yearly_sales",
            "label": _("Yearly Sales"),
            "fieldtype": "Currency",
            "width": 150,
        },
    ]

    return columns
