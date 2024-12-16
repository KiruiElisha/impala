// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Approval Documents Report"] = {
	"filters": [
		{
			fieldname: 'company',
			fieldtype: 'Link',
			options: 'Company',
			label: __('Company'),
			default: frappe.defaults.get_user_default('company'),			
		},
		// {
		// 	fieldname: 'document_type',
		// 	fieldtype: 'Link',
		// 	options: 'DocType',
		// 	label: __('Document Type'),			
		// },
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			options: 'Date',
			label: __('Creation From Date'),
			default: frappe.datetime.month_start(),			
		},
		{
			fieldname: 'to_date',
			fieldtype: 'Date',
			options: 'Date',
			label: __('Creation To Date'),
			default: frappe.datetime.month_end(),			
		},
		{
			fieldname: 'owner',
			fieldtype: 'Link',
			options: 'User',
			label: __('Created By')
		}

	]
};
