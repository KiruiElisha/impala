// Copyright (c) 2023, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee turnover Report"] = {
	"filters": [
{"label": "Employee Number", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
{
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Select",
            "options": [
				"",
				{
					label: __("Active"),
					value: "Active",
				},
				{
					label: __("Inactive"),
					value: "Inactive",
				},
				{
					label: __("Suspended"),
					value: "Suspended",
				},
				{
					label: __("Left"),
					value: "Left",
				},
			],
            "width": 120
        },
{"label": "Check to get Employees who left", "fieldname": "left", "fieldtype": "Check", "width": 120}

	]
};
