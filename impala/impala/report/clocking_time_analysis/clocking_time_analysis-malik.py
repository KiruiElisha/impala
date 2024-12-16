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
			  where c.docstatus =1 {} and e.{} = '{}' group by 1 order by c.attendance_date""".format(conditions, field_is, g.name), as_dict=1, debug=True)
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
					row["clocked_hours"] = "00:00:00"

					if row.get("time_in") and row.get("time_out"):
						p = datetime.strptime(str(row.get("time_out")), "%H:%M:%S").time()
						m = datetime.strptime(str(row.get("time_in")), "%H:%M:%S").time()
						diff = datetime.combine(date.today(), p) - datetime.combine(date.today(), m)
						if diff.days < 0:
							diff = timedelta(days=0, seconds=diff.seconds, microseconds=diff.microseconds)

						total_shift_hours = "23:59:59"
						if row.get("time_table"):
							total_shift_hours = frappe.db.get_value("Time Table", row.get("time_table"), "total_shift_hours")
						if datetime.strptime(str(diff), "%H:%M:%S") > datetime.strptime(str(total_shift_hours), "%H:%M:%S"):
							diff = total_shift_hours
						row["clocked_hours"] = diff

					data.append(row)
				total = {"name": "<b class='row-total'> Total </b>"}
				total.update({"total_time": correct_time(d.total_time)})
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

			"fieldname": "early_entry",
			"label": _("Early Entry"),
			"fieldtype": "Data",
			"width": 80
		},
		{

			"fieldname": "late_entry_time",
			"label": _("Late Arrival"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "early_exit_time",
			"label": _("Early Dep."),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "late_exit",
			"label": _("Late Exit"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "late_exit_wo_overtime",
			"label": _("Late Exit w/o Overtime"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "clocked_hours",
			"label": _("Clocked Hours"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "total_time",
			"label": _("Worked Hours"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "status",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 90
		},
	]

	return columns


def get_details(conditions="", filters={}):
	details = {}
	data = frappe.db.sql("""select e.name, e.employee_name, attendance_date as date, time_in, time_out, total_time, c.employee_shift as time_table,
			e.branch , e.department, e.cost_center, e.designation, late_entry_time, early_exit_time, c.status, overtime_time,
			early_entry,late_exit,late_exit_wo_overtime
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

	if filters.get("time_table"):
		conditions += " and c.employee_shift = '{}'".format(filters.get("time_table"))

	if filters.get("employee"):
		conditions += " and e.name = '{}'".format(filters.get("employee"))

	# if filters.get("status"):
	# 	if filters.get("status") not in ["Late Entry", "Early Exit"]:
	# 		conditions += " and c.status = %(status)s"
	# 	elif filters.get("status") == "Late Entry":
	# 		conditions += " and late_entry = 1"
	# 	elif filters.get("status") == "Early Exit":
	# 		conditions += " and early_exit = 1"


	# if filters.get("employee_name"):
	# 	conditions += " and e.employee_name like '%%{}%%'".format(filters.get("employee_name"))

	if filters.get("from_date"):
		conditions += " and attendance_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and attendance_date <= '{}'".format(filters.get("to_date"))
	# if filters.get("student"):
	# 	conditions += " and student = %(student)s"
	# if filters.get("student_group"):
	# 	conditions += " and student_group = %(student_group)s"
		# students = frappe.db.sql("select student from `tabStudent Group Student` where parent = %s and active = 1",(filters.get("student_group")))
		# if students:
		# 	for s in students:
		# 		students_list.append(s[0])

		# conditions += " and student in {}".format(tuple(students_list))

	return conditions
