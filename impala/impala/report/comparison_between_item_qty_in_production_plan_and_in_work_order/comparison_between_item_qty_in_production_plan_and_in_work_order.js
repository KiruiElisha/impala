// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Comparison between Item Qty in Production Plan and in Work Order"] = {
	"filters": [
		{
			"fieldname": "production_plan",
			"fieldtype": "Link",
			"label": "Production Plan",
			"options": "Production Plan"
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			"default": new Date(new Date().setMonth(new Date().getMonth() - 1))
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",
			"default": new Date()
		}
	]
};

