frappe.query_reports["Sales by Salesperson"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 0
        },
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
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "reqd": 0
        },
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        if (column.fieldname === "total_sales") {
            return frappe.format(value, { fieldtype: "Currency" });
        }
        return default_formatter(value, row, column, data);
    }
};
