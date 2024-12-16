// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Breakdown Summary"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options" : "Company",
			"default": frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			"fieldname":"cost_center",
			"label": __("Division"),
			"fieldtype": "Link",
			"options" : "Cost Center", 
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
				"December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},

		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default" : frappe.defaults.get_user_default("Fiscal Year"),
			"reqd": 1,
		},

	]
};
