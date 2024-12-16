// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Funds Movement Cash Flow V2"] = {
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
			"default": frappe.datetime.month_start()
			// "default": frappe.datetime.year_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end()
			// "default": frappe.datetime.year_end()
		},
		{
			"fieldname": "currency_exchange",
			"label": __("Currency Exchange"),
			"fieldtype": "Select",
			"options": ["", "UGX", "USD"],
			"default": "Currency"
		},
		{
			"fieldname": "exchange_rate",
			"label": __("Exchange Rate"),
			"fieldtype": "Float",
			"default": 1,
			// "reqd": true
		},
		// {
		// 	"fieldname": "group_by",
		// 	"label": __("Group by"),
		// 	"fieldtype": "Select",
		// 	"options": ["Currency", "Main Account"],
		// 	"default": "Currency"
		// },
		// {
		// 	"fieldname": "show_by",
		// 	"label": __("Show by"),
		// 	"fieldtype": "Select",
		// 	"options": ["All", "Receipts", "Payments"],
		// 	"default": "All"
		// },
		{
			"fieldname": "un_group",
			"label": __("Un Group"),
			"fieldtype": "Check",
			"default": 0
		}

	]
};
