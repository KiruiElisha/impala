// Created by Josh
// Copyright (c) 2024, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Transfer for NET SALARY customized"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.month_end()
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100",
		},
		{
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": "100",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100",
		},
		{
			"fieldname":"payroll_category",
			"label": __("Payroll Category"),
			"fieldtype": "Link",
			"options": "Payroll Category",
			"width": "100",
			"reqd": 1,
			"get_query": function() {
				return {
					"filters": {
						// Fetch the user's payroll category and set it as a filter
						"name": frappe.get_session().user
					}
				};
			}
			
		},
		{
			"fieldname":"docstatus",
			"label": __("Document Status"),
			"fieldtype": "Select",
			"options": ["","Draft", "Submitted"],
			"width": "100",
		},
	],

	"onload": function(report) {
		var user_id = frappe.session.user;
	
		// Fetch employee details using the user_id as a filter
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Employee",
				filters: { "user_id": user_id },
				fieldname: ["payroll_category"]
			},
			callback: function(response) {
				if (response.message) {
					var payrollCategory = response.message.payroll_category;
	
					console.log("Payroll Category:", payrollCategory);
	
					// Set the retrieved payroll category in the filter
					var payrollCategoryField = report.page.fields_dict["payroll_category"];
					if (payrollCategoryField) {
						payrollCategoryField.set_input(payrollCategory);
					}
				} else {
					console.log(`No employee found with user_id: ${user_id}`);
				}
			}
		});
	},
	

	// "onload": function(report) {
	// 	console.log(frappe.session.user);
	// 	var validDataFound = false;
	// 	function getEmployeeInfoByField(field) {
	// 		if (!validDataFound) {
	// 			frappe.call({
	// 				method: "frappe.client.get_value",
	// 				args: {
	// 					doctype: "Employee",
	// 					filters: { [field]: frappe.session.user },
	// 					fieldname: ["employee_number", "payroll_category"]
	// 				},
	// 				callback: function(response) {
	// 					if (response.message) {
	// 						var employeeNumber = response.message.employee_number;
	// 						var payrollCategory = response.message.payroll_category;

	// 						console.log("Employee Number:", employeeNumber);
	// 						console.log("Payroll Category:", payrollCategory);
	// 						validDataFound = true;
	// 						console.log("Additional instructions after valid data is found");

	// 						// Set the retrieved payroll category in the filter
	// 						var payrollCategoryField = report.page.fields_dict["payroll_category"];
	// 						if (payrollCategoryField) {
	// 							payrollCategoryField.set_input(payrollCategory);
	// 						}
	// 					} else {
	// 						console.log(`No employee found with ${field}: ${frappe.session.user}`);
	// 					}
	// 				}
	// 			});
	// 		}
	// 	}
	// 	getEmployeeInfoByField("user_id");
	// 	getEmployeeInfoByField("personal_email");
	// 	getEmployeeInfoByField("company_email");
	// },
};


// payroll category in an array, 