# Copyright (c) 2023, Aqiq Hrm and contributors
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
	columns = get_column(filters,conditions)
	data = []
	master = get_details(conditions,filters)
	employee_condition = get_employee_conditions(filters)
	employees = frappe.db.sql("select name, employee_name, department from `tabEmployee` where status='Active' %s"%employee_condition, as_dict=True)
	
	emp_overtime_cond = ""
	if filters.from_date:
		emp_overtime_cond += " and eovt.payroll_date >= '%s'"%filters.from_date
		emp_overtime_cond += " and eovt.payroll_date <= '%s'"%filters.to_date

	if master and employees:
		for emp in employees:
			row = {}
			row["name"] = emp.name
			row["employee_name"] = emp.employee_name
			row["department"] = emp.department
			row["present"] = 0
			row["absent"] = 0
			row["weekend"] = 0
			row["holiday"] = 0
			row["on_leave"] = 0
			row["early_exit"] = 0
			row["late_entry"] = 0
			row["half_day"] = 0
			row["manual_overtime_in_minutes"] = 0
			row["fixed_overtime_in_minutes"] = 0
			row["holiday_overtime_in_minutes"] = 0
			total_early_exit_time = 0.0
			total_late_entry_time = 0.0
			total_late_exit_wo_overtime = 0.0
			total_total_time = 0.0
			total_overtime_time = 0.0

			for i in master:
				if i.name == emp.name and i.status == 'Present':
					row["present"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Absent':
					row["absent"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Weekend':
					row["weekend"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Holiday':
					row["holiday"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'On Leave':
					row["on_leave"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Early Exit':
					row["early_exit"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Late Entry':
					row["late_entry"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				if i.name == emp.name and i.status == 'Half Day':
					row["half_day"] = i.get("count")
					total_early_exit_time += i.get("early_exit_time")
					total_late_entry_time += i.get("late_entry_time")
					total_late_exit_wo_overtime += i.get("late_exit_wo_overtime")
					total_total_time += i.get("total_time")
					total_overtime_time += i.get("overtime_time")

				emp_ovt_query = frappe.db.sql("""
						SELECT eovt.salary_component, SUM(eovt_details.overtime_in_mins) AS overtime_in_mins
						FROM  `tabEmployee Overtime` eovt
						RIGHT JOIN `tabOvertime Details` eovt_details ON eovt.name=eovt_details.parent
						WHERE eovt.docstatus=1 and eovt_details.employee='{}' {} GROUP BY eovt.salary_component ORDER BY payroll_date, salary_component
					""".format(emp.name, emp_overtime_cond), as_dict=True)

				for eovt in emp_ovt_query:			
					if eovt.salary_component == 'Manual OverTime':
						row["manual_overtime_in_minutes"] = eovt.overtime_in_mins or 0

					if eovt.salary_component == 'Fixed OverTime':
						row["fixed_overtime_in_minutes"] = eovt.overtime_in_mins or 0

					if eovt.salary_component == 'Holiday OverTime':
						row["holiday_overtime_in_minutes"] = eovt.overtime_in_mins or 0

			row["early_exit_time"] = correct_time(total_early_exit_time)
			row["late_entry_time"] = correct_time(total_late_entry_time)
			row["late_exit_wo_overtime"] = correct_time(total_late_exit_wo_overtime)
			row["total_time"] = correct_time(total_total_time)
			row["overtime_time"] = correct_time(total_overtime_time)
			
			data.append(row)

	return columns, data


# def correct_time(time_in_secs):
# 	formated_time = time.strftime('%H:%M:%S', time.gmtime(time_in_secs))
# 	return formated_time

def correct_time(time_in_secs):
    # Ensure time_in_secs is an integer
    total_seconds = int(time_in_secs)  # Convert to an integer

    # Calculate the number of days, hours, minutes, and seconds
    # days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(total_seconds, 3600)       # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)

    # Use string formatting with leading zeros
    formatted_time = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    return formatted_time


def get_column(filters,conditions):
	group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
	field_is = group_by_detail.get(filters.get("group_by"))

	columns = [
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
			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "present",
			"label": _("Present"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'Present' else 0
		},
		{
			"fieldname": "absent",
			"label": _("Absent"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'Absent' else 0
		},
		{
			"fieldname": "half_day",
			"label": _("Half Day"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'Half Day' else 0
		},
		{
			"fieldname": "on_leave",
			"label": _("On Leave"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'On Leave' else 0
		},
		{
			"fieldname": "holiday",
			"label": _("Holiday"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'Holiday' else 0
		},
		{
			"fieldname": "weekend",
			"label": _("Weekend"),
			"fieldtype": "Int",
			"width": 100,
			"hidden": 1 if filters.status and filters.status != 'Weekend' else 0
		},
		# {
		# 	"fieldname": "late_entry",
		# 	"label": _("Late Entry"),
		# 	"fieldtype": "Int",
		# 	"width": 100,
		# 	"hidden": 1 if filters.status and filters.status != 'Late Entry' else 0
		# },
		# {
		# 	"fieldname": "early_exit",
		# 	"label": _("Early Exit"),
		# 	"fieldtype": "Int",
		# 	"width": 100,
		# 	"hidden": 1 if filters.status and filters.status != 'Early Exit' else 0
		# },
		# {

		# 	"fieldname": "early_entry",
		# 	"label": _("Early Entry"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
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
		# {
		# 	"fieldname": "late_exit",
		# 	"label": _("Late Exit"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		{
			"fieldname": "late_exit_wo_overtime",
			"label": _("Late Exit w/o Overtime"),
			"fieldtype": "Data",
			"width": 80
		},
		# {
		# 	"fieldname": "clocked_hours",
		# 	"label": _("Clocked Hours"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# },
		{
			"fieldname": "total_time",
			"label": _("Worked Hours"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "overtime_time",
			"label": _("Overtime Time"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "manual_overtime_in_minutes",
			"label": _("Manual overtime in minutes"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "holiday_overtime_in_minutes",
			"label": _("Holiday overtime in minutes"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "fixed_overtime_in_minutes",
			"label": _("Fixed overtime in minutes"),
			"fieldtype": "Int",
			"width": 80
		},


	]

	return columns

def get_details(conditions="", filters={}):
	details = {}
	data = frappe.db.sql("""select e.name, e.employee_name, c.status, COUNT(c.name) as count,
	 		IFNULL(SUM(TIME_TO_SEC(c.early_exit_time)), 0) as early_exit_time,
	 		IFNULL(SUM(TIME_TO_SEC(c.late_entry_time)), 0) as late_entry_time,
	 		IFNULL(SUM(TIME_TO_SEC(c.late_exit_wo_overtime)), 0) as late_exit_wo_overtime,
	 		IFNULL(SUM(TIME_TO_SEC(c.total_time)), 0) as total_time,
	 		IFNULL(SUM(TIME_TO_SEC(c.overtime_time)), 0) as overtime_time
			from `tabEmployee` e inner join `tabAttendance` c on c.employee = e.name
			where e.status = 'Active' and c.docstatus = 1 {} group by e.employee, c.status order by e.employee_name, c.status
		""".format(conditions), as_dict=1)
	return data



def get_employee_conditions(filters):
	conditions = ""
	if filters.get("department"):
		conditions += " and department = '{}'".format(filters.get("department"))
	if filters.get("designation"):
		conditions += " and designation = '{}'".format(filters.get("designation"))

	if filters.get("employee"):
		conditions += " and name = '{}'".format(filters.get("employee"))

	if filters.get("cost_center"):
		conditions += " and cost_center = '{}'".format(filters.get("cost_center"))

	if filters.get("branch"):
		conditions += " and branch = '{}'".format(filters.get("branch"))


	return conditions



def get_conditions(filters):
	conditions = ""
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

	if filters.get("from_date"):
		conditions += " and attendance_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and attendance_date <= '{}'".format(filters.get("to_date"))

	return conditions
