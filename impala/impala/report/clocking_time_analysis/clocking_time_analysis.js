// Copyright (c) 2023, Aqiq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Clocking Time Analysis"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd":1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100",
		},
		{
			"fieldname":"time_table",
			"label": __("Time Table"),
			"fieldtype": "Link",
			"options": "Time Table",
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
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["","Present", "Absent", "Half Day", "On Leave", "Late Entry", "Early Exit", "Holiday", "Weekend"]
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Cost Center",
		},
		{
			"fieldname":"group_by",
			"label":__("Group by"),
			"fieldtype":"Select",
			"options":["Department", "Cost Center"],
			"default": "Department",
			"width": "100px"
		},
	],

	"onload": function(report){
		var isZero = false;
		
		$(document).delegate('.arrival_time', 'focus', function(){
			var hms = $(this).val();
			var a = hms.split(':');
			var seconds = (+a[0])*60*60 + (+a[1])*60 + (+a[2]);
			var count = 1;
			if(seconds > 0){
				isZero = true;
				console.log(isZero);
				if (isZero){
					$(this).attr("readonly", true)
				}
			}
		})


		$(document).delegate('.arrival_time','change', function(e) {
			var employee = $(this).attr('data-employee');
			var employee_name = $(this).attr('data-employee_name')
			var time_table = $(this).attr('data-time_table')
			var type = 'IN'
			var arrivalDate = $(this).attr('data-date');
			var arrivalTime = $(this).val()
			
			var checkInDtime = arrivalDate + ' ' + arrivalTime

			frappe.db.insert({
				'doctype': 'Employee Checkin',
				'employee': employee,
				'employee_name': employee_name,
				'type': type,
				'employee_shift': time_table,
				'time': checkInDtime
			}).then(doc => {
				console.log('Inserted a new Employee Checkin.');
				
			})
		
		});

		$(document).delegate('.departure_time', 'focus', function(){
			var hms = $(this).val();
			var a = hms.split(':');
			var seconds = (+a[0])*60*60 + (+a[1])*60 + (+a[2]);
			var count = 1;
			if(seconds > 0){
				isZero = true;
				console.log(isZero);
				if (isZero){
					$(this).attr("readonly", true)
				}
			}
		})


		$(document).delegate('.departure_time','change', function(e) {
			var employee = $(this).attr('data-employee');
			var employee_name = $(this).attr('data-employee_name')
			var time_table = $(this).attr('data-time_table')
			var type = 'OUT'
			var departureDate = $(this).attr('data-date');
			var departureTime = $(this).val()
			
			var checkOutDtime = departureDate + ' ' + departureTime
			console.log(time_table)
			console.log(checkOutDtime)
			frappe.db.insert({
				'doctype': 'Employee Checkin',
				'employee': employee,
				'employee_name': employee_name,
				'type': type,
				'employee_shift': time_table,
				'time': checkOutDtime
			}).then(doc => {
				console.log('Inserted a new Employee Checkin.');
				
			})
		
		});	
	},
};
