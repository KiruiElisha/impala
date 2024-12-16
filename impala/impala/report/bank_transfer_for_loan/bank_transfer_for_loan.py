# Copyright (c) 2024, Aqiq and contributors
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
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
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
			"label": _("Salary Mode"),
			"width": 120,
		},
		# {
		# 	"fieldname": "amount",
		# 	"fieldtype": "Currency",
		# 	"label": _("Payment Amount"),
		# 	"width": 120,
		# },
		{
			"fieldname": "transaction_type_code",
			"fieldtype": "data",
			"label": _("Transaction Type Code"),
			"width": 220,
		},
		{
			"fieldname": "payment_type",
			"fieldtype": "data",
			"label": _("Payment Type"),
			"width": 120,
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
		{
			"fieldname": "loan_type",
			"label": _("Loan Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "loan_amount",
			"fieldtype": "Currency",
			"label": _("Loan Amount"),
			"width": 120,
		},
		


	]

	return columns

def get_data(conditions="", filters={}):
	details = {}
	
	SQL_QUERY = """
		SELECT
			loan.loan_amount,
			loan.docstatus,
			loan.status,
			loan.loan_type,
			emp.employee,
			emp.employee_name,
			emp.bank_name,
			emp.bank_ac_no,
			emp.salary_mode,
			emp.branch_code,
			emp.bank_code,
			emp.transaction_type_code,
			emp.charge_type,
			emp.payment_type
		FROM
			`tabLoan` loan
			INNER JOIN `tabEmployee` emp ON loan.applicant = emp.name
		WHERE loan.docstatus<2 %s
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
	if filters.get("loan_type"):
		conditions += " and loan.loan_type = '{}'".format(filters.get("loan_type"))
	if filters.get("status"):
		conditions += " and loan.status = '{}'".format(filters.get("status"))
	if filters.get("from_date"):
		conditions += " and loan.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and loan.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("docstatus"):
		conditions += " and loan.docstatus = {}".format(1 if filters.get("docstatus")=="Submitted" else 0)
	return conditions
