// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salesmen wise Collection"] = {
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
			options: ["","Qty" , "Sale Exclusive" , "Sale Inclusive" ,  "Return Sale Inclusive" , "Return Sales Exclusive" , "Sales To Return"]
			// default : "qty
		},




		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person"

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