// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/financial_statements_customized.js", function() {
	frappe.query_reports["Balance Sheet Customized"] = $.extend({}, erpnext.financial_statements);

	erpnext.utils.add_dimensions('Balance Sheet Customized', 9);

	
	frappe.query_reports["Balance Sheet Customized"]["filters"].push(
		{
			"fieldname": "presentation_currency",
			"label": __("Currency"),
			"fieldtype": "Select",
			"options": erpnext.get_presentation_currency_list()
	});
	frappe.query_reports["Balance Sheet Customized"]["filters"].push({
		"fieldname": "conversion_rate",
		"label": __("Converstion Rate"),
		"fieldtype": "Float",
		"default": 1.0
	});

	frappe.query_reports["Balance Sheet Customized"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	frappe.query_reports["Balance Sheet Customized"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check",
		"default": 1
	});
});
