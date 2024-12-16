# Copyright (c) 2023, Aqiq and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import calendar
import datetime

def execute(filters=None):
	columns, data = get_columns(), []
	conditions = get_conditions(filters)
	# employee_list = frappe.db.get_list('Employee', {'status' : 'Active'}, ['name', 'employee_name', 'residential_status', 'employee_pin', 'type_of_employee'])
	employee_list = frappe.db.sql("""select e.name, e.employee_name, e.residential_status, e.employee_pin, e.type_of_employee
		from `tabEmployee` e inner join `tabSalary Slip` ss on ss.employee = e.name where ss.docstatus = 1 and e.status = 'Active'
		{}  group by 1 order by 1""".format(conditions), as_dict=1)
	
	for employee in employee_list:
		row = {}
		row['employee_pin'] = employee.employee_pin
		row['employee_name'] = employee.employee_name
		row['residential_status'] = employee.residential_status
		row['type_of_employee'] = employee.type_of_employee

		row['basic'] = 0
		row['house_allowance'] = 0
		row['trasnport_allowance'] = 0
		row['leave_pay'] = 0
		row['overtime_allowance'] = 0
		row['director_fees'] = 0
		row['lump_sum_payment_if_any'] = 0
		row["other_allowance"] = 0
		row['value_of_car_benefits'] = 0
		row['non_cash_benefit'] = 0
		row['global_income'] = 0
		row['type_of_housing'] = ""
		row['actual_contribution'] = 0
		row['mortgage_relief'] = 0
		row['deposit_on_home'] = 0
		row['monthly_personal_relief'] = 0
		row['amount_of_insurance_relief'] = 0
		row['self_assessed_paye'] = 0
		row['tax_payable']=0
		row['ahl_relief']=0
		salary_slips = frappe.db.get_list('Salary Slip', {'employee' : employee.name}, pluck='name')
		for slip in salary_slips:
			salary_slip_details = get_salary_details_for_employee(filters, conditions, employee.name, slip)
			if salary_slip_details:
				row["actual_contribution"] = 0.0
				for s in salary_slip_details:
					if s.earning_type == "Allowance":
						row["other_allowance"] += s.amount or 0.0
					elif s.earning_type == "Overtime":
						row["overtime_allowance"] += s.amount or 0.0
					elif s.earning_type=='Basic':
						if s.type == 'Earning':
							row['basic'] += s.amount or 0.0  # Add earning to basic
						elif s.type == 'Deduction':
							row['basic'] -= s.amount or 0.0
					elif s.salary_component=='House Allowance':
						row['house_allowance'] = s.amount
					elif s.salary_component=='Transport Allowance':
						row['trasnport_allowance'] = s.amount
					elif s.salary_component=='Leave Pay':
						row['leave_pay'] = s.amount
					elif s.salary_component=='Overtime Allowance':
						row['overtime_allowance'] = s.amount
					elif s.salary_component=='Director Fees':
						row['director_fees'] = s.amount
					elif s.salary_component=='Lump Sum Payment If Any':
						row['lump_sum_payment_if_any'] = s.amount
					# elif s.salary_component=='Other Allowance':
					# 	row['other_allowance'] = s.amount
					elif s.salary_component=='Total Cash Pay':
						row['total_cash_pay'] = s.amount
					elif s.salary_component=='Car Benefit':
						row['value_of_car_benefits'] = s.amount
					elif s.salary_component=='Non Cash Benefit':
						row['non_cash_benefit'] = s.amount
					elif s.salary_component=='Non Cash Benefit':
						row['total_non_cash_benefit'] = s.amount
					elif s.salary_component=='Type of Housing':
						row['type_of_housing'] = s.amount
					elif s.salary_component=='Rent of House':
						row['rent_of_house'] = s.amount
					elif s.salary_component=='Computed Rent of House':
						row['computed_rent_of_house'] = s.amount
					elif s.salary_component=='Rent Recovery From Employee':
						row['rent_recovery_from_employee'] = s.amount
					elif s.salary_component=='Net Value of Housing':
						row['net_value_of_housing'] = s.amount
					elif s.salary_component=='Total Gross Pay':
						row['total_gross_pay'] = s.amount
					elif s.salary_component=='30% Cash Pay':
						row['thirty_perc_cash_pay'] = s.amount
					elif s.salary_component in ('NSSF Tier 1', 'NSSF Tier 2', 'EMP Voluntary NSSF'):
						row['actual_contribution'] += s.amount
					elif s.salary_component=='Permissible Limit1':
						row['permissible_limit1'] = s.amount
					elif s.salary_component=='Mortgage':
						row['mortgage_relief'] = s.amount
					elif s.salary_component=='AHL Relief':
						row['ahl_relief'] = s.amount
					elif s.salary_component=='Amount of Benefit':
						row['amount_of_benefit'] = s.amount
					elif s.salary_component=='Tax Charged':
						row['taxable_pay'] = s.amount
					elif s.salary_component=='Personal Relief':
						row['monthly_personal_relief'] = s.amount
					elif s.salary_component=='Insurance Relief':
						row['amount_of_insurance_relief'] = s.amount
					elif s.salary_component=='Self Assessed PAYE':
						row['paye_tax'] = s.amount
					elif s.salary_component=='PAYE':
						row['self_assessed_paye'] = s.amount
					# elif s.salary_component=='PAYE':
					# 	row['paye_tax'] = s.amount
					# elif s.salary_component=='Self Assessed PAYE':
					# 	row['self_assessed_paye'] = s.amount
				data.append(row)

	return columns, data



