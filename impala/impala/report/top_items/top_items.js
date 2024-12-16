// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Top Items"] = {
    "filters": [       
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default" : frappe.defaults.get_default("company"),
            "reqd": 1
        },
        {
            "fieldname": "cost_center",
            "label": __("Division"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "reqd": 0
        },
        {
            "fieldname": "item",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        }, 
        {
            "fieldname": "limit",
            "label": __("Limit"),
            "fieldtype": "Data",
            "default" : 10,
            "reqd": 0
        }
    ]
};
