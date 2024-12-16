# Copyright (c) 2024, Aqiq and contributors
# For license information, please see license.txt

from itertools import groupby
import frappe
from frappe import _
from frappe.utils import add_days
from erpnext.hr.doctype.leave_application.leave_application import (
    get_leave_balance_on,
    get_leaves_for_period,
)

def execute(filters=None):
    if filters.to_date <= filters.from_date:
        frappe.throw(_('"From Date" can not be greater than or equal to "To Date"'))
    columns = get_columns()
    data = get_data(filters)
    charts = get_chart_data(data)
    return columns, data, None, charts

def get_columns():
    return [
        {'label': _('Leave Type'), 'fieldtype': 'Link', 'fieldname': 'leave_type', 'width': 200, 'options': 'Leave Type'},
        {'label': _('Employee'), 'fieldtype': 'Link', 'fieldname': 'employee', 'width': 100, 'options': 'Employee'},
        {'label': _('Employee Name'), 'fieldtype': 'Dynamic Link', 'fieldname': 'employee_name', 'width': 100, 'options': 'employee'},
        {'label': _('Opening Balance'), 'fieldtype': 'float', 'fieldname': 'opening_balance', 'width': 130},
        {'label': _('Leave Allocated'), 'fieldtype': 'float', 'fieldname': 'leaves_allocated', 'width': 130},
        {'label': _('Leave Taken'), 'fieldtype': 'float', 'fieldname': 'leaves_taken', 'width': 130},
        {'label': _('Leave Expired'), 'fieldtype': 'float', 'fieldname': 'leaves_expired', 'width': 130},
        {'label': _('Closing Balance'), 'fieldtype': 'float', 'fieldname': 'closing_balance', 'width': 130},
    ]

def get_data(filters):
    leave_types = frappe.db.get_list('Leave Type', pluck='name', order_by='name')
    conditions = get_conditions(filters)
    user = frappe.session.user
    department_approver_map = get_department_leave_approver_map(filters.get('department'))

    active_employees = frappe.get_list('Employee', filters=conditions, fields=['name', 'employee_name', 'department', 'user_id', 'leave_approver'])
    data = []
    employee_leave_data = get_employee_leave_data(filters, active_employees, leave_types)

    for employee, leave_data in employee_leave_data.items():
        for leave_type, leave_details in leave_data.items():
            row = frappe._dict({
                'leave_type': leave_type,
                'employee': employee.name,
                'employee_name': employee.employee_name,
                'opening_balance': leave_details['opening'],
                'leaves_allocated': leave_details['new_allocation'],
                'leaves_taken': leave_details['leaves_taken'],
                'leaves_expired': leave_details['expired_leaves'],
                'closing_balance': leave_details['closing_balance'],
                'indent': 1
            })
            data.append(row)
    return data

def get_conditions(filters):
    conditions = {'status': 'Active'}
    if filters.get('employee'):
        conditions['name'] = filters.get('employee')
    if filters.get('company'):
        conditions['company'] = filters.get('company')
    if filters.get('department'):
        conditions['department'] = filters.get('department')
    return conditions

def get_department_leave_approver_map(department=None):
    department_list = frappe.get_list('Department', filters={'disabled': 0}, or_filters={'name': department, 'parent_department': department}, fields=['name'], pluck='name')
    approver_list = frappe.get_all('Department Approver', filters={'parentfield': 'leave_approvers', 'parent': ('in', department_list)}, fields=['parent', 'approver'], as_list=1)
    approvers = {k: [v for k, v in approver_list] for k, v in approver_list}
    return approvers

def get_allocated_and_expired_leaves(from_date, to_date, employee, leave_type):
    records = frappe.db.sql("""
        SELECT employee, leave_type, from_date, to_date, leaves, transaction_name, transaction_type, is_carry_forward, is_expired
        FROM `tabLeave Ledger Entry`
        WHERE employee=%(employee)s AND leave_type=%(leave_type)s AND docstatus=1 AND transaction_type = 'Leave Allocation'
        AND (from_date between %(from_date)s AND %(to_date)s OR to_date between %(from_date)s AND %(to_date)s
        OR (from_date < %(from_date)s AND to_date > %(to_date)s))
    """, {
        "from_date": from_date,
        "to_date": to_date,
        "employee": employee,
        "leave_type": leave_type
    }, as_dict=1)

    new_allocation = sum(record.leaves for record in records if record.from_date >= frappe.utils.getdate(from_date))
    expired_leaves = sum(record.leaves for record in records if record.to_date < frappe.utils.getdate(to_date))
    return new_allocation, expired_leaves

def get_employee_leave_data(filters, active_employees, leave_types):
    employee_leave_data = {}
    for employee in active_employees:
        leave_approvers = get_leave_approvers(employee.department)
        if can_access_leave_data(filters, employee, leave_approvers):
            employee_leave_data[employee.name] = {}
            for leave_type in leave_types:
                leaves_taken = get_leaves_for_period(employee.name, leave_type, filters.from_date, filters.to_date) * -1
                new_allocation, expired_leaves = get_allocated_and_expired_leaves(filters.from_date, filters.to_date, employee.name, leave_type)
                opening = get_leave_balance_on(employee.name, leave_type, add_days(filters.from_date, -1))
                closing_balance = new_allocation + opening - (expired_leaves + leaves_taken)
                employee_leave_data[employee.name][leave_type] = {
                    'leaves_taken': leaves_taken,
                    'new_allocation': new_allocation,
                    'expired_leaves': expired_leaves,
                    'opening': opening,
                    'closing_balance': closing_balance
                }
    return employee_leave_data

def get_leave_approvers(department):
    department_approver_map = get_department_leave_approver_map(department)
    return department_approver_map.get(department, [])

def can_access_leave_data(filters, employee, leave_approvers):
    user = frappe.session.user
    return (leave_approvers and user in leave_approvers) or (user in ["Administrator", employee.user_id]) or ("HR Manager" in frappe.get_roles(user))

def get_chart_data(data):
    labels = []
    datasets = []
    employee_data = sorted(data, key=lambda k: k['employee_name'])
    get_dataset_for_chart(employee_data, datasets, labels)
    return {
        'data': {'labels': labels, 'datasets': datasets},
        'type': 'bar',
        'colors': ['#456789', '#EE8888', '#7E77BF']
    }

def get_dataset_for_chart(employee_data, datasets, labels):
    leaves = []
    for key, group in groupby(employee_data, lambda x: x['employee_name']):
        for grp in group:
            if grp.closing_balance:
                leaves.append(frappe._dict({'leave_type': grp.leave_type, 'closing_balance': grp.closing_balance}))
        if leaves:
            labels.append(key)
    for leave in leaves:
        datasets.append({'name': leave.leave_type, 'values': [leave.closing_balance]})
