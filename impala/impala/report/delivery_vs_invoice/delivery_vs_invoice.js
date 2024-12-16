// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery VS Invoice"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 0
		},
		{
			"fieldname": "delivery_note",
			"label": __("Delivery Note"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"reqd": 0
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 0
		},
		{
			"fieldname": "cost_center",
			"label": __("Division"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"reqd": 0
		},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"reqd": 0
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"reqd": 0
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["","Draft","Return","Credit Note Issued","Submitted","Paid","Partly Paid","Unpaid","Unpaid and Discounted","Partly Paid and Discounted","Overdue and Discounted","Overdue","Cancelled","Internal Transfer"],
			"reqd": 0
		},
		{
            "fieldname": "remove_zero_balance",
            "label": __("Remove Rows with Zero Balance Qty"),
            "fieldtype": "Check",
            "default": 0,
            "reqd": 0
        }
	]
};
