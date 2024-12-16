// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Summary Report"] = {
	"filters": [
		{
			fieldname: "company",
			fieldtype: "Link",
			label: __("Company"),
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),	
		},
		{
			fieldname: "date_range",
			fieldtype: "DateRange",
			label: __("Date Range"),
			default: [frappe.datetime.month_start(), frappe.datetime.month_end()]
		},
		{
			fieldname: "item_type",
			fieldtype: "Select",
			label: __("Item Type"),
			options: ["", "Finished", "Scrap"]
		}
	]
};
