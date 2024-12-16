// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Payment Schedule Detail"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},





		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},

		// {
		// 	"fieldname":"purchase_order",
		// 	"label": __("Purchase Order"),
		// 	"fieldtype": "Link",
		// 	"options": "Purchase Order",
		// 	get_query: function() {
		// 		return {
		// 			filters: [
		// 				["Purchase Order", "company", "=", frappe.query_report.get_filter_value('company')]
		// 			]
		// 		}
		// 	}


		// },





		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
			get_query: function() {
				return {
					filters: [
						["Cost Center", "company", "=", frappe.query_report.get_filter_value('company')]
					]
				}
			}
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			get_query: function() {
				return {
					filters: [
						["Supplier", "company", "=", frappe.query_report.get_filter_value('company')]
					]
				}
			}


		},



	]
};

