// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product Sales Analysis Monthly"] = {
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
			options: ["" , "Customer", "Item Group" , "Item" , "Sales Person" , "Division" , "Territory"],


		},


		{
			fieldname: "level_2",
			label: __("Level 2"),
			fieldtype: "Select",
			options: ["","Customer", "Item Group" , "Item" , "Sales Person" , "Division" , "Territory"],


		},


		{
			fieldname: "level_3",
			label: __("Level 3"),
			fieldtype: "Select",
			options: ["","Customer", "Item Group" , "Item" , "Sales Person" , "Division" , "Territory"],


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
			options: ["","qty","amount_exclusive",  "amount_inclusive" ,]
			// default : "qty"


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