// Copyright (c) 2023, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Loan Balance"] = {
	"filters": [
{"label": "Loan Name", "fieldname": "name", "fieldtype": "Link", "options": "Loan", "width": 120},
		{
			"label": "Employee Number",
			"fieldname": "applicant",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"label": "Loan Type",
			"fieldname": "loan_type",
			"fieldtype": "Link",
			"options": "Loan Type",
			"width": 120
		},
		{
			"label": "Department",
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"label": "From Date",
			"fieldname": "from_date",
			"fieldtype": "Date",
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
		},
		{
            "label": "DocStatus",
            "fieldname": "docstatus",
            "fieldtype": "Select",
            "options": [
                "",
                {
                    label: __("Draft"),
                    value: 0,
                },
                {
                    label: __("Submitted"),
                    value: 1,
                },
                {
                    label: __("Cancelled"),
                    value: 2,
                },
            ],
            "width": 120
        },,
		{
			"label": "showing balance",
			"fieldname": "showin_balance",
			"fieldtype": "Check",
			"width": 120
		}
	]
};
