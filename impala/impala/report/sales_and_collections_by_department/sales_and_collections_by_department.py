# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, today, getdate
import datetime
from dateutil.relativedelta import relativedelta
import dateutil
def execute(filters=None):
    
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    daily_sales = get_daily_sales(filters, conditions)

    """ Getting this year this week"""

    this_yr, this_week, this_weekday = datetime.date.today().isocalendar()
    this_yr_week = int(f"{this_yr}{this_week}")
    week_start = datetime.date(this_yr, 1, 1) + dateutil.relativedelta.relativedelta(weeks=+this_week, days=-6)
    week_end = datetime.date(this_yr, 1, 1) + dateutil.relativedelta.relativedelta(weeks=+this_week)

    """ Getting this month date range"""
    tod = getdate()
    month_start = tod.replace(day=1)
    from dateutil.relativedelta import relativedelta
    month_end = month_start + relativedelta(months=1, days=-1)


    weekly_sales = get_weekly_sales(filters, conditions, week_start, week_end)
    monthly_sales = get_monthly_sales(filters, conditions, month_start, month_end)
    daily_collections = get_daily_collections(filters, conditions)
    weekly_collections = get_weekly_collections(filters, conditions, week_start, week_end)
    monthly_collections = get_monthly_collections(filters, conditions, month_start, month_end)

    data = []
    dept_list = frappe.db.get_list("Department", filters = {"disabled" : 0}, pluck = "name")
    currency_list = frappe.db.get_list("Currency", filters = {"enabled" : 1}, pluck = "name")

    report_data = {}
    for d in dept_list:
        for i in currency_list:
            row = {}
            has_value = False
            for z in daily_sales:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['daily_sales'] = z.get("daily_sales") or "KES 0.0"
                    if z.get("sales_val") > 0.05:
                        has_value = True
            for z in weekly_sales:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['weekly_sales'] = z.get("weekly_sales") or "KES 0.0"

                    if z.get("sales_val") > 0.05:
                        has_value = True

            for z in monthly_sales:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['monthly_sales'] = z.get("monthly_sales") or "KES 0.0"
                    if z.get("sales_val") > 0.05:
                        has_value = True

            for z in daily_collections:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['daily_collections'] = z.get("daily_collections") or "KES 0.0"
                    if z.get("collection_val") > 0.05:
                        has_value = True

            for z in weekly_collections:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['weekly_collections'] = z.get("weekly_collections") or "KES 0.0"
                    if z.get("collection_val") > 0.05:
                        has_value = True

            for z in monthly_collections:
                if d == z.get("department") and i == z.get("currency"):
                    row['department'] = d
                    row['currency'] = i
                    row['monthly_collections'] = z.get("monthly_collections") or "KES 0.0"
                    if z.get("collection_val") > 0.05:
                        has_value = True

            if has_value==True:
                data.append(row)

    frappe.log_error(cstr(data))
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



def get_daily_sales(filters, conditions):

    sales = frappe.db.sql("""SELECT department, currency, CONCAT(currency," ", FORMAT(IFNULL(SUM(grand_total), 0.0), 2, 'en_US')) as daily_sales, SUM(grand_total) as sales_val
            FROM `tabSales Invoice`
            WHERE docstatus=1 and posting_date = '{}' {} GROUP BY department, currency ORDER BY department, currency""".format(today(), conditions), as_dict=1)

    return sales


def get_weekly_sales(filters, conditions, week_start, week_end):
    
    sales = frappe.db.sql("""SELECT department, currency, CONCAT(currency," ", FORMAT(IFNULL(SUM(grand_total), 0.0), 2, 'en_US')) as weekly_sales, SUM(grand_total) as sales_val
            FROM `tabSales Invoice`
            WHERE docstatus=1 and posting_date BETWEEN '{}' AND '{}' {} GROUP BY department, currency ORDER BY department, currency""".format(week_start, week_end, conditions),as_dict=1, debug=True)
   
    return sales


def get_monthly_sales(filters, conditions, month_start, month_end):
    

    sales = frappe.db.sql("""SELECT department, currency, CONCAT(currency," ", FORMAT(SUM(grand_total), 2, 'en_US')) as monthly_sales, SUM(grand_total) as sales_val
            FROM `tabSales Invoice`
            WHERE docstatus=1 and posting_date BETWEEN '{}' AND '{}' {} GROUP BY department, currency ORDER BY department, currency""".format(month_start, month_end, conditions),as_dict=1)

    return sales


def get_daily_collections(filters, conditions):

    collections = frappe.db.sql("""SELECT department, paid_from_account_currency as currency, CONCAT(paid_from_account_currency," ", FORMAT(SUM(paid_amount), 2, 'en_US')) as daily_collections, SUM(paid_amount) as collection_val
        FROM `tabPayment Entry`
        WHERE docstatus=1  and payment_type='Receive' and posting_date='{}' {} GROUP BY department, paid_from_account_currency ORDER BY department, paid_from_account_currency""".format(today(), conditions), as_dict=1)

    return collections


def get_weekly_collections(filters, conditions, week_start, week_end):
    current_week = datetime.date.today().isocalendar()[1]

    collections = frappe.db.sql("""SELECT department, paid_from_account_currency as currency, CONCAT(paid_from_account_currency," ", FORMAT(SUM(paid_amount), 2, 'en_US')) as weekly_collections, SUM(paid_amount) as collection_val
        FROM `tabPayment Entry`
        WHERE docstatus=1  and payment_type='Receive' and posting_date BETWEEN '{}' and '{}' {} GROUP BY department, paid_from_account_currency ORDER BY department, paid_from_account_currency""".format(week_start, week_end, conditions), as_dict=1)

    return collections


def get_monthly_collections(filters, conditions, month_start, month_end):

    collections = frappe.db.sql("""SELECT department, paid_from_account_currency as currency, CONCAT(paid_from_account_currency," ", FORMAT(IFNULL(SUM(paid_amount), 0.0), 2, 'en_US')) as monthly_collections, SUM(paid_amount) as collection_val
        FROM `tabPayment Entry`
        WHERE docstatus=1  and payment_type='Receive' and posting_date BETWEEN '{}' AND '{}' {} GROUP BY department, paid_from_account_currency ORDER BY department, paid_from_account_currency""".format(month_start, month_end, conditions), as_dict=1)

    return collections


def get_columns(filters):
    columns = [
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 280,
        },
        {  
            "fieldname": "currency",
            "label": _("Currency"),
            "fieldtype": "Link",
            "options": "Currency",
            "width": 200,
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
            "width": 150,
            "align": "right",
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
            "align": "right"
        },
    ]

    return columns
