// Copyright (c) 2023, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["P10R Report"] = {
	"filters": [
		{
			'fieldname': 'company',
			'label': __('Company'),
			'fieldtype': 'Link',
			'options': 'Company',
			'default': frappe.defaults.get_user_default('company'),
		},
		{
			'fieldname': 'from_date',
			'label': __('From Date'),
			'fieldtype': 'Date',
		},
		{
			'fieldname': 'to_date',
			'label': __('To Date'),
			'fieldtype': 'Date',
		},
		// {
		// 	'fieldname': 'payroll_month',
		// 	'label': __('Payroll Month'),
		// 	'fieldtype': 'Select',
		// 	'reqd':1,
		// 	'options': ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		// },
		{
			'fieldname': 'fiscal_year',
			'fieldtype': 'Link',
			'options': 'Fiscal Year',
			'label': __('Payroll/Fiscal Year'),
			'reqd':1,
			'default': 2023,
		},
		{
			'fieldname': 'employee',
			'fieldtype': 'Link',
			'options': 'Employee',
			'label': __('Employee'),
		}

	]
};
