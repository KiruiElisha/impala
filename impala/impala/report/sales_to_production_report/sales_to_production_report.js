// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales to Production Report"] = {
	"filters": [
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			label : __("Date Range"),
			fieldname: "date_range",
			fieldtype: "DateRange",
			default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
			reqd: 1

		},
		{
			label: __("Customer"),
			fieldname: "customer",
			fieldtype: "Link",
			options: "Customer",
		},
		{
			label: __("Item"),
			fieldname: "item",
			fieldtype: "Link",
			options: "Item",
		},
	],
	"onload": function(report) {
		// Columns Definitions here
		report.columns.forEach(function(column) {
			if(column.id === "is_packed") {
				column.read_only = true;
			}
		})
	}
};
