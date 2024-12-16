# Copyright (c) 2023, Aqiq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta

def execute(filters=None):
	columns, data = [], []

	conditions = get_conditions(filters)

	# get_no_of_columns = frappe.db.sql("""select count(*) from `tabEmployee Checkin` chk 
	# 	inner join `tabEmployee` emp on emp.name = chk.employee where 1=1
	# 	{} group by chk.employee, date(`time`) order by 1 desc limit 1
	# 	""".format(conditions))[0][0] or 0
	


	checkins = frappe.db.sql("""select emp.name as employee, 
		date(`time`) as date, `time` as checkin from `tabEmployee Checkin` chk 
		inner join `tabEmployee` emp on emp.name = chk.employee where 1=1
		{}  order by 1,2,3 asc
		""".format(conditions),as_dict=1)

	employees = frappe.db.sql("""select emp.name as employee, emp.employee_name, 
		date(`time`) as date from `tabEmployee Checkin` chk 
		inner join `tabEmployee` emp on emp.name = chk.employee where 1=1
		{} group by 1,3 order by 1,3 asc
		""".format(conditions),as_dict=1)
	max_count = 0
	for d in employees:
		row = {}
		row.update(d)
		count = 0
		for i in checkins:
			if d.employee == i.employee and d.date == i.date:
				count+=1
				checkin = str(i.checkin).split(" ")[1]
				row["checkin"+str(count)] = checkin
		if count > max_count:
			max_count = count
		data.append(row)

	columns = get_column(max_count)

	return columns, data


def get_column(get_no_of_columns):
	columns = [
		{
			"fieldname": "employee",
			"label": _("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
	]

	get_no_of_columns+=1

	for d in range(1, get_no_of_columns):
		columns.append({
			"fieldname": "checkin"+str(d),
			"label": _("Checkin "+str(d)),
			"fieldtype": "Data",
			"width": 100
		},)

	return columns


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

	if filters.get("time_table"):
		conditions += " and chk.time_table = '{}'".format(filters.get("time_table"))

	if filters.get("from_date"):
		conditions += " and date(`time`) >= '{}'".format(filters.get("from_date"))

	if filters.get("to_date"):
		conditions += " and date(`time`) <= '{}'".format(filters.get("to_date"))

	return conditions
