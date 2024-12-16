// Copyright (c) 2024, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Component Analysis"] = {
	"filters": [
		{
			"fieldname": "name",
			"fieldtype": "Link",
			"label": __("Sales Order"),
			"options": "Sales Order"
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": __("Item"),
			"options": "Item"
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
		},
	]
};
