// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Collection Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"width": "80",
			"default": "Impala Glass Industries Ltd",
		},
		{
			"fieldname": "from_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": "80",
		},
		{
			"fieldname": "to_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": "80",
		},

	]
};
