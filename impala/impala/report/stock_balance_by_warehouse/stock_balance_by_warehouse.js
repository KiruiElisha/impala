// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance By Warehouse"] = {
	"filters": [
		{
			"fieldname" : 'warehouse',
			"label" : __('Warehouse'),
			"fieldtype" : 'MultiSelectList',
			"options" : 'Warehouse',
			"width" : 120,
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse', txt, {
					company: frappe.query_report.get_filter_value("company")
				});
			}
		},
		{
			"fieldname" : 'item_group',
			"label" : __('Item Group'),
			"fieldtype" : 'Link',
			"options" : 'Item Group',
			"width" : 120
		},
		{
			"fieldname" : 'items',
			"label" : __('Items'),
			"fieldtype" : 'Link',
			"options" : 'Item',
			"width" : 120
		},
	]
};
