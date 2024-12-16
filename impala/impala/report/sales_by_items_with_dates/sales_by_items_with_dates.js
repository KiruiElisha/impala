// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales by Items With Dates"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		// {
		// 	"fieldname": "from_date",
		// 	"label": "From Date",
		// 	"fieldtype": "Date",
		// 	"width": "80",
		// 	"default": frappe.datetime.add_days(frappe.datetime.get_today(), -2),
		// 	"reqd": 1,
		// },
		// {
		// 	"fieldname": "to_date",
		// 	"label": "To Date",
		// 	"fieldtype": "Date",
		// 	"width": "80",
		// 	"default": frappe.datetime.get_today(),
		// 	"reqd": 1
		// },
		{
			"fieldname": "date_range",
			"label": "Date Range",
			"fieldtype": "DateRange",
			"default": [
				frappe.datetime.add_days(frappe.datetime.get_today(), -2),
				frappe.datetime.get_today(),
			],
			"reqd": 1,
		},

	]
};
