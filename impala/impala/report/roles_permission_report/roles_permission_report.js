// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Roles Permission Report"] = {
	"filters": [
		{
			'fieldname': 'role',
			'fieldtype': 'Link',
			'options': 'Role',
			'label': __('Role'),
			'width': 200
		},
		{
			'fieldname': 'document',
			'fieldtype': 'Link',
			'options': 'DocType',
			'label': __('Document Type'),
			'width': 200
		},
	]
};
