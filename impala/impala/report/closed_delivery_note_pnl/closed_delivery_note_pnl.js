// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Closed Delivery Note PNL"] = {
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
			"default" : frappe.datetime.year_start(),
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"default": frappe.datetime.year_end(),
		},
		{
			"fieldname": "group_by",
			"fieldtype": "Select",
			"options": ["Voucher", "Item"],
			"label": __("Report Based On"),
			"default": "Voucher",
			"hidden": 1
		},
		{
			"fieldname": "voucher_no",
			"fieldtype": "MultiSelectList",
			"options": "Sales Invoice",
			"label": __("Voucher No"),
			get_data : function(txt){
				return frappe.db.get_link_options("Delivery Note", txt, {
					'company' : frappe.query_report.get_filter_value('company')
				})
			},
			depends_on: 'eval:frappe.query_report.get_filter_value("group_by")=="Voucher"'
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
			},
			depends_on: 'eval: frappe.query_report.get_filter_value("group_by")=="Item"'
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
			"fieldname": "customer",
			"fieldtype": "MultiSelectList",
			"options": "Customer",
			"label": __("Customer"),
			get_data : function(txt){
				return frappe.db.get_link_options("Customer", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			},
			depends_on: 'eval: frappe.query_report.get_filter_value("group_by")=="Voucher"'
		},
		{
			"fieldname": "customer_group",
			"fieldtype": "MultiSelectList",
			"options": "Customer Group",
			"label": __("Customer Group"),
			get_data : function(txt){
				return frappe.db.get_link_options("Customer Group", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			},
			depends_on: 'eval: frappe.query_report.get_filter_value("group_by")=="Voucher"'
		},
		{
			"fieldname": "territory",
			"fieldtype": "MultiSelectList",
			"options": "Territory",
			"label": __("Territory"),
			get_data : function(txt){
				return frappe.db.get_link_options("Territory", txt, {
				})
			},
			depends_on: 'eval: frappe.query_report.get_filter_value("group_by")=="Voucher"'
		},
		{
			"fieldname": "warehouse",
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			"label": __("Warehouse"),
			get_data: function(txt){
				return frappe.db.get_link_options("Warehouse", txt, {})
			}
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "MultiSelectList",
			"options":"Sales Person",
			get_data : function(txt){
				return frappe.db.get_link_options('Sales Person', txt, {
				});
			}
		},
		// {
		// 	"fieldname": "item_category",
		// 	"label": __("Item Category"),
		// 	"fieldtype": "MultiSelectList",
		// 	"options":"Item Category",
		// 	get_data : function(txt){
		// 		return frappe.db.get_link_options('Item Category', txt, {
		// 			// company: frappe.query_report.get_filter_value("company")
		// 		});
		// 	}
		// }
	],
	
};
