// Copyright (c) 2023, Aqiq Hrm and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Overtime Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Link",
			"width": "100",
			"reqd": 1,
			"options": "Fiscal Year", // Fixed the missing comma here
			"default": new Date().getFullYear() // Default to the current year
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100",
		},
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": "100",
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"hidden": 1,
			"options": ["", "Present", "Absent", "Half Day", "On Leave", "Late Entry", "Early Exit", "Holiday", "Weekend"]
		},
	]
};