def get_salary_details_for_employee(filters, conditions, employee, slip):

	return frappe.db.sql("""select sd.salary_component, sd.amount, 
		sc.earning_type,sc.type
		FROM `tabSalary Slip` ss 
		INNER JOIN `tabSalary Detail` sd on ss.name=sd.parent 
		INNER JOIN `tabSalary Component` sc on sc.name=sd.salary_component 
		WHERE ss.docstatus=1 and ss.name='%s' and ss.employee='%s' %s
		"""%(slip, employee, conditions), as_dict=True, debug=True)



def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and ss.company='{}'".format(filters.get("company"))
	if filters.get("employee"):
		conditions += " and ss.employee='{}'".format(filters.get("employee"))
	if filters.get("payroll_month") and filters.get("fiscal_year"):
		payroll_yr = filters.get("fiscal_year")
		payroll_month = filters.get("payroll_month")
		datetime_object = datetime.datetime.strptime(payroll_month, "%b")
		month_number = datetime_object.month
		month_end = datetime.date(int(payroll_yr), month_number+1, 1) - datetime.timedelta(days=1)
		month_end = month_end.strftime("%Y-%m-%d")
		month_number = "0"+str(month_number) if month_number<9 else str(month_number)
		month_start = str(payroll_yr) + "-" + month_number + "-" + "01"
		conditions += " and ss.start_date >='{}' AND ss.end_date<='{}'".format(month_start, month_end)

	if filters.get("from_date"):
		conditions += " and ss.posting_date>='{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and ss.posting_date<='{}'".format(filters.get("to_date"))
	return conditions
