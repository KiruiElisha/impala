from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = get_conditions(filters)
    columns = get_columns()
    data = []

    total_ear = 0
    earnings_query = get_earnings_query(conditions)
    data.append({"description": "<b>EARNINGS</b>"})
    for d in earnings_query:
        row = {}
        row.update(d)
        row["description"] = d.salary_component
        data.append(row)
        total_ear += flt(d.amount)
    data.append({"description": "<b>TOTAL EARNINGS</b>", "amount": total_ear})

    total_ded = 0
    deductions_query = get_deductions_query(conditions)
    data.append({"description": "<b>DEDUCTIONS</b>"})
    for d in deductions_query:
        row = {}
        row.update(d)
        row["description"] = d.salary_component
        data.append(row)
        total_ded += flt(d.amount)
    data.append({"description": "<b>TOTAL DEDUCTIONS</b>", "amount": total_ded})

    diff = flt(total_ear) - flt(total_ded)

    data.append({"description": "<b>PAYMENT ANALYSIS</b>"})
    total_paid = 0
    payment_details_query = get_payment_details_query(conditions)
    for i in payment_details_query:
        data.append({"description": i.salary_mode, "nos": i.nos, "amount": i.paid})
        total_paid += flt(i.paid)

    net_due = flt(diff) - flt(total_paid)
    data.append({"description": "NET PAY DUE", "amount": net_due})

    return columns, data

def get_columns():
    return [
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 400
        },
        {
            "fieldname": "nos",
            "label": _("NOs"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 300
        },
    ]

def get_conditions(filters):
    conditions = ""
    if filters.get("department"):
        conditions += " and p.department = '{}'".format(filters.get("department"))
    if filters.get("designation"):
        conditions += " and p.designation = '{}'".format(filters.get("designation"))
    if filters.get("branch"):
        conditions += " and p.branch = '{}'".format(filters.get("branch"))
    # if filters.get("employee"):
    #     conditions += " and e.employee = '{}'".format(filters.get("employee"))
    if filters.get("cost_center"):
                conditions += " and p.cost_center = '{}'".format(filters.get("cost_center"))
    if filters.get("start_date"):
        conditions += " and p.posting_date >= '{}'".format(filters.get("start_date"))
    if filters.get("end_date"):
        conditions += " and p.posting_date <= '{}'".format(filters.get("end_date"))

    return conditions

def get_earnings_query(conditions):
    return frappe.db.sql("""
        select c.salary_component, count(p.employee) as nos, sum(c.amount) as amount
        from `tabSalary Detail` c
        inner join `tabSalary Slip` p on p.name = c.parent
        inner join `tabEmployee` e on p.employee = e.name
        inner join `tabSalary Component` sc on sc.name = c.salary_component 
        where p.docstatus = 1 and e.status = 'Active' and c.parentfield = 'earnings'
        {} group by c.salary_component order by c.salary_component
    """.format(conditions), as_dict=1)

def get_deductions_query(conditions):
    return frappe.db.sql("""
        select c.salary_component, count(p.employee) as nos, sum(c.amount) as amount
        from `tabSalary Detail` c
        inner join `tabSalary Slip` p on p.name = c.parent
        inner join `tabEmployee` e on p.employee = e.name
        inner join `tabSalary Component` sc on sc.name = c.salary_component
        where p.docstatus = 1 and e.status = 'Active' and c.parentfield = 'deductions'
        {} group by c.salary_component order by c.salary_component
    """.format(conditions), as_dict=1)

def get_payment_details_query(conditions):
    return frappe.db.sql("""
        select e.salary_mode, count(p.employee) as nos, sum(p.net_pay) as paid
        from `tabSalary Slip` p
        inner join `tabEmployee` e on p.employee = e.name
        where p.docstatus = 1 and e.status = 'Active' {}
        group by e.salary_mode
    """.format(conditions), as_dict=1)