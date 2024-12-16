// Copyright (c) 2023, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Extra Hours Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100",
		},
		{
			"fieldname":"time_table",
			"label": __("Time Table"),
			"fieldtype": "Link",
			"options": "Time Table",
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
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["","Present", "Absent", "Half Day", "On Leave", "Late Entry", "Early Exit", "Holiday", "Weekend"]
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
		},
		{
			"fieldname":"group_by",
			"label":__("Group by"),
			"fieldtype":"Select",
			"options":["Department", "Cost Center"],
			"default": "Department",
			"width": "100px"
		},
	]
};
