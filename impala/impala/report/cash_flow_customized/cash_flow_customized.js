// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements_customized.js", function() {
	frappe.query_reports["Cash Flow Customized"] = $.extend({},
		erpnext.financial_statements);

	erpnext.utils.add_dimensions('Cash Flow Customized', 9);

	// The last item in the array is the definition for Presentation Currency
	// filter. It won't be used in Cash Flow Customized for now so we pop it. Please take
	// of this if you are working here.

	frappe.query_reports["Cash Flow Customized"]["filters"].push(
		{
			"fieldname": "presentation_currency",
			"label": __("Currency"),
			"fieldtype": "Select",
			"options": erpnext.get_presentation_currency_list()
		});
	frappe.query_reports["Cash Flow Customized"]["filters"].push(
		{
			"fieldname": "conversion_rate",
			"label": __("Conversion Rate"),
			"fieldtype": "Float",
			"default": 1.0
		});
	frappe.query_reports["Cash Flow Customized"]["filters"].push(
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		});
});
