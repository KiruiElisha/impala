// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product and Salesmen wise analysis"] = {
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
			options: ["" ,"Sales Person"],


		},


		{
			fieldname: "level_2",
			label: __("Level 2"),
			fieldtype: "Select",
			options: ["" , "Item"],


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
			options: ["","Qty","Sale Exclusive",  "Sale Inclusive" , "Retun Exclusive",  "Return Inclusive" , "Return To Sales"]
			// default : "qty"


		},


		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item"
			// default : "qty"


		},



		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Data",
			// default : "qty"


		},


		// {
		// 	fieldname: "sales_person",
		// 	label: __("Sales Person"),
		// 	fieldtype: "Link",
		// 	options: "Sales Person"]
		// 	// default : "qty"


		// },





		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},



	],
}