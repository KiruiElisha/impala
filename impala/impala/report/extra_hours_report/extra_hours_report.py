# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta

def execute(filters=None):
	if not filters:
		filters = {}

	conditions = get_conditions(filters)
	columns = get_column(filters,conditions)
	data = []

	group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
	group_by_data = frappe.db.sql("select name from `tab{}` where is_group = 0 and disabled = 0".format(filters.get("group_by")), as_dict=1)
	field_is = group_by_detail.get(filters.get("group_by"))
	for g in group_by_data:
		# frappe.msgprint(str(g))
		data_sum = frappe.db.sql(""" select c.employee, SEC_TO_TIME(SUM(TIME_TO_SEC(total_time))) AS total_time , 
			SEC_TO_TIME(SUM(TIME_TO_SEC(overtime_time))) AS overtime_time, c.employee_name
			  from `tabAttendance` c inner join `tabEmployee` e on e.name = c.employee
			  where c.docstatus =1 {} and overtime = 1 and e.{} = '{}' group by 1 order by c.attendance_date""".format(conditions, field_is, g.name), as_dict=1, debug=True)
		if data_sum:
			data.append({field_is: "<b>"+str(g.name)+"</b>"})
		for d in data_sum:
			conditions = get_conditions(filters, d.employee)
			master = get_details(conditions,filters)
			if master:
				# details = get_details(conditions,filters)
				# data.append({"department":"<b>"+str(d.employee_name)+" | "+str(d.employee)+"</b>"})
				for i in master:
					row = {}
					row.update(i)
					row['employee_name'] = i.get("employee_name")
					row['department'] = ""
					row['cost_center'] = ""
					row['designation'] = i.get("designation")
					row['branch'] = i.get("branch")
					row['date'] = i.get("date")
					row['status'] = i.get("status")
					date = frappe.utils.getdate(i.get("date"))
					row['day'] = date.strftime("%A")
					data.append(row)
				total = {"name": "<b class='row-total'> Total </b>"}
				total.update({"total_time": correct_time(d.total_time), "overtime_time": correct_time(d.overtime_time)})
				data.append(total)
				data.append({})

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
			"fieldname": "name",
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
			"width": 90
		},
		{
			"fieldname": "time_table",
			"label": _("Time Table"),
			"fieldtype": "Link",
			"options": "Time Table",
			"width": 100
		},
		{

			"fieldname": "start_time",
			"label": _("Start Time"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "end_time",
			"label": _("End Time"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "time_in",
			"label": _("Arrival Time"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "time_out",
			"label": _("Dep. Time"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "total_time",
			"label": _("Work Hours"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "overtime_time",
			"label": _("Overtime"),
			"fieldtype": "Data",
			"width": 80
		},
	]

	return columns


def get_details(conditions="", filters={}):
	details = {}
	data = frappe.db.sql("""select e.name, e.employee_name, attendance_date as date, time_in, time_out, total_time, c.employee_shift as time_table,
			tt.start_time, tt.end_time,
			e.branch , e.department, e.cost_center, e.designation, late_entry_time, early_exit_time, c.status, overtime_time
			from `tabEmployee` e inner join `tabAttendance` c on c.employee = e.name 
			inner join `tabTime Table` tt on c.employee_shift = tt.name
			where e.status = 'Active' and overtime = 1 and c.docstatus = 1 {} order by e.employee_name,attendance_date
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
