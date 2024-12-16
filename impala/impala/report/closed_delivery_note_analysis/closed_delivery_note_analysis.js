// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Closed Delivery Note Analysis"] = {
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
			"fieldname": "groupby",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": ["Customer", "Cost Center", "Department", "Warehouse", "Customer Group", "Item Group"],
			"default": "Customer"
		},
		{
			"fieldname": "territory",
			"fieldtype": "MultiSelectList",
			"options": "Territory",
			"label": __("Territory"),
			get_data: function(txt){
				return frappe.db.get_link_options("Territory", txt, {
					// company : frappe.query_report.get_filter_value('company')
				})
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
			},
			"onload": function(frm) {
				frm.set_query("department", function () {
					return {
						filters: {
							is_group: 0,
							disabled: 0
						}
					};
				});
			}
		},
		{
			"fieldname": "warehouse",
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			"label": __("Warehouse"),
			get_data: function(txt){
				return frappe.db.get_link_options("Warehouse", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			} 
		},
		{
			"fieldname": "brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options":"Brand"
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
			}
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
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "MultiSelectList",
			"options":"Sales Person",
			get_data : function(txt){
				return frappe.db.get_link_options('Sales Person', txt, {
					// company: frappe.query_report.get_filter_value("company")
				});
			}
		},
		{
			"fieldname": "item_category",
			"label": __("Item Category"),
			"fieldtype": "MultiSelectList",
			"options":"Item Category",
			get_data : function(txt){
				return frappe.db.get_link_options('Item Category', txt, {
					// company: frappe.query_report.get_filter_value("company")
				});
			}
		},

	],

	"formatter": function(value, row, column, data, default_formatter) {
		// body...
		value = default_formatter(value, row, column, data);

		if (column.fieldname=='qty' && data.qty==null){
			value = ""
		}
		
		if (column.fieldname=='amount' && data.amount==null){
			value = ""
		}

		if (column.fieldname=='base_amount' && data.base_amount==null){
			value = ""
		}

		if (column.fieldname=='item_cost' && data.item_cost==null){
			value = ""
		}

		if (column.fieldname=='gross_profit' && data.gross_profit==null){
			value = ""
		}
		
		if (column.fieldname=='gp_percent' && data.gp_percent==null){
			value = ""
		}


		return value	
	}
};
