// Copyright (c) 2023, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["P10 Report"] = {
	"filters": [
		{
            "fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Link",
            "options":"Fiscal Year",
            "default": frappe.defaults.get_user_default('fiscal_year')
        },
{
            "fieldname": "employee",
            "label": __("Employee Number"),
            "fieldtype": "Link",
            "options": "Employee"
        },
                {
            'fieldname': 'employer_pin',
            'fieldtype': 'Data',
            'label': __('Employer PIN'),
            'hidden': 1,
        },
	],
     onload: function() {
                frappe.query_report.set_filter_value('employee', '');     
                frappe.query_report.set_filter_value('year', '');    
                var company = frappe.query_report.get_filter_value('company');       
                frappe.db.get_value("Company", company, "tax_id", function(value) {
                    console.log(value['tax_id'])
                    frappe.query_report.set_filter_value('employer_pin', value['tax_id'])
                });        
               
            }
};
