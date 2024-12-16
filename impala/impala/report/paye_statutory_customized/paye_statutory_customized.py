# Copyright (c) 2024, Aqiq and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import cstr

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
	overtime_earnings = ["Manual OverTime", "Holiday OverTime", "Fixed OverTime", "Overtime"]
	earning_types.extend(overtime_earnings)
	columns = get_columns(earning_types, ded_types)

	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

	doj_map = get_employee_doj_map()

	data = []
	for ss in salary_slips:
		row = {
			"salary_slip_id": ss.name,
			"national_id": ss.national_id,
			"employee": ss.employee,
			"last_name": ss.last_name,
			"first_name": ss.first_name,
			"middle_name": ss.middle_name,
			"employee_name": (ss.first_name or "") + " " + (ss.middle_name or ""),
			"employee_pin": ss.employee_pin,
			"nssf_number": ss.nssf_number,
			"nssf_last_name": ss.nssf_last_name,
			"nssf_name": ss.nssf_name,
			"nhif_number": ss.nhif_number,
			"data_of_joining": doj_map.get(ss.employee),
			"branch": ss.branch,
			"department": ss.department,
			"designation": ss.designation,
			"company": ss.company,
			"start_date": ss.start_date,
			"residential_status":ss.residential_status,
			"end_date": ss.end_date,
			"leave_without_pay": ss.leave_without_pay,
			"payment_days": ss.payment_days,
			"currency": currency or company_currency,
			"total_loan_repayment": ss.total_loan_repayment,
			"type_of_employee": ss.type_of_employee,
			"payroll_category":ss.payroll_category
		}

		update_column_width(ss, columns)

		for e in earning_types:
			row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})
		over_time_allowance = sum(ss_earning_map.get(ss.name, {}).get(earning, 0) for earning in overtime_earnings)
		row.update({"over_time_allowance": over_time_allowance})
		manual_overtime = sum(ss_earning_map.get(ss.name, {}).get(earning, 0) for earning in ["Manual OverTime"])
		row.update({"manual_overtime": manual_overtime})
		holiday_overtime = sum(ss_earning_map.get(ss.name, {}).get(earning, 0) for earning in ["Holiday OverTime"])
		row.update({"holiday_overtime": holiday_overtime})
		fixed_overtime = sum(ss_earning_map.get(ss.name, {}).get(earning, 0) for earning in ["Fixed OverTime"])
		row.update({"fixed_overtime": fixed_overtime})
		total_rtis = ss_ded_map.get(ss.name, {}).get("Total RTI", 0)
		total_rtiss=abs(total_rtis)
		row.update({"total_rtiss": abs(total_rtiss)})
		basic_salary = ss_earning_map.get(ss.name, {}).get("Basic", 0)
		absent = ss_ded_map.get(ss.name, {}).get("Absent", 0)
		basics=basic_salary-absent
		row.update({"basics": basics})


		for d in ded_types:
			row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})
		if 'insurance_relief' in row:
			insurance_value = row.get('insurance_relief')
			if insurance_value is None:
				row['insurance_relief'] = 0

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
			"label": _("PIN of Employee"),
			"fieldname": "employee_pin",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Name of Employee"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		
		{
			"label": _("Residential Status"),
			"fieldname": "residential_status",
			"fieldtype": "Data",
			"width": 140,
		},
		{
				"label": _("Type of Employee"),
				"fieldname": "type_of_employee",
				"fieldtype": "Data",
				"width": 120
		},
		{
			"label": _("Basic Salary"),
			"fieldname": "basics",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("House Allowance"),
			"fieldname": "house_allowance",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Transport Allowance"),
			"fieldname": "leave_travel_allowance",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},{
			"label": _("Leave Pay"),
			"fieldname": "leave_encashment",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Over Time Allowance"),
			"fieldname": "over_time_allowance",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		 {
		 	"label": _("AHL Levy"),
		 	"fieldname": "ahl_levy_employee",
		 	"fieldtype": "Currency",
		 	"options": "currency",
		 	"width": 120,
		 },
		 {
		 	"label": _("AHL Relief"),
		 	"fieldname": "ahl_relief",
		 	"fieldtype": "Currency",
		 	"options": "currency",
		 	"width": 120,
		 },
		# {
		# 	"label": _("Transport Allowance"),
		# 	"fieldname": "transport_allowance",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Telephone Allowance"),
		# 	"fieldname": "telephone_allowance",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Bonus"),
		# 	"fieldname": "bonus",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Other Earning"),
		# 	"fieldname": "other_earning",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Notice Pay"),
		# 	"fieldname": "notice_pay",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Commission"),
		# 	"fieldname": "commission",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# # {
		# # 	"label": _("Night Shift Allowance"),
		# # 	"fieldname": "night_shift_allowance",
		# # 	"fieldtype": "Currency",
		# # 	"options": "currency",
		# # 	"width": 120,
		# # },
		# {
		# 	"label": _("Gratuity/Service"),
		# 	"fieldname": "gratuity/service",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Telephone Benefit"),
		# 	"fieldname": "telephone_benefit",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# # {
		# 	"label": _("Personal Relief"),
		# 	"fieldname": "personal_relief",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("NHIF Relief"),
		# 	"fieldname": "nhif_relief",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# # {
		# # 	"label": _("NITA"),
		# # 	"fieldname": "nita",
		# # 	"fieldtype": "Currency",
		# # 	"options": "currency",
		# # 	"width": 120,
		# # },
		# {
		# 	"label": _("Gross Salary"),
		# 	"fieldname": "gross_salary",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Total Benefits"),
		# 	"fieldname": "total_benefits",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Total Reliefs"),
		# 	"fieldname": "total_reliefs",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Paid Casual Leave"),
		# 	"fieldname": "paid_casual_leave",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Manual Shift Attendance Bonus"),
		# 	"fieldname": "manual_shift_attendance_bonus",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Net Personal Relief"),
		# 	"fieldname": "net_personal_relief",
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 120,
		# },
		{
			"label": _("Merit"),
			"fieldname": "merit",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Absent Refund"),
			"fieldname": "absent_refund",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Director's Fee"),
			"fieldname": "director_fee",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Lump Sum Payment if any"),
			"fieldname": "lump_sum_payment_if_any",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Other Allowance"),
			"fieldname": "night_shift_allowance",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Arrear"),
			"fieldname": "arrear",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Absent"),
			"fieldname": "absent",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("total Cash Pay (A)"),
			"fieldname": "total_cash_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Value Of Car Benefit"),
			"fieldname": "value_of_car_benefit",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Other Non Cash Benefits"),
			"fieldname": "other_non_cash_benefits",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Total Non Cash Pay"),
			"fieldname": "total_non_cash_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Global Income"),
			"fieldname": "global_income",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Type Of Housing"),
			"fieldname": "type_of_housing",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Rent Of house/Market Value"),
			"fieldname": "rent_of_house/market_value",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Computed Rent of House"),
			"fieldname": "computed_rent_of_house",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Rent Recovered From Employee"),
			"fieldname": "rent_recovered_from_employee",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Net Value of Housing"),
			"fieldname": "net_value_of_housing",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},{
			"label": _("Total Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("30% Of cash pay"),
			"fieldname": "cash_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Actual Contributions"),
			"fieldname": "total_rtiss",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Permissible limit"),
			"fieldname": "permissible_limit",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Mortgage interest"),
			"fieldname": "mortgage_interest",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Deposit on Home Ownership"),
			"fieldname": "deposit_on_home_ownership",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Amount of benefit"),
			"fieldname": "amount_of_benefit",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Taxable Pay"),
			"fieldname": "Taxable_income",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Monthly Personal Relief"),
			"fieldname": "personal_relief",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Amount of insurance relief"),
			"fieldname": "insurance_relief",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Paye Tax"),
			"fieldname": "paye_tax",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Self Assessed PAYE"),
			"fieldname": "paye",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}

	]
	

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
            employee.national_id,
            employee.last_name,
            employee.first_name,
            employee.middle_name,
            employee.employee_pin,
            employee.nssf_number,
            employee.nhif_number,
            employee.type_of_employee,
            employee.nssf_last_name,
            employee.residential_status,
            employee.nssf_name,
            employee.payroll_category
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
    
    if filters.get("unionized"):
        query = query.where(employee.unionized == filters.get("unionized"))
    
    # Fetching Payroll Categories based on current user and static value
    payroll_categories = frappe.db.get_list("User Permission",
                                            filters={'user': frappe.session.user,
                                                     'allow': "Your Static Payroll Category"},
                                            fields=["for_value"])
    if payroll_categories:
        payroll_categories = [p['for_value'] for p in payroll_categories]
        # Filtering based on fetched Payroll Categories
        query = query.where(employee.payroll_category.in_(payroll_categories))

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
			salary_slip.exchange_rate
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
