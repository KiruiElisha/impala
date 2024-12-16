// Copyright (c) 2023, Aqiq Hrm and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Company Sacco Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
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
        },
		
	]
};
