// Copyright (c) 2023, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Transfer for NET SALARY"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.month_end()
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100",
		},
		{
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": "100",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100",
		},
		{
			"fieldname":"docstatus",
			"label": __("Document Status"),
			"fieldtype": "Select",
			"options": ["","Draft", "Submitted"],
			"width": "100",
		}
	]
};
