// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Branch wise Sales Report"] = {
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
			options: ["","value_inclusive","value_exclusive",  "return_exclusive" , "sales_return" ]
			// default : "qty"


		},



		// {
		// 	fieldname: "branch",
		// 	label: __("Branch"),
		// 	fieldtype: "Link",
		// 	options: "Branch"

		// },



		// {
		// 	fieldname: "sales_invoice",
		// 	label: __("Sales Invoice"),
		// 	fieldtype: "Link",
		// 	options: "Sales Invoice"

		// },


		// {
		// 	fieldname: "sales_order",
		// 	label: __("Sales Order"),
		// 	fieldtype: "Link",
		// 	options: "Sales Order"

		// },


		// {
		// 	fieldname: "qoutation",
		// 	label: __("Qoutation"),
		// 	fieldtype: "Link",
		// 	options: "Qoutation"

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