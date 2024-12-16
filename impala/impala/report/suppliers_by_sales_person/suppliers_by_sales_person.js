// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt

frappe.query_reports["Suppliers By Sales Person"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			"hidden": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
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
			"fieldname": "supplier_group",
			"label": __("Supplier Group"),
			"fieldtype": "Link",
			"options": "Supplier Group"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (!data) return value;
		
		if (column.fieldname == "outstanding_amount") {
			if (data.outstanding_amount > 0) {
				value = `<span style='color:red; font-weight: bold;'>${value}</span>`;
			} else if (data.outstanding_amount < 0) {
				value = `<span style='color:green; font-weight: bold;'>${value}</span>`;
			}
		}
		
		if (column.fieldname == "payment_ratio") {
			const ratio = flt(data.payment_ratio, 2);
			if (ratio >= 90) {
				value = `<span style='color:green; font-weight: bold;'>${ratio}%</span>`;
			} else if (ratio >= 70) {
				value = `<span style='color:orange; font-weight: bold;'>${ratio}%</span>`;
			} else {
				value = `<span style='color:red; font-weight: bold;'>${ratio}%</span>`;
			}
		}
		
		if (column.fieldname == "avg_payment_days") {
			const days = flt(data.avg_payment_days, 1);
			if (days <= 30) {
				value = `<span style='color:green; font-weight: bold;'>${days}</span>`;
			} else if (days <= 60) {
				value = `<span style='color:orange; font-weight: bold;'>${days}</span>`;
			} else {
				value = `<span style='color:red; font-weight: bold;'>${days}</span>`;
			}
		}
		
		if (column.fieldname == "total_suppliers_overdue") {
			if (data.total_suppliers_overdue > 0) {
				value = `<span style='color:red; font-weight: bold;'>${value}</span>`;
			} else {
				value = `<span style='color:green; font-weight: bold;'>${value}</span>`;
			}
		}
		
		if (["total_invoices", "paid_amount"].includes(column.fieldname)) {
			value = `<span style='font-weight: 500;'>${value}</span>`;
		}
		
		if (column.fieldname == "sales_person") {
			value = `<span style='font-weight: bold; color: #1a73e8;'>${value}</span>`;
		}
		
		if (column.fieldname == "total_suppliers") {
			value = `<span style='font-weight: bold; color: #34495e;'>${value}</span>`;
		}
		
		return value;
	}
};
