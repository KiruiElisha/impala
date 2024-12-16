# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from quopri import decodestring
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from frappe.utils import cstr, getdate, today
import calendar
import datetime


def execute(filters=None):
    today_date = datetime.datetime.date(datetime.datetime.now())
    current_date_month = getdate(today_date).month
    current_date_year = getdate(today_date).year
    select_group = ""
    groupby = ""
    select_group = "cost_center as details"
    data = []
    columns = get_columns(current_date_month)
    master = get_details(filters)
    for d in master:
        row = {}
        current_date_year = getdate(today_date).year
        current_date_month = 1
        row["details"] = d.get("details")
        for i in range(12):
            groupby = "GROUP BY cost_center ORDER BY cost_center"
            query_data_sales = get_monthly_sales(
                select_group,
                d.get("details"),
                calendar.month_name[current_date_month],
                current_date_year,
                groupby,
            )
            groupby = "GROUP BY si.cost_center ORDER BY si.cost_center"
            query_data_collections = get_monthly_collections(
                d.get("details"),
                calendar.month_name[current_date_month],
                current_date_year,
                groupby,
            )
            if query_data_sales:
                # frappe.msgprint(cstr(query_data_sales))
                row[
                    calendar.month_name[current_date_month] + "sales"
                ] = query_data_sales[0].get("sales")
            else:
                row[calendar.month_name[current_date_month] + "sales"] = 0.0
            if query_data_collections:
                # frappe.msgprint(cstr(query_data_collections))
                row[
                    calendar.month_name[current_date_month] + "collection"
                ] = query_data_collections[0].get("collection")
            else:
                row[calendar.month_name[current_date_month] + "collection"] = 0.0
            row[calendar.month_name[current_date_month] + "outstanding"] = row.get(
                calendar.month_name[current_date_month] + "sales"
            ) - row.get(calendar.month_name[current_date_month] + "collection")
            current_date_month = current_date_month + 1
            if current_date_month == 13:
                current_date_month = current_date_month - 12

        data.append(row)

        # frappe.msgprint(cstr())
        sv = sort_value()
        data = sorted(
            data,
            key=lambda i: (
                i.get(sv[0]),
                i.get(sv[1]),
                i.get(sv[2]),
                i.get(sv[3]),
                i.get(sv[4]),
                i.get(sv[5]),
                i.get(sv[6]),
                i.get(sv[7]),
                i.get(sv[8]),
                i.get(sv[9]),
                i.get(sv[10]),
                i.get(sv[11]),
                i.get(sv[12]),
                i.get(sv[13]),
                i.get(sv[14]),
                i.get(sv[15]),
                i.get(sv[16]),
                i.get(sv[17]),
                i.get(sv[18]),
                i.get(sv[19]),
                i.get(sv[20]),
                i.get(sv[21]),
                i.get(sv[22]),
                i.get(sv[23]),
                i.get(sv[24]),
                i.get(sv[25]),
                i.get(sv[26]),
                i.get(sv[27]),
                i.get(sv[28]),
                i.get(sv[29]),
                i.get(sv[30]),
                i.get(sv[31]),
                i.get(sv[32]),
                i.get(sv[33]),
                i.get(sv[34]),
                i.get(sv[35]),
            ),
            reverse=True,
        )

    return columns, data


def sort_value():
    current_date_month = 1
    colsdict = []
    for _ in range(12):
        colsdict.append(
            calendar.month_name[current_date_month] + "sales",
        )
        colsdict.append(
            calendar.month_name[current_date_month] + "collection",
        )
        colsdict.append(
            calendar.month_name[current_date_month] + "outstanding",
        )
        current_date_month = current_date_month + 1
        if current_date_month == 13:
            current_date_month = current_date_month - 12
    return colsdict


def get_details(filters):
    if filters.get("cost_center"):
        details = frappe.db.sql(
            """SELECT name as details FROM `tabCost Center`
				WHERE company = '{}' and name = '{}' """.format(
                filters.get("company"),
                filters.get("cost_center"),
            ),
            as_dict=1,
            # debug=True,
        )
    else:
        details = frappe.db.sql(
            """SELECT  name as details FROM `tabCost Center` WHERE company = '{}' """.format(
                filters.get("company")
            ),
            as_dict=1,
            # debug=True,
        )
    return details


def get_monthly_sales(select_group, details, month, year, groupby):
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
                    FROM `tabSales Invoice`
                    WHERE docstatus=1 and cost_center="{}" and MONTHNAME(posting_date)='{}' and YEAR(posting_date) = '{}' {}""".format(
            select_group,
            details,
            month,
            year,
            groupby,
        ),
        as_dict=1,
        # debug=True,
    )

    return sales


# def get_monthly_collections(details, month, year, groupby):
#     collections = frappe.db.sql(
#         """SELECT pe.party, cs.customer_name as details, SUM(pe.paid_amount) as collection
#             FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
#             WHERE pe.docstatus=1 and cs.customer_code="{}" and pe.payment_type='Receive' and MONTHNAME(pe.posting_date)='{}' and YEAR(pe.posting_date) = '{}' {}""".format(
#             details,
#             month,
#             year,
#             groupby,
#         ),
#         as_dict=1,
#         debug=True,
#     )

#     return collections


def get_monthly_collections(details, month, year, groupby):
    collections = frappe.db.sql(
        """SELECT si.cost_center as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
		inner join `tabSales Invoice` si on  per.reference_name = si.name 
		WHERE pe.docstatus=1 and si.cost_center="{}" and pe.payment_type='Receive' and MONTHNAME(si.posting_date)='{}' and YEAR(si.posting_date) = '{}' {}""".format(
            details,
            month,
            year,
            groupby,
        ),
        as_dict=1,
        # debug=True,
    )

    return collections


def get_columns(b):

    columns = [
        {
            "fieldname": "details",
            "label": _("Division"),
            "fieldtype": "Data",
            "width": 250,
        }
    ]
    b = 1
    for i in range(12):
        columns.append(
            {
                "fieldname": calendar.month_name[b] + "sales",
                "label": _(calendar.month_name[b] + " Sales"),
                "fieldtype": "Currency",
                "width": 150,
            }
        )
        columns.append(
            {
                "fieldname": calendar.month_name[b] + "collection",
                "label": _(calendar.month_name[b] + " Collection"),
                "fieldtype": "Currency",
                "width": 150,
            }
        )
        columns.append(
            {
                "fieldname": calendar.month_name[b] + "outstanding",
                "label": _(calendar.month_name[b] + " Outstanding"),
                "fieldtype": "Currency",
                "width": 150,
            }
        )
        b = b + 1
        if b == 13:
            b = b - 12

    return columns
