# Copyright (c) 2024, Aqiq and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}

    conditions, fiscal_year_start_month = get_conditions(filters)
    columns = get_columns(fiscal_year_start_month)
    data = []

    earnings_query = get_earnings_query(conditions, fiscal_year_start_month)
    data.append({"description": "<b>EARNINGS</b>"})
    for d in earnings_query:
        row = {"description": d.salary_component}
        for month in range(1, 13):
            row[f"nos_{month}"] = d.get(f"nos_{month}", 0)
            row[f"amount_{month}"] = d.get(f"amount_{month}", 0.0)
        data.append(row)

    deductions_query = get_deductions_query(conditions, fiscal_year_start_month)
    data.append({"description": "<b>DEDUCTIONS</b>"})
    for d in deductions_query:
        row = {"description": d.salary_component}
        for month in range(1, 13):
            row[f"nos_{month}"] = d.get(f"nos_{month}", 0)
            row[f"amount_{month}"] = d.get(f"amount_{month}", 0.0)
        data.append(row)

    payment_details_query = get_payment_details_query(conditions, fiscal_year_start_month)
    data.append({"description": "<b>PAYMENT ANALYSIS</b>"})
    for i in payment_details_query:
        row = {"description": i.salary_mode}
        for month in range(1, 13):
            row[f"nos_{month}"] = i.get(f"nos_{month}", 0)
            row[f"amount_{month}"] = i.get(f"paid_{month}", 0.0)
        data.append(row)

    return columns, data

def get_columns(fiscal_year_start_month):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    columns = [
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 200
        }
    ]
    for i in range(12):
        month_index = (fiscal_year_start_month + i - 1) % 12
        month_name = month_names[month_index]
        columns.append({
            "fieldname": f"nos_{i+1}",
            "label": _(f"NOs ({month_name})"),
            "fieldtype": "Int",
            "width": 100
        })
        columns.append({
            "fieldname": f"amount_{i+1}",
            "label": _(f"Amount ({month_name})"),
            "fieldtype": "Currency",
            "width": 150
        })
    return columns

def get_conditions(filters):
    conditions = ""
    fiscal_year_start_month = 1  # Default to January

    if filters.get("department"):
        conditions += " and p.department = '{}'".format(filters.get("department"))
    if filters.get("designation"):
        conditions += " and p.designation = '{}'".format(filters.get("designation"))
    if filters.get("branch"):
        conditions += " and p.branch = '{}'".format(filters.get("branch"))
    if filters.get("cost_center"):
        conditions += " and p.cost_center = '{}'".format(filters.get("cost_center"))
    if filters.get("fiscal_year"):
        fiscal_year = filters.get("fiscal_year")
        fiscal_year_start_month = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date").month
        conditions += " and YEAR(p.posting_date) = '{}'".format(fiscal_year)

    return conditions, fiscal_year_start_month

def get_earnings_query(conditions, fiscal_year_start_month):
    return frappe.db.sql("""
        select c.salary_component,
        {month_cases}
        from `tabSalary Detail` c
        inner join `tabSalary Slip` p on p.name = c.parent
        inner join `tabEmployee` e on p.employee = e.name
        where p.docstatus = 1 and e.status = 'Active' and c.parentfield = 'earnings'
        {} group by c.salary_component
    """.format(conditions, month_cases=generate_month_cases(fiscal_year_start_month, "c.amount")), as_dict=1)

def get_deductions_query(conditions, fiscal_year_start_month):
    return frappe.db.sql("""
        select c.salary_component,
        {month_cases}
        from `tabSalary Detail` c
        inner join `tabSalary Slip` p on p.name = c.parent
        inner join `tabEmployee` e on p.employee = e.name
        where p.docstatus = 1 and e.status = 'Active' and c.parentfield = 'deductions'
        {} group by c.salary_component
    """.format(conditions, month_cases=generate_month_cases(fiscal_year_start_month, "c.amount")), as_dict=1)

def get_payment_details_query(conditions, fiscal_year_start_month):
    return frappe.db.sql("""
        select e.salary_mode,
        {month_cases}
        from `tabSalary Slip` p
        inner join `tabEmployee` e on p.employee = e.name
        where p.docstatus = 1 and e.status = 'Active' {}
        group by e.salary_mode
    """.format(conditions, month_cases=generate_month_cases(fiscal_year_start_month, "p.net_pay")), as_dict=1)

def generate_month_cases(fiscal_year_start_month, amount_column):
    month_cases = []
    for i in range(12):
        month = (fiscal_year_start_month + i - 1) % 12 + 1
        month_cases.append(f"""
            sum(case when MONTH(p.posting_date) = {month} then 1 else 0 end) as nos_{i+1},
            sum(case when MONTH(p.posting_date) = {month} then {amount_column} else 0 end) as amount_{i+1}
        """)
    return ", ".join(month_cases)