# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import calendar
from datetime import datetime, date, timedelta
from frappe.utils import flt

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
		total_absents = 0
		# frappe.msgprint(str(g))
		data_sum = frappe.db.sql(""" select c.employee, count(c.name) as absents, c.employee_name
			  from `tabAttendance` c inner join `tabEmployee` e on e.name = c.employee
			  where c.docstatus =1 and c.status = "Absent" 
			  {} and e.{} = '{}' group by 1 order by c.attendance_date
			  """.format(conditions, field_is, g.name), as_dict=1, debug=True)
		if data_sum:
			data.append({field_is: "<b>"+str(g.name)+"</b>"})
		for d in data_sum:
			total_absents += flt(d.absents)
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
				total = {}
				total.update({"status": "Total Absence "+str(d.absents)})
				data.append(total)
				
		if data_sum:
			data.append({"status": str(g.name)+" Total Absent "+str(int(total_absents))})
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
			"width": 120
		},
		# {
		# 	"fieldname": "time_table",
		# 	"label": _("Time Table"),
		# 	"fieldtype": "Link",
		# 	"options": "Time Table",
		# 	"width": 100
		# },
		# 		{
		# 	"fieldname": "time_in",
		# 	"label": _("Arrival Time"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		# {
		# 	"fieldname": "time_out",
		# 	"label": _("Dep. Time"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		# {

		# 	"fieldname": "late_entry_time",
		# 	"label": _("Late Arrival"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		
		# {
		# 	"fieldname": "early_exit_time",
		# 	"label": _("Early Dep."),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		# {
		# 	"fieldname": "total_time",
		# 	"label": _("Clocked Hours"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		# {
		# 	"fieldname": "worked_hours",
		# 	"label": _("Worked Hours"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		{
			"fieldname": "status",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 250
		},
	]

	return columns


def get_details(conditions="", filters={}):
	details = {}
	data = frappe.db.sql("""select e.name, e.employee_name, attendance_date as date, time_in, time_out, total_time, c.employee_shift as time_table,
			e.branch , e.department, e.cost_center, e.designation, late_entry_time, early_exit_time, c.status, overtime_time
			from `tabEmployee` e inner join `tabAttendance` c on c.employee = e.name 
			where e.status = 'Active' and c.docstatus = 1 and c.status = "Absent" {} 
			order by e.employee_name,attendance_date
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