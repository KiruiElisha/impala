# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta
from frappe.utils import flt, getdate
import pandas as pd

def execute(filters=None):
	if not filters:
		filters = {}

	conditions = get_conditions(filters)
	columns = get_column(filters,conditions)
	data = []

	details = get_details(conditions, filters)

	group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
	group_by_data = frappe.db.sql("select name from `tab{}` where is_group = 0 and disabled = 0".format(filters.get("group_by")), as_dict=1)
	field_is = group_by_detail.get(filters.get("group_by"))
	value_in_details = {"Present": "P", "Absent": "A", "On Leave": "L", "Holiday": "HD", "Weekend": "WO"}
	master = frappe.db.sql("""select c.employee, e.employee_name, e.{}   
		from `tabEmployee` e inner join `tabAttendance` c on c.employee = e.name
		where e.status = 'Active' and c.docstatus = 1 {}
		""".format(field_is,conditions), as_dict=1, debug=True)
	for g in group_by_data:
		dep_added = []
		for m in master:
			if g.name == m.get(field_is):
				if g.name not in dep_added:
					data.append({field_is: "<b>"+str(g.name)+"</b>"})
				row = {}
				row.update(m)
				row["total_absent"] = frappe.db.sql("""select count(*) from 
					`tabAttendance` c where status = 'Absent' and docstatus = 1 and employee = '{}'
					""".format(m.employee))[0][0] or 0
				lates_detail = frappe.db.sql("""select count(*) as lates, 
					SEC_TO_TIME(SUM(TIME_TO_SEC(late_entry_time))) as late_hrs from 
					`tabAttendance` c where late_entry = 1 and docstatus = 1 and employee = '{}'
					""".format(m.employee))
				row["total_lates"] = 0
				row["total_late_hrs"] = "00:00:00"
				row["department"] = ""
				row["cost_center"] = ""
				if lates_detail:
					row["total_lates"] = lates_detail[0][0] or 0
					row["total_late_hrs"] = correct_time(lates_detail[0][1]) or "00:00:00"
				for d in details:
					if d.employee == m.employee:
						value_in = d.late_entry_time
						if not value_in:
							value_in = value_in_details.get(d.status)
						row[frappe.scrub("date"+str(d.date))] = value_in
				data.append(row)
	return columns, data

def correct_time(time):
	total_time = str(time)
	if " " in total_time:
		days = int(total_time.split(" ")[0])
		time = total_time.split(" ")[2].split(":")
		hh = time[0]
		mm = time[1]
		ss = time[2]
		new_hh = (int(days)*24)+int(hh)
		total_time = str(new_hh).zfill(2)+":"+str(mm).zfill(2)+":"+str(ss).zfill(2)
	return total_time

def get_column(filters,conditions):
	group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
	field_is = group_by_detail.get(filters.get("group_by"))

	columns = [
		# {
		# 	"fieldname": "employee_name",
		# 	"label": _("Employee Name"),
		# 	"fieldtype": "Data",
		# 	"options": "",
		# 	"width": 180
		# },
		{
			"fieldname": field_is,
			"label": _(filters.get("group_by")),
			"fieldtype": "Link",
			"options": filters.get("group_by"),
			"width": 200
		},
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
		}]

	today = getdate(filters.get("from_date"))
	while getdate(filters.get("to_date")) >= getdate(today):
		fieldname = "date"+str(today)
		label = str(getdate(today).day)+"-"+str(getdate(today).month)
		columns.append({
			"fieldname": frappe.scrub(fieldname),
			"label": _(label),
			"fieldtype": "Data",
			"width": 90
		})
		
		today = pd.to_datetime(today) + pd.DateOffset(days=1)
		today = today.strftime('%Y-%m-%d')

	columns.append({
			"fieldname": "total_absent",
			"label": _("Total Abs"),
			"fieldtype": "Int",
			"width": 90
		})

	columns.append({
			"fieldname": "total_lates",
			"label": _("Total Lates"),
			"fieldtype": "Int",
			"width": 90
		})

	columns.append({
			"fieldname": "total_late_hrs",
			"label": _("Total Late Hrs"),
			"fieldtype": "Data",
			"width": 90
		})

	return columns


def get_details(conditions="", filters={}):
	details = {}
	data = frappe.db.sql("""select e.name as employee, e.employee_name, attendance_date as date, time_in, time_out, total_time, c.employee_shift as time_table,
			e.branch , e.department, e.cost_center, e.designation, late_entry_time, early_exit_time, c.status, overtime_time
			from `tabEmployee` e inner join `tabAttendance` c on c.employee = e.name 
			where e.status = 'Active' and c.docstatus = 1 {} order by e.employee_name,attendance_date
		""".format(conditions), as_dict=1)
	return data

def get_conditions(filters,sales_order=None):
	# students_list = []
	# conditions = " and p.status = 'Completed'"
	conditions = ""
	if sales_order:
		conditions += " and e.name = '{}'".format(sales_order)
	if filters.get("department"):
		conditions += " and e.department = '{}'".format(filters.get("department"))
	if filters.get("designation"):
		conditions += " and e.designation = '{}'".format(filters.get("designation"))

	if filters.get("employee"):
		conditions += " and e.name = '{}'".format(filters.get("employee"))

	if filters.get("cost_center"):
		conditions += " and e.cost_center = '{}'".format(filters.get("cost_center"))


	if filters.get("branch"):
		conditions += " and e.branch = '{}'".format(filters.get("branch"))

	if filters.get("shift"):
		conditions += " and c.shift = '{}'".format(filters.get("shift"))

	if filters.get("employee"):
		conditions += " and e.name = '{}'".format(filters.get("employee"))

	if filters.get("from_date"):
		conditions += " and attendance_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and attendance_date <= '{}'".format(filters.get("to_date"))

	return conditions
