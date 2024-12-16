// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Central Receipt Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": __("Company"),
			"options": "Company",
			"width": 100,
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_end()
		},
		// {
		// 	"fieldname": "group_by",
		// 	"label": __("Group by"),
		// 	"fieldtype": "Select",
		// 	"options": ["Currency", "Main Account"],
		// 	"default": "Currency"
		// },
		{
			"fieldname": "show_by",
			"label": __("Show by"),
			"fieldtype": "Select",
			"options": ["All", "Receipts", "Payments"],
			"default": "Receipts",
			"hidden": true
		}

	]
};
