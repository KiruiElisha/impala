// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Department Wise Sales and Collections"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		// {
		// 	"fieldname": "from_date",
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.month_start(),
		// },
		// {
		// 	"fieldname": "to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.month_end(),
		// },
		{
			"fieldname": "groupby",
			"label": __("Group by"),
			"fieldtype": "Select",
			"options": ["Department", "Division"],
			"default": "Department",
		},
		// {
		// 	"fieldname": "range",
		// 	"label": __("Range"),
		// 	"fieldtype": "Select",
		// 	"options": ["Daily", "Weekly", "Monthly"],
		// 	"default": "Daily",
		// },

	]
};
