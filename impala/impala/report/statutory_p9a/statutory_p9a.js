// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statutory P9A"] = {
    "filters": [
        {
            'fieldname': 'company',
            'label': __('Company'),
            'fieldtype': 'Link',
            'options': 'Company',
            "hidden": 1,
            'default': frappe.defaults.get_user_default('company'),
        },
        // {
        //     'fieldname': 'from_date',
        //     'label': __('From Date'),
        //     'fieldtype': 'Date',
        //     'default': frappe.datetime.add_months(frappe.datetime.get_today(), -1), // Set default as one month ago
        // },
        // {
        //     'fieldname': 'to_date',
        //     'label': __('To Date'),
        //     'fieldtype': 'Date',
        //     'default': frappe.datetime.get_today(), // Set default as today
        // },
        {
            'fieldname': 'year',
            'fieldtype': 'Link',
            'options': 'Fiscal Year',
            'label': __('Payroll/Fiscal Year'),
            'reqd': 1,
            'default': 2024,
        },
        {
            'fieldname': 'employee',
            'fieldtype': 'Link',
            'options': 'Employee',
            'label': __('Employee'),
            'reqd': 1,
            on_change: function() {
                frappe.query_report.set_filter_value('employee_pin', '');
                frappe.query_report.set_filter_value('employee_name', '');
                frappe.query_report.set_filter_value('employee_payroll', '');
                frappe.query_report.set_filter_value('net_pay', '');

                var e = frappe.query_report.get_filter_value("employee");

                if (e) {
                    frappe.db.get_value("Employee", e, "employee_pin", function(value) {
                        frappe.query_report.set_filter_value('employee_pin', value['employee_pin'])
                    });

                    frappe.db.get_value("Employee", e, "employee_name", function(value) {
                        frappe.query_report.set_filter_value('employee_name', value['employee_name'])
                    });
                    frappe.db.get_value("Salary Slip", {'employee': e}, "payroll_entry", function(value) {
                        console.log(value['payroll_entry'])
                        frappe.query_report.set_filter_value('employee_payroll', value['payroll_entry']);
                    });
                    frappe.db.get_value("Salary Slip", {'employee': e}, "net_pay", function(value) {
                        console.log(value['net_pay'])
                        frappe.query_report.set_filter_value('net_pay', value['net_pay']);
                    });
                    
                }
            }
        },
        {
            'fieldname': 'employee_pin',
            'fieldtype': 'Data',
            'label': __('Employee PIN'),
            'hidden': 1,
        },
        {
            'fieldname': 'employee_name',
            'fieldtype': 'Data',
            'label': __('Employee Name'),
            'hidden': 1,
        },
        {
            'fieldname': 'employer_pin',
            'fieldtype': 'Data',
            'label': __('Employer PIN'),
            'hidden': 1,            
        },
        {
            'fieldname': 'employee_payroll',
            'fieldtype': 'Data',
            'label': __('Employee Payroll'),
            'hidden': 1,            
        },
        {
            'fieldname': 'net_pay',
            'fieldtype': 'Data',
            'label': __('Net Pay'),
            'hidden': 1,            
        },
    ],

    onload: function() {
                frappe.query_report.set_filter_value('employer_pin', '');               
                var company = frappe.query_report.get_filter_value('company');

                frappe.db.get_value("Company", company, "tax_id", function(value) {
                    console.log(value['tax_id'])
                    frappe.query_report.set_filter_value('employer_pin', value['tax_id'])
                });                   
               
            }
};

