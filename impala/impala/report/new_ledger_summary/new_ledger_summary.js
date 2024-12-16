frappe.query_reports["New Ledger Summary"] = {
	"filters": [
        {
            "fieldname": "party_type",
            "label": __("Party Type"),
            "fieldtype": "Select",
            "options": "Supplier",
            "reqd": 1,
            "default": "Supplier",
            "read_only": 1,
            "on_change": function(query_report) {
                var party_type = query_report.get_filter_value("party_type");
                var party_field = query_report.get_filter("party");
                var party_group_field = query_report.get_filter("party_group");
                var department_field = query_report.get_filter("department");
                var division_field = query_report.get_filter("division");
                if (party_type) {
                    query_report.refresh();
                    party_field.df.options = party_type;
                    party_field.refresh();
                    department_field.df.options = party_type;
                    department_field.refresh();
                    division_field.df.options = party_type;
                    division_field.refresh();
                }
            }
        },
        {
            "fieldname": "party_group",
            "label": __("Supplier Group"),
            "fieldtype": "Link",
            "options": "Supplier Group",
            "default": "3rd Party Supplier",
            "reqd": 1,
            "read_only": 1
        },
        {
            "fieldname": "party",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0,
            "get_query": function() {
                var party_group = frappe.query_report.get_filter_value('party_group');
                return {
                    filters: {
                        'supplier_group': party_group
                    }
                };
            }
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "reqd": 0
        },
        {
            "fieldname": "division",
            "label": __("Division"),
            "fieldtype": "Link",
            "options": "Cost Center",
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
        },
        {
            "fieldname": "date_filter",
            "label": __("Date Filter"),
            "fieldtype": "Select",
            "options": "Due Date\nPosting Date",
            "default": "Posting Date",
            "reqd": 1
        }
	]
}
