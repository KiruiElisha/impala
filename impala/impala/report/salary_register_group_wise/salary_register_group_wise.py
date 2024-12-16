# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

import erpnext


def execute(filters=None):
	if not filters: filters = {}
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips: return [], []

	columns, earning_types, ded_types = get_columns(salary_slips, filters)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	doj_map = get_employee_doj_map()

	data = []
	if filters.get("payroll_category"):
		group_by_detail = {"Department": "department", "Cost Center": "cost_center"}
		# group_by_data = frappe.db.sql("select {} from `tabSalary Slip` where is_group = 0 and disabled = 0".format(filters.get("group_by")), as_dict=1)
		grand_total = {"field_is": 0, 
				"Salary Slip ID":"","Employee":"","Employee Name":"","Date of Joining":"","Branch":"",
				"Designation":"","Company":"","Start Date":"","End Date":"","Leave Without Pay":0,
				"Payment Days":0, 
			}
		group_by_data = []
		total_employees = 0
		field_is = group_by_detail.get(filters.get("group_by"))
		for d in salary_slips:
			group_by_field = d.get(field_is)
			if group_by_field not in group_by_data:
				group_by_data.append(group_by_field)
		for i in group_by_data:
			data.append({field_is: "<b>"+str(i)+"</b>"})
			group_total = {"field_is": 0, 
				"Salary Slip ID":"","Employee":"","Employee Name":"","Date of Joining":"","Branch":"",
				"Designation":"","Company":"","Start Date":"","End Date":"","Leave Without Pay":0,
				"Payment Days":0,
			}
			employees = 0
			for ss in salary_slips:
				group_by_field = ss.get(field_is)
				if group_by_field == i:
					group_total["field_is"] += 1
					grand_total["field_is"] += 1
					row = ["",ss.name, ss.employee, ss.employee_name, doj_map.get(ss.employee), ss.branch, ss.designation,
						ss.company, ss.start_date, ss.end_date, ss.leave_without_pay, ss.payment_days]

					# if ss.branch is not None: columns[3] = columns[3].replace('-1','120')
					# # if ss.department is not None: columns[4] = columns[4].replace('-1','120')
					# if ss.designation is not None: columns[5] = columns[3].replace('-1','120')
					# if ss.leave_without_pay is not None: columns[9] = columns[8].replace('-1','130')

					for e in earning_types:
						if not group_total.get(e):
							group_total[e] = 0
						group_total[e] += flt(ss_earning_map.get(ss.name, {}).get(e))
						if not grand_total.get(e):
							grand_total[e] = 0
						grand_total[e] += flt(ss_earning_map.get(ss.name, {}).get(e))
						row.append(ss_earning_map.get(ss.name, {}).get(e))

					if not group_total.get("Gross Pay"):
						group_total["Gross Pay"] = 0
					if not grand_total.get("Gross Pay"):
						grand_total["Gross Pay"] = 0
					if currency == company_currency:
						row += [flt(ss.gross_pay) * flt(ss.exchange_rate)]
						group_total["Gross Pay"] += flt(ss.gross_pay) * flt(ss.exchange_rate)
						grand_total["Gross Pay"] += flt(ss.gross_pay) * flt(ss.exchange_rate)
					else:
						row += [ss.gross_pay]
						group_total["Gross Pay"] += ss.gross_pay
						grand_total["Gross Pay"] += ss.gross_pay

					for d in ded_types:
						if not group_total.get(d):
							group_total[d] = 0
						group_total[d] += flt(ss_ded_map.get(ss.name, {}).get(d))
						if not grand_total.get(d):
							grand_total[d] = 0
						grand_total[d] += flt(ss_ded_map.get(ss.name, {}).get(d))
						row.append(ss_ded_map.get(ss.name, {}).get(d))

					if not group_total.get("Loan Repayment"):
						group_total["Loan Repayment"] = 0
					group_total["Loan Repayment"] += ss.total_loan_repayment
					if not grand_total.get("Loan Repayment"):
						grand_total["Loan Repayment"] = 0
					grand_total["Loan Repayment"] += ss.total_loan_repayment
					row.append(ss.total_loan_repayment)

					if not group_total.get("Deductions"):
						group_total["Deductions"] = 0

					if not group_total.get("Net Pay"):
						group_total["Net Pay"] = 0

					if not grand_total.get("Deductions"):
						grand_total["Deductions"] = 0

					if not grand_total.get("Net Pay"):
						grand_total["Net Pay"] = 0

					if currency == company_currency:
						row += [flt(ss.total_deduction) * flt(ss.exchange_rate), flt(ss.net_pay) * flt(ss.exchange_rate)]
						group_total["Deductions"] += flt(ss.total_deduction) * flt(ss.exchange_rate)
						group_total["Net Pay"] += flt(ss.net_pay) * flt(ss.exchange_rate)
						grand_total["Deductions"] += flt(ss.total_deduction) * flt(ss.exchange_rate)
						grand_total["Net Pay"] += flt(ss.net_pay) * flt(ss.exchange_rate)
					else:
						row += [ss.total_deduction, ss.net_pay]
						group_total["Deductions"] += ss.total_deduction
						group_total["Net Pay"] += ss.net_pay
						grand_total["Deductions"] += ss.total_deduction
						grand_total["Net Pay"] += ss.net_pay
					row.append(currency or company_currency)
					group_total["Currency"] = ""
					grand_total["Currency"] = ""
					data.append(row)
					# frappe.msgprint(str(len(row)))
			# for total in group_total.items():
			# data.append(group_total)
			row = []
			for key,val in group_total.items():
				if key == "field_is":
					val = "<b>Employees "+str(val)+"</b>"
				row.append(val)
			data.append(row)

		row = []
		for key,val in grand_total.items():
			if key == "field_is":
				val = "<b>Total Employees "+str(val)+"</b>"
			row.append(val)
		data.append(row)

	return columns, data

def get_columns(salary_slips, filters):
	"""
	columns = [
		_("Salary Slip ID") + ":Link/Salary Slip:150",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
		_("Date of Joining") + "::80",
		_("Branch") + ":Link/Branch:120",
		_("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120",
		_("Company") + ":Link/Company:120",
		_("Start Date") + "::80",
		_("End Date") + "::80",
		_("Leave Without Pay") + ":Float:130",
		_("Payment Days") + ":Float:120",
		_("Currency") + ":Link/Currency:80"
	]
	"""
	# group_by_detail = {"Department"}
	columns = [
		_(filters.get("group_by")) + ":Link/"+filters.get("group_by")+":150",_("Salary Slip ID") + ":Link/Salary Slip:150",_("Employee") + ":Link/Employee:120", _("Employee Name") + "::140",
		_("Date of Joining") + "::80", _("Branch") + ":Link/Branch:-1",
		_("Designation") + ":Link/Designation:120", _("Company") + ":Link/Company:120", _("Start Date") + "::80",
		_("End Date") + "::80", _("Leave Without Pay") + ":Float:50", _("Payment Days") + ":Float:120"
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Currency:120"] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
		[_("Loan Repayment") + ":Currency:120", _("Total Deduction") + ":Currency:120", _("Net Pay") + ":Currency:120"]

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("payroll_category"): conditions += " and payroll_category = %(payroll_category)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	return conditions, filters

def get_employee_doj_map():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_ded_map
