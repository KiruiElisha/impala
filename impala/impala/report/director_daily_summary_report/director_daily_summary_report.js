// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Director Daily Summary Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "item_groups",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 0,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 0,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "workstation",
			"label": __("Workstation"),
			"fieldtype": "Link",
			"options": "Workstation",
			"width": "100",
		},
		{
			"fieldname": "groupby",
			"label": __("Group by"),
			"fieldtype": "Select",
			"options": ["Department", "Division"],
			"default": "Division",
			"hidden": 1,
		},

	]
};
