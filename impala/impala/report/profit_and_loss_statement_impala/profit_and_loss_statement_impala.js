// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


frappe.require("assets/erpnext/js/financial_statements_customized.js", function() {
	frappe.query_reports["Profit and Loss Statement Impala"] = $.extend({},
		erpnext.financial_statements);

	erpnext.utils.add_dimensions('Profit and Loss Statement Impala', 9);
	
	frappe.query_reports["Profit and Loss Statement Impala"]["filters"].push(
		{
			"fieldname": "presentation_currency",
			"label": __("Currency"),
			"fieldtype": "Select",
			"options": erpnext.get_presentation_currency_list()
	});
	frappe.query_reports["Profit and Loss Statement Impala"]["filters"].push(
		{
			"fieldname": "conversion_rate",
			"fieldtype": "Float",
			"label": __("Conversion Rate"),
			"default": 1.0
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "show_in_millions",
			"label": __("Show in Millions"),
			"fieldtype": "Check",
			"default": 0,
		}
	);
});
