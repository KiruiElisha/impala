// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Division Wise Sales Collections and Outstanding"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "cost_center",
			"label": __("Division"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},

	]
};
