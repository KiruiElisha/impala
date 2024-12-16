// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product Sales Analysis Daily"] = {
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
			fieldname: "item_code",
			label: __("ITem Code"),
			fieldtype: "Link",
			options: "Item",
			},


		{
			fieldname: "item_group",
			label: __(" Item Group "),
			fieldtype: "Link",
			options: "Item Group",
			},


		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},


		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["","Draft","On Hold",   "To Deliver and Bill" , "To Bill" , "To Deliver", "Completed" , "Cancelled" , "Closed" ]
			// default : "qty"
		},




	]
};