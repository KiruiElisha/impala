frappe.query_reports["Advance Bank Details Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "100",
            "reqd": 1,
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "100",
            "reqd": 1,
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "width": "100",
            "options": "Cost Center",
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": "100",
        },
        {
            "fieldname": "designation",
            "label": __("Designation"),
            "fieldtype": "Link",
            "options": "Designation",
            "width": "100",
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": "100",
        }
				
		
		
    ]
};
