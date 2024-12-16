// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Master Sales Report KVL"] = {
	"filters": [
		{
			"fieldname" : "company",
			"fieldtype": "Link",
			"label": __("Company"),
			"options": "Company",
			"default": frappe.defaults.get_user_default("company"),
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
			"default" : frappe.datetime.month_start(),
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"default": frappe.datetime.month_end(),
		},
		{
			"fieldname": "customer",
			"fieldtype": "MultiSelectList",
			"label": __("Customer"),
			"options": "Customer",
			get_data : function(txt){
				return frappe.db.get_link_options('Customer', txt, {
					company: frappe.query_report.get_filter_value("company")
				});
			}
		},
		{
			"fieldname": "cost_center",
			"fieldtype": "MultiSelectList",
			"options": "Cost Center",
			"label": __("Division"),
			get_data: function(txt){
				return frappe.db.get_link_options("Cost Center", txt, {
					company : frappe.query_report.get_filter_value('company')
				})
			}
		},
		{
			"fieldname": "department",
			"fieldtype": "MultiSelectList",
			"options": "Department",
			"label": __("Department"),
			get_data : function(txt){
				return frappe.db.get_link_options("Department", txt, {
					
				})
			}
		},
		{
			"fieldname": "item_code",
			"fieldtype": "MultiSelectList",
			"options": "Item",
			"label": __("Item"),
			get_data : function(txt){
				return frappe.db.get_link_options("Item", txt, {
					// 'item_group' : frappe.query_report.get_filter_value('item_group')
				})
			}
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
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Customer Group",
			get_data : function(txt){
				return frappe.db.get_link_options("Customer Group", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			}
		},
		// {
		// 	"fieldname": "sales_person",
		// 	"fieldtype": "MultiSelectList",
		// 	"options": "Sales Person",
		// 	"label": __("Sales Person"),
		// 	get_data : function(txt){
		// 		return frappe.db.get_link_options("Sales Person", txt, {
		// 			// company : frappe.query_report.get_filter_value('company')
		// 		})
		// 	}
		// },
		// {
		// 	"fieldname": "parent_group_by",
		// 	"label": __("Group By Parent Columns"),
		// 	"fieldtype": "Select",
		// 	"options" : ["", "Customer", "Department", "Division"],
		// }
	]
};
