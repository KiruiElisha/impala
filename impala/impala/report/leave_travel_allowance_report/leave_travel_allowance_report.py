# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta
import time

def execute(filters=None):
	if not filters:
		filters = {}

	conditions = get_conditions(filters)
	columns = get_column(filters, conditions)
	data = get_data(conditions, filters)

	for d in data:
		d['beneficiary_address_line1'] = "Nairobi"
		d['transaction_currency'] = "KES"

	return columns, data



def get_column(filters,conditions):
	group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
	field_is = group_by_detail.get(filters.get("group_by"))

	columns = [
		# {
		# 	"fieldname": "name",
		# 	"label": _("Payroll Monthly Input ID"),
		# 	"fieldtype": "Link",
		# 	"options": "Payroll Monthly Input",
		# 	"width": 100
		# },
		{
			"fieldname": "employee",
			"label": _("Employee"),
			"fieldtype": "Data",
			"options": "Employee",
			"width": 200
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "docstatus",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "bank_name",
			"fieldtype": "data",
			"label": _("Bank Name"),
			"width": 260,
		},
		{
			"fieldname": "branch_code",
			"fieldtype": "data",
			"label": _("Branch Code"),
			"width": 120,
		},
		{
			"fieldname": "bank_code",
			"fieldtype": "data",
			"label": _("Bank Code/Swift Code"),
			"width": 120,
		},
		{
			"fieldname": "bank_ac_no",
			"fieldtype": "data",
			"label": _("Beneficiary Account No"),
			"width": 220,
		},
		{
			"fieldname": "salary_mode",
			"fieldtype": "data",
			"label": _("Payment Type"),
			"width": 120,
		},
		{
			"fieldname": "amount",
			"fieldtype": "Currency",
			"label": _("Payment Amount"),
			"width": 120,
		},
		{
			"fieldname": "transaction_type_code",
			"fieldtype": "data",
			"label": _("Transaction Type Code"),
			"width": 220,
		},
		{
			"fieldname": "purpose_of_payment",
			"fieldtype": "data",
			"label": _("Purpose of Payment"),
			"width": 220,
		},
		{
			"fieldname": "beneficiary_address_line1",
			"fieldtype": "data",
			"label": _("Beneficiary Address Line 1"),
			"width": 220,
			"default": "Nairobi",
		},
		{
			"fieldname": "charge_type",
			"fieldtype": "data",
			"label": _("Charge Type"),
			"width": 120,
		},
		{
			"fieldname": "transaction_currency",
			"fieldtype": "data",
			"label": _("Transaction Currency"),
			"width": 120,
			"default": "KES",
		},
		# {
		# 	"fieldname": "payment_type",
		# 	"fieldtype": "data",
		# 	"label": _("Payment Type"),
		# 	"width": 120,
		# },


	]

	return columns

def get_data(conditions="", filters={}):
	details = {}
	
	SQL_QUERY = """
		SELECT
			mpi.amount,
			mpid.employee,
			mpid.employee_name,
			emp.bank_name,
			emp.bank_ac_no,
			emp.salary_mode,
			emp.branch_code,
			emp.bank_code,
			emp.transaction_type_code,
			emp.charge_type,
			emp.payment_type,
			mpi.docstatus,
			mpi.name,
			mpi.salary_component

		FROM
			`tabSalary Detail` mpi
			INNER JOIN `tabSalary Slip` mpid ON mpi.parent=mpid.name
			INNER JOIN `tabEmployee` emp ON mpid.employee = emp.name %s
	""" %conditions

	data = frappe.db.sql(SQL_QUERY, as_dict=1)
	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("department"):
		conditions += " and emp.department = '{}'".format(filters.get("department"))
	if filters.get("designation"):
		conditions += " and emp.designation = '{}'".format(filters.get("designation"))

	if filters.get("employee"):
		conditions += " and emp.name = '{}'".format(filters.get("employee"))

	if filters.get("cost_center"):
		conditions += " and emp.cost_center = '{}'".format(filters.get("cost_center"))

	if filters.get("branch"):
		conditions += " and emp.branch = '{}'".format(filters.get("branch"))

	if filters.get("from_date"):
		conditions += " and mpid.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and mpid.posting_date <= '{}'".format(filters.get("to_date"))

	return conditions

# SELECT mpid.amount,mpid.employee,mpid.employee_name,emp.bank_name,emp.bank_ac_no,emp.salary_mode,emp.branch_code,emp.bank_code,emp.transaction_type_code,emp.charge_type,emp.payment_type,mpi.docstatus,mpi.name,mpi.salary_component FROM `tabPayroll Monthly Input` mpi INNER JOIN `tabPayroll Monthly Input Employees` mpid ON mpi.name=mpid.parent INNER JOIN `tabEmployee` emp ON mpid.employee = emp.name ;