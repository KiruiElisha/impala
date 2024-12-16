# Copyright (c) 2023, Aqiq and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import calendar
import datetime

def execute(filters=None):
	columns, data = get_columns(), []
	
	employee_list = frappe.db.get_list('Employee', {'status' : 'Active'}, ['name', 'employee_name', 'residential_status', 'employee_pin', 'type_of_employee'])
	
	for employee in employee_list:
		months_of_the_year = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		for month in months_of_the_year:
			conditions = ""
			if filters.get("company"):
				conditions += " and ss.company='{}'".format(filters.get("company"))
			if filters.get("employee"):
				conditions += " and ss.employee='{}'".format(filters.get("employee"))
			if month and filters.get("fiscal_year"):
				payroll_yr = filters.get("fiscal_year")
				datetime_object = datetime.datetime.strptime(month, "%B")
				month_number = datetime_object.month
				month_end = datetime.date(int(payroll_yr), month_number+1 if month_number<12 else 1, 1) - datetime.timedelta(days=1)
				month_end = month_end.strftime("%Y-%m-%d")
				month_number = "0"+str(month_number) if month_number<9 else str(month_number)
				month_start = str(payroll_yr) + "-" + month_number + "-" + "01"
				conditions += " and ss.posting_date >='{}' AND ss.posting_date<='{}'".format(month_start, month_end)

				row = {}
				row['month_name'] = month
				salary_slips = frappe.db.get_list('Salary Slip', {'employee' : 'HR-EMP-00001', 'posting_date' : ['between', [month_start, month_end]]}, pluck='name', debug=False)
				
				for slip in salary_slips:
					salary_slip_details = get_salary_details_for_employee(filters, conditions, employee.name, slip)
					if salary_slip_details:
						data.append({'employee_name' : employee.employee_name, 'month_name': employee.employee_pin})
						for s in salary_slip_details:
							if s.salary_component=='Basic':
								row['basic'] = s.amount or 0.0
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
							elif s.salary_component=='Other Allowance':
								row['other_allowance'] = s.amount
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
							elif s.salary_component=='Actual Contribution':
								row['actual_contribution'] = s.amount
							elif s.salary_component=='Permissible Limit1':
								row['permissible_limit1'] = s.amount
							elif s.salary_component=='Mortgage':
								row['mortgage_relief'] = s.amount
							elif s.salary_component=='Deposit on Home':
								row['deposit_on_home'] = s.amount
							elif s.salary_component=='Amount of Benefit':
								row['amount_of_benefit'] = s.amount
							elif s.salary_component=='Tax Charged':
								row['taxable_pay'] = s.amount
							elif s.salary_component=='Personal Relief':
								row['monthly_personal_relief'] = s.amount
							elif s.salary_component=='Insurance Relief':
								row['amount_of_insurance_relief'] = s.amount
							elif s.salary_component=='PAYE':
								row['paye_tax'] = s.amount
							elif s.salary_component=='Self Assessed PAYE':
								row['self_assessed_paye'] = s.amount

			data.append(row)



	return columns, data



def get_salary_details_for_employee(filters, conditions, employee, slip):

	return frappe.db.sql("""SELECT sd.salary_component, sd.amount FROM `tabSalary Slip` ss INNER JOIN `tabSalary Detail` sd on ss.name=sd.parent WHERE ss.name='%s' and ss.employee='%s' %s"""%(slip, employee, conditions), as_dict=True, debug=True)



def get_conditions(filters):
	# conditions = ""
	# if filters.get("company"):
	# 	conditions += " and ss.company='{}'".format(filters.get("company"))
	# if filters.get("employee"):
	# 	conditions += " and ss.employee='{}'".format(filters.get("employee"))


	# if filters.get("from_date"):
	# 	conditions += " and ss.posting_date>='{}'".format(filters.get("from_date"))
	# if filters.get("to_date"):
	# 	conditions += " and ss.posting_date<='{}'".format(filters.get("to_date"))
	return conditions
def get_columns():
	return [
		{
			'fieldname': 'employee_name',
			'fieldtype': 'Data',
			'label': _('Name of Employee'),
			'width': 200,
		},
		{
			'fieldname': 'month_name',
			'fieldtype': 'Data',
			'label': _('MONTH'),
			'width': 200,
		},
		{
			'fieldname': 'basic',
			'fieldtype': 'Currency',
			'label': _('Basic'),
			'width': 150,
		},
		{
			'fieldname': 'benefits',
			'fieldtype': 'Currency',
			'label': _('Benefits'),
			'width': 150,
		},
		{
			'fieldname': 'value_of',
			'fieldtype': 'Currency',
			'label': _('Value Of'),
			'width': 150,
		},
		{
			'fieldname': 'gross_pay',
			'fieldtype': 'Currency',
			'label': _('Gross Pay'),
			'width': 150,
		},
		{
			'fieldname': 'def_contr_ret_scheme_e1',
			'fieldtype': 'Currency',
			'label': _('Defined Contribution Retirement Scheme E1'),
			'width': 150,
		},
		{
			'fieldname': 'def_contr_ret_scheme_e2',
			'fieldtype': 'Currency',
			'label': _('Defined Contribution Retirement Scheme E2'),
			'width': 150,
		},
		{
			'fieldname': 'def_contr_ret_scheme_e3',
			'fieldtype': 'Currency',
			'label': _('Defined Contribution Retirement Scheme E3'),
			'width': 150,
		},
		{
			'fieldname': 'saving_amount_of_interest',
			'fieldtype': 'Currency',
			'label': _('Saving Amount of Interest'),
			'width': 150,
		},
		{
			'fieldname': 'owner_the_lowest_of_e_added',
			'fieldtype': 'Currency',
			'label': _('Owner The Lowest of E Added'),
			'width': 150,
		},
		{
			'fieldname': 'charge_pay',
			'fieldtype': 'Currency',
			'label': _('Charge Pay'),
			'width': 150,
		},
		{
			'fieldname': 'tax_charged',
			'fieldtype': 'Currency',
			'label': _('Tax Charged'),
			'width': 150,
		},
		{
			'fieldname': 'personal_relief',
			'fieldtype': 'Currency',
			'label': _('Personal Relief'),
			'width': 150,
		},
		{
			'fieldname': 'paye',
			'fieldtype': 'Currency',
			'label': _('PAYE'),
			'width': 150,
		},
		


		
	]
