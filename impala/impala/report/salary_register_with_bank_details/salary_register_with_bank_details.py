# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def execute(filters=None):
	if not filters:
		filters = {}

	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))

	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []

	earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
	columns = get_columns(earning_types, ded_types)

	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

	doj_map = get_employee_doj_map()

	data = []
	if filters.get("payroll_category"):
		for ss in salary_slips:
			row = {
				"salary_slip_id": ss.name,
				"employee": ss.employee,
				"employee_name": ss.employee_name,
				"data_of_joining": doj_map.get(ss.employee),
				"branch": ss.branch,
				"department": ss.department,
				"designation": ss.designation,
				"company": ss.company,
				"start_date": ss.start_date,
				"end_date": ss.end_date,
				"leave_without_pay": ss.leave_without_pay,
				"payment_days": ss.payment_days,
				"currency": currency or company_currency,
				"total_loan_repayment": ss.total_loan_repayment,
				"branch_code": ss.branch_code,
				"bank_code": ss.bank_code,
				"bank_ac_no": ss.bank_ac_no,
				"salary_mode": ss.salary_mode,
				"bank_name": ss.bank_name,
			}

			update_column_width(ss, columns)

			for e in earning_types:
				row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})

			for d in ded_types:
				row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})

			if currency == company_currency:
				row.update(
					{
						"gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
						"total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
						"net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
					}
				)

			else:
				row.update(
					{"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
				)

			data.append(row)

	return columns, data


def get_earning_and_deduction_types(salary_slips):
	salary_component_and_type = {_("Earning"): [], _("Deduction"): []}

	for salary_compoent in get_salary_components(salary_slips):
		component_type = get_salary_component_type(salary_compoent[0])
		salary_component_and_type[_(component_type)].append(salary_compoent[0])

	return sorted(salary_component_and_type[_("Earning")]), sorted(
		salary_component_and_type[_("Deduction")]
	)


def update_column_width(ss, columns):
	if ss.branch is not None:
		columns[3].update({"width": 120})
	if ss.department is not None:
		columns[4].update({"width": 120})
	if ss.designation is not None:
		columns[5].update({"width": 120})
	if ss.leave_without_pay is not None:
		columns[9].update({"width": 120})


def get_columns(earning_types, ded_types):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": -1,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": -1,
		},
		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 120,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": _("Leave Without Pay"),
			"fieldname": "leave_without_pay",
			"fieldtype": "Float",
			"width": 50,
		},
		{
			"label": _("Payment Days"),
			"fieldname": "payment_days",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Net Pay"),
			"fieldname": "net_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Data",
			"options": "Currency",
			"hidden": 1,
		},
	]

	columns.extend([
		{
			"fieldname": "bank_name",
			"fieldtype": "data",
			"label": _("Bank Name"),
			"width": 260,
		},
		{
			"fieldname": "bank_code",
			"fieldtype": "data",
			"label": _("Bank Code/Swift Code"),
			"width": 120,
		},
		{
			"fieldname": "branch_code",
			"fieldtype": "data",
			"label": _("Branch Code"),
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


		])
	return columns


def get_salary_components(salary_slips):
	return (
		frappe.qb.from_(salary_detail)
		.where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
		.select(salary_detail.salary_component)
		.distinct()
	).run(as_list=True)


def get_salary_component_type(salary_component):
	return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    employee = frappe.qb.DocType("Employee")
    query = (
        frappe.qb.from_(salary_slip)
        .inner_join(employee)
        .on(salary_slip.employee == employee.name)
        .select(
            salary_slip.star,
            employee.bank_name,
            employee.bank_ac_no,
            employee.salary_mode,
            employee.branch_code,
            employee.bank_code,
            employee.payroll_category,  # Add payroll_category to the select statement
        )
    )

    if filters.get("docstatus"):
        query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

    if filters.get("from_date"):
        query = query.where(salary_slip.start_date >= filters.get("from_date"))

    if filters.get("to_date"):
        query = query.where(salary_slip.end_date <= filters.get("to_date"))

    if filters.get("company"):
        query = query.where(salary_slip.company == filters.get("company"))

    if filters.get("employee"):
        query = query.where(salary_slip.employee == filters.get("employee"))

    if filters.get("currency") and filters.get("currency") != company_currency:
        query = query.where(salary_slip.currency == filters.get("currency"))

    if filters.get("payroll_category"):  # Add condition for payroll_category
        query = query.where(employee.payroll_category == filters.get("payroll_category"))

    salary_slips = query.run(as_dict=1)

    return salary_slips or []



def get_employee_doj_map():
	employee = frappe.qb.DocType("Employee")

	result = (frappe.qb.from_(employee).select(employee.name, employee.date_of_joining)).run()

	return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, component_type):

	salary_slips = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == component_type))
		.select(
			salary_detail.parent,
			salary_detail.salary_component,
			salary_detail.amount,
			salary_slip.exchange_rate,
		)
	).run(as_dict=1)

	ss_map = {}
	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map
