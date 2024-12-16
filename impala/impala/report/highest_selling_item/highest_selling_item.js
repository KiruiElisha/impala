// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Highest Selling Item"] = {
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
			fieldname: "top",
			label: __("Top"),
			fieldtype: "Select",
			options: ["","1",  "5", "10","15","20","25"]

		},





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