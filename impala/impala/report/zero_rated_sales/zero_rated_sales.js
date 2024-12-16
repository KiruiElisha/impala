// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zero Rated Sales"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			reqd: 1,
		},
		{
			"fieldname": "cost_center",
			"label": __("Division"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "etr_sno",
			"label": __("etr serial no"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
				"December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},

		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year"
			// "default" : frappe.datetime.year_end()
		},

	]
};
