// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salesmen Wise Sales and Collections"] = {
	"filters": [
		// {
		// 	"fieldname": "company",
		// 	"label": __("Company"),
		// 	"fieldtype": "Link",
		// 	"options": "Company",
		// 	"default": "Impala Glass Industries Ltd",
		// },
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
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
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
