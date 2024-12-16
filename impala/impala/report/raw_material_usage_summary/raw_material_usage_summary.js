// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Raw Material Usage Summary"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "month",
			"label": __("Month Name"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"],
			"default": "2022",
			"reqd": 1
		},

	]
};
