// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Cost VS Sales"] =  {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default : frappe.datetime.year_start(),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default : frappe.datetime.year_end(),
			reqd: 1
		},


		{
			fieldname: "level_1",
			label: __("Level 1"),
			fieldtype: "Select",
			options: ["" ,"Item Group"],


		},


		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: ["","Week","Month","Quarter","Year","Day"]
			// default : "Week"

			
			// on_change: function() {
			// 	if (filters.range !=""){

			// 		frappe.query_report.set_filter_value('value', "qty");
			// 	}
			// } ,


		} ,




		{
			fieldname: "value",
			label: __("Value"),
			fieldtype: "Select",
			options: ["","Qty" , "Amount Exclusive"]
			// default : "qty
		},







		{
			fieldname: "item_code",
			label: __("Item Code"),
			fieldtype: "Link",
			options:  "Item" 
		} ,


	{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options:  "Item" 
		} ,



		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},



		{
			fieldname: "cost_center",
			label: __("Division"),
			fieldtype: "Link",
			options: "Cost Center",
		},



	],
}