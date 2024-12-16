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
    group_doctype = "Item Group"
    select_details = "name as details"
    data = []
    columns = get_columns(filters)
    select_group = "sii.item_group as details"
    groupby = "GROUP BY sii.item_group ORDER BY sii.item_group"
    conditions = get_conditions(filters)
    daily_conditions = get_daily_conditions(filters)
    daily_sales = get_daily_sales(select_group, daily_conditions, groupby)
    weekly_sales = get_weekly_sales(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales(select_group, conditions, groupby)
    # yearly_sales = get_yearly_sales(select_group, conditions, groupby)
    # conditions = get_conditions2(filters)
    # daily_collections = get_daily_collections(conditions, groupby)
    # weekly_collections = get_weekly_collections(conditions, groupby)
    # monthly_collections = get_monthly_collections(conditions, groupby)

    master = get_details(select_details, group_doctype, filters)
    for d in master:
        row = {}
        has_value = False
        row["details"] = d.get("details")
        if daily_sales:
            for ds in daily_sales:
                if ds.get("details") == d.get("details"):
                    if ds.get("sales"):
                        row["daily_sales"] = ds.get("sales")
                        has_value = True
                    break
                else:
                    row["daily_sales"] = 0.0
        else:
            row["daily_sales"] = 0.0

        if weekly_sales:
            for ws in weekly_sales:
                if ws.get("details") == d.get("details"):
                    if ws.get("sales"):
                        row["weekly_sales"] = ws.get("sales")
                        has_value = True
                        break
                else:
                    row["weekly_sales"] = 0.0
        else:
            row["weekly_sales"] = 0.0

        if monthly_sales:
            for ms in monthly_sales:
                if ms.get("details") == d.get("details"):
                    if ms.get("sales"):
                        has_value = True
                        row["monthly_sales"] = ms.get("sales")
                        break
                else:
                    row["monthly_sales"] = 0.0
        else:
            row["monthly_sales"] = 0.0

        # if yearly_sales:
        #     for ms in yearly_sales:
        #         if ms.get("details") == d.get("details"):
        #             if ms.get("sales"):
        #                 has_value = True
        #                 row["yearly_sales"] = ms.get("sales")
        #                 break
        #         else:
        #             row["yearly_sales"] = 0.0
        # else:
        #     row["yearly_sales"] = 0.0

        # if daily_collections:
        #     for dc in daily_collections:
        #         if dc.get("details") == d.get("details"):
        #             row["daily_collections"] = dc.get("collection")
        #             break
        #         else:
        #             row["daily_collections"] = 0.0
        # else:
        #     row["daily_collections"] = 0.0

        # if weekly_collections:
        #     for wc in weekly_collections:
        #         if wc.get("details") == d.get("details"):
        #             row["weekly_collections"] = wc.get("collection")
        #             break
        #         else:
        #             row["weekly_collections"] = 0.0
        # else:
        #     row["weekly_collections"] = 0.0

        # if monthly_collections:
        #     for mc in monthly_collections:
        #         if mc.get("details") == d.get("details"):
        #             row["monthly_collections"] = mc.get("collection")
        #             break
        #         else:
        #             row["monthly_collections"] = 0.0
        # else:
        #     row["monthly_collections"] = 0.0
        if has_value==True:
            data.append(row)
    data = sorted(
        data,
        key=lambda i: (
            i.get("daily_sales"),
            # i.get("daily_collections"),
            i.get("weekly_sales"),
            # i.get("weekly_collections"),
            i.get("monthly_sales"),
            # i.get("monthly_collections"),
            i.get("yearly_sales"),
        ),
        reverse=True,
    )

    return columns, data


# def get_conditions2(filters):
#     conditions = ""

#     if filters.get("company"):
#         conditions += " and pe.company = '{}'".format(filters.get("company"))
#     if filters.get("customer_groups"):
#         conditions += " and cs.customer_group = '{}'".format(
#             filters.get("customer_groups")
#         )
#     if filters.get("from_date"):
#         conditions += " and pe.posting_date >= '{}'".format(filters.get("from_date"))
#     if filters.get("to_date"):
#         conditions += " and pe.posting_date <= '{}'".format(filters.get("to_date"))

#     return conditions


def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and si.company = '{}'".format(filters.get("company"))
    if filters.get("item_groups"):
        conditions += " and sii.item_group = '{}'".format(filters.get("item_groups"))
    # if filters.get("from_date"):
    #     conditions += " and si.posting_date >= '{}'".format(filters.get("from_date"))
    # if filters.get("to_date"):
    #     conditions += " and si.posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_daily_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and si.company = '{}'".format(filters.get("company"))

    if filters.get("item_groups"):
        conditions += " and sii.item_group = '{}'".format(filters.get("item_groups"))

    if filters.get("from_date"):
        conditions += " and si.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and si.posting_date <= '{}'".format(filters.get("to_date"))
    if not (filters.get("from_date") and filters.get("to_date")):
        conditions += " and si.posting_date = '{}'".format(today())
    return conditions

def get_details(select_details, group_doctype, filters):
    if filters.get("item_groups"):
        details = frappe.db.sql(
            """SELECT {} FROM `tab{}`
                WHERE company = '{}' and name = '{}' """.format(
                select_details,
                group_doctype,
                filters.get("company"),
                filters.get("item_groups"),
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
    today_date = datetime.date.today()
    
    sales = frappe.db.sql(
        """SELECT {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si
            INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE si.docstatus=1 AND si.posting_date='{}' {} {}""".format(
            select_group, today_date, conditions, groupby
        ),
        as_dict=1,
        debug=False,
    )

    return sales


def get_weekly_sales(select_group, conditions, groupby):
    current_week = datetime.date.today().strftime("%U")
    current_yr = datetime.date.today().strftime("%Y")

    sales = frappe.db.sql(
        """SELECT {}, SUM(sii.base_net_amount) as sales
            FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on  si.name = sii.parent
            WHERE si.docstatus=1 and WEEK(si.posting_date)= '{}' and YEAR(posting_date)='{}' {} {}""".format(
            select_group, current_week, current_yr, conditions, groupby
        ),
        as_dict=1,
        debug=False,
    )

    return sales


def get_monthly_sales(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    current_year = datetime.date.today().strftime("%Y")
    sales = frappe.db.sql(
        """SELECT {}, SUM(sii.base_net_amount) as sales
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
        """SELECT {}, SUM(sii.base_net_amount) as sales
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
            "fieldname": "details",
            "label": _("Item Group"),
            "fieldtype": "Data",
            "width": 260,
        },
        {
            "fieldname": "daily_sales",
            "label": _("Todays Sales"),
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
        # {
        #     "fieldname": "yearly_sales",
        #     "label": _("Yearly Sales"),
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
    ]

    return columns
