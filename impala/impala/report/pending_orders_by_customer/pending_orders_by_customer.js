// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Orders by Customer"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center"
        }
    ]
};
