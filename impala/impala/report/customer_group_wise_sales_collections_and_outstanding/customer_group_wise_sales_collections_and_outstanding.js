// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Group Wise Sales Collections and Outstanding"] = {
	"filters": [
		{
			"fieldname": "customer_groups",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
		},
	]
};
