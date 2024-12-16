frappe.query_reports["Production Variance"] = {
    "filters": [
        {
            "fieldname": "work_order",
            "label": __("Work Order"),
            "fieldtype": "Link",
            "options": "Work Order",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": "From",
            "fieldtype": "Date",
            "options": "",
            "default": new Date(new Date().setFullYear(new Date().getFullYear() - 1))
        },
        {
            "fieldname": "to_date",
            "label": "To",
            "fieldtype": "Date",
            "options": "",
            "default": new Date()
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": [
                "Draft", 
                "Submitted", 
                "Not Started", 
                "In Process", 
                "Completed", 
                "Stopped", 
                "Closed", 
                "Cancelled"
            ].join("\n"),
            "default": "In Process",
            "reqd": 0
        }
    ]
};
