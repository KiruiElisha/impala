// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance by Multiple Units"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Company",
			"reqd":1,
			"default": frappe.defaults.get_user_default("Company"),
			get_query: function() {
				return {
					filters: [
						["Company", "is_group", "=", 0]
					]
				}
			},
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Warehouse",
			get_query: function() {
				return {
					filters: [
						["Warehouse", "company", "=", frappe.query_report.get_filter_value('company')]
					]
				}
			},
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Item",
			get_query: function() {
				return {
					filters: [
						// ["Company", "is_group", "=", 0]
					]
				}
			},
		},
	]
};
