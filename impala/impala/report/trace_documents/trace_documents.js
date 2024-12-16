// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trace Documents"] = {
	"filters": [
		{
			"fieldname": "document_type",
			"label": __("Document Type"),
			"fieldtype": "Link",
			"options": "DocType",
			get_query: () => {
				docs = ['Material Request', 'Stock Entry', 'Quotation', 'Sales Order', 'Sales Invoice', 'Delivery Note', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice']
				return {
					filters: {
						'name': ['in', docs],
					}
				};
			},
			// "default": 'Material Request',
			'reqd': 1,
		},
		{
			"fieldname": "document_name",
			"label": __("Document Name"),
			"fieldtype": "Dynamic Link",
			"options": "document_type",
			'reqd': 1,
		},

	]
};

