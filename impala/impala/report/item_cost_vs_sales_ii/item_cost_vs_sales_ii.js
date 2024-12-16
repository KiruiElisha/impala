// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Cost VS Sales II"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			"default" : frappe.datetime.year_start(),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			"default" : frappe.datetime.year_end(),
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
			fieldname: "item_code",
			label: __("Item Code"),
			fieldtype: "Link",
			options: "Item"

		},

		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Data",

		},




		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},



	],
}