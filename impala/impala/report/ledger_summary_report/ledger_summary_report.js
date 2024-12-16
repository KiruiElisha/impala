// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ledger Summary Report"] = {
	"filters": [
        {
            "fieldname": "party_type",
            "label": __("Party Type"),
            "fieldtype": "Select",
            "options": "Customer\nSupplier",
            "reqd": 1,
            "default": "Customer",
            "on_change": function(query_report) {
                var party_type = query_report.get_filter_value("party_type");
                var party_field = query_report.get_filter("party");
                if (party_type) {
                    query_report.refresh();
                    party_field.df.options = party_type;
                    party_field.refresh();
                }
            }
        },
        {
            "fieldname": "party",
            "label": __("Party"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0
        },
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
        }
    ]
};
