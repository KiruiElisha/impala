// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Overall Balances V-1"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["Item Group", "Warehouse"],
			"reqd": 1,
			"default": "Item Group"
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Item Group",
			get_data : function(txt){
				return frappe.db.get_link_options("Item Group", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			}
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Warehouse",
			get_data : function(txt){
				return frappe.db.get_link_options("Warehouse", txt, {
					company : frappe.query_report.get_filter_value('company')
				})
			}
			
		},
				{
			"fieldname": "show_qty",
			"label": __("Show Qty"),
			"fieldtype": "Check",
			"default": 1,
		},
		{
			"fieldname": "show_val",
			"label": __("Show Val"),
			"fieldtype": "Check",
			"default": 1,
		}
	],
};
