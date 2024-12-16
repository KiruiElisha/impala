// Copyright (c) 2023, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Loan Customized"] = {
	"filters": [
{"label": "Loan Name", "fieldname": "name", "fieldtype": "Link", "options": "Loan", "width": 120},
		{
			"label": "Applicant Type",
			"fieldname": "applicant_type",
			"fieldtype": "Select",
			"options": [
				"",
				{
					label: __("Employee"),
					value: "Employee",
				},
				{
					label: __("Member"),
					value: "Member",
				},
				{
					label: __("Customer"),
					value: "Customer",
				},
			],
			"width": 120
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Select",
			"options": [
				"",
				{
					label: __("Sanctioned"),
					value: "Sanctioned",
				},
				{
					label: __("Partially Disbursed"),
					value: "Partially Disbursed",
				},
				{
					label: __("Disbursed"),
					value: "Disbursed",
				},
				{
					label: __("Loan Closure Requested"),
					value: "Loan Closure Requested",
				},
				{
					label: __("Closed"),
					value: "Closed",
				},
			],
			"width": 120
		}
	]
};
