// Copyright (c) 2016, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Traceability"] = {
	"filters": [{
		fieldname: "company",
		label: __("Company"),
		fieldtype: "Link",
		options: "Company",
		
},
{
	fieldname: "department",
	label: __("Department"),
	fieldtype: "Link",
	options:"Department"
},
{
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date"
},
{
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date"
},

	]
};