def get_columns():
	return [
		{
			'fieldname': 'employee_pin',
			'fieldtype': 'Data',
			'label': _('PIN of Employee'),
			'width': 180,
		},
		{
			'fieldname': 'employee_name',
			'fieldtype': 'Data',
			'label': _('Name of Employee'),
			'width': 200,
		},
		{
			'fieldname': 'residential_status',
			'fieldtype': 'Data',
			'label': _('Residential Status'),
			'width': 150,
		},
		{
			'fieldname': 'type_of_employee',
			'fieldtype': 'Data',
			'label': _('Type of Employee'),
			'width': 150,
		},
		{
			'fieldname': 'basic',
			'fieldtype': 'Currency',
			'label': _('Basic Salary'),
			'width': 150,
		},
		{
			'fieldname': 'house_allowance',
			'fieldtype': 'Currency',
			'label': _('House Allowance'),
			'width': 150,
		},
		{
			'fieldname': 'trasnport_allowance',
			'fieldtype': 'Currency',
			'label': _('Transport Allowance'),
			'width': 150,
		},
		{
			'fieldname': 'leave_pay',
			'fieldtype': 'Currency',
			'label': _('Leave Pay'),
			'width': 150,
		},
		{
			'fieldname': 'overtime_allowance',
			'fieldtype': 'Currency',
			'label': _('Over Time Allowance'),
			'width': 150,
		},
		{
			'fieldname': 'director_fees',
			'fieldtype': 'Currency',
			'label': _("Director's Fee"),
			'width': 150,
		},
		{
			'fieldname': 'lump_sum_payment_if_any',
			'fieldtype': 'Currency',
			'label': _('Lump Sum Payment if any'),
			'width': 150,
		},
		{
			'fieldname': 'other_allowance',
			'fieldtype': 'Currency',
			'label': _('Other Allowance'),
			'width': 150,
		},
		{
			'fieldname': 'total_cash_pay',
			'fieldtype': 'Currency',
			'label': _('total Cash Pay (A)'),
			'width': 150,
		},
		{
			'fieldname': 'value_of_car_benefits',
			'fieldtype': 'Currency',
			'label': _('Value Of Car Benefit'),
			'width': 150,
		},
		{
			'fieldname': 'non_cash_benefit',
			'fieldtype': 'Currency',
			'label': _('Other Non Cash Benefits'),
			'width': 150,
		},
		{
			'fieldname': 'total_non_cash_benefit',
			'fieldtype': 'Currency',
			'label': _('Total Non Cash Pay'),
			'width': 150,
		},
		{
			'fieldname': 'global_income',
			'fieldtype': 'Currency',
			'label': _('Global Income'),
			'width': 150,
		},
		{
			'fieldname': 'type_of_housing',
			'fieldtype': 'Currency',
			'label': _('Type Of Housing'),
			'width': 150,
		},
		{
			'fieldname': 'rent_of_house',
			'fieldtype': 'Currency',
			'label': _('Rent Of house/Market Value'),
			'width': 150,
		},
		{
			'fieldname': 'computed_rent_of_house',
			'fieldtype': 'Currency',
			'label': _('Computed Rent of House'),
			'width': 150,
		},
		{
			'fieldname': 'rent_recovery_from_employee',
			'fieldtype': 'Currency',
			'label': _('Rent Recovered From Employee'),
			'width': 150,
		},
		{
			'fieldname': 'net_value_of_housing',
			'fieldtype': 'Currency',
			'label': _('Net Value of Housing'),
			'width': 150,
		},
		{
			'fieldname': 'total_gross_pay',
			'fieldtype': 'Currency',
			'label': _('Total Gross Pay'),
			'width': 150,
		},
		{
			'fieldname': 'thirty_perc_cash_pay',
			'fieldtype': 'Currency',
			'label': _('30% Of cash pay'),
			'width': 150,
		},
		{
			'fieldname': 'actual_contribution',
			'fieldtype': 'Currency',
			'label': _('Actual Contributions'),
			'width': 150,
			"precision": None,
		},
		{
			'fieldname': 'permissible_limit1',
			'fieldtype': 'Currency',
			'label': _('Permissible limit'),
			'width': 150,
		},
		{
			'fieldname': 'mortgage_relief',
			'fieldtype': 'Currency',
			'label': _('Mortgage interest'),
			'width': 150,
		},
		{
			'fieldname': 'ahl_relief',
			'fieldtype': 'Currency',
			'label': _('AHL Relief'),
			'width': 150,
		},
		{
			'fieldname': 'amount_of_benefit',
			'fieldtype': 'Currency',
			'label': _('Amount of benefit'),
			'width': 150,
		},
		{
			'fieldname': 'taxable_pay',
			'fieldtype': 'Currency',
			'label': _('Taxable Pay'),
			'width': 150,
		},
		{
			'fieldname': 'tax_payable',
			'fieldtype': 'Currency',
			'label': _('Tax Payable'),
			'width': 150,
		},
		{
			'fieldname': 'monthly_personal_relief',
			'fieldtype': 'Currency',
			'label': _('Monthly Personal Relief'),
			'width': 150,
		},
		{
			'fieldname': 'amount_of_insurance_relief',
			'fieldtype': 'Currency',
			'label': _('Amount of insurance relief'),
			'width': 150,
		},
		{
			'fieldname': 'paye_tax',
			'fieldtype': 'Currency',
			'label': _('Paye Tax'),
			'width': 150,
		},
		{
			'fieldname': 'self_assessed_paye',
			'fieldtype': 'Currency',
			'label': _('Self Assessed PAYE'),
			'width': 150,
		},
	]
