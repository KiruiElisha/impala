// Copyright (c) 2024, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */
// Copyright (c) 2024, Your Company
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Note Customized"] = {
	"filters": [
        {
            "fieldname": "delivery_note_number",
            "label": __("Delivery Note Number"),
            "fieldtype": "Link",
            "options": "Delivery Note"
        },
        {
            "fieldname": "from_date",
            "label": __("Date From"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("Date To"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "against_sales_order",
            "label": __("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order"
        }
    ],
    "onload": function(report) {
        // Set default values for filters if needed
        report.page.fields_dict.from_date.set_input("2024-01-01");
        report.page.fields_dict.to_date.set_input(frappe.datetime.get_today());
    }
};
