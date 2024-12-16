// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Dues"] = {
"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.year_start()
		},

		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.year_end()
		},


		{
			fieldname: "period",
			label: __("Period"),
			fieldtype: "Select",
			options: ["Week", "Month", "Quarter", "Year"],
			"default" : "Week"
			
		},


		{
			fieldname: "grouping",
			label: __("Grouping"),
			fieldtype: "Select",
			options: ["Item", "Sales Person","Territory", "Item Group", "Customer","Divsion"],
			"default" : "Item"
			
	},

	]
};