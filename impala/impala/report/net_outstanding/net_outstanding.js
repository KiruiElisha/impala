// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Net Outstanding"] = {
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
			"fieldname": "party_type",
			"label": __("Party Type"),
			"fieldtype": "Select",
			"options": "Customer\nSupplier",
			"reqd": 1,
			"default": "Customer",
			"on_change": function(query_report) {
				let party_type = query_report.get_filter_value('party_type');
				let party = query_report.get_filter('party');
				let party_group = query_report.get_filter('party_group');

				party.df.options = party_type;
				party.df.label = __(party_type);
				party.refresh();

				party_group.df.options = party_type === "Customer" ? "Customer Group" : "Supplier Group";
				party_group.df.label = __(party_type === "Customer" ? "Customer Group" : "Supplier Group");
				party_group.refresh();

				query_report.set_filter_value('party', '');
				query_report.set_filter_value('party_group', '');
				query_report.refresh();
			}
		},
		{
			"fieldname": "party",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"on_change": function(query_report) {
				if(query_report.get_filter_value('party')) {
					query_report.set_filter_value('party_group', '');
					query_report.refresh();
				}
			}
		},
		{
			"fieldname": "party_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"on_change": function(query_report) {
				if(query_report.get_filter_value('party_group')) {
					 query_report.set_filter_value('party', '');
					 query_report.refresh();
				}
			}
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": "Due Date\nPosting Date",
			"default": "Due Date"
		},
		{
			"fieldname": "range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"hidden": 1
		},
		{
			"fieldname": "range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"hidden": 1
		},
		{
			"fieldname": "range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"hidden": 1
		},
		{
			"fieldname": "range4",
			"label": __("Ageing Range 4"),
			"fieldtype": "Int",
			"default": "120",
			"hidden": 1
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (data) {
			if (["outstanding", "pd_cheques", "net_outstanding", "range1", "range2", "range3", "range4", "range5"].includes(column.fieldname)) {
				value = format_currency(Math.abs(data[column.fieldname]));
				
				if (data[column.fieldname] < 0) {
					value = "<span style='color:red'>(" + value + ")</span>";
				}
			}

			if (data.bold) {
				value = value.bold();
			}

			if (row % 2 === 0) {
				$(row).css('background-color', '#f8f9fa');
			}
		}
		
		return value;
	},

	"onload": function(report) {
		report.page.add_inner_button(__("Refresh"), function() {
			let filters = report.get_values();
			
			Promise.all([
				frappe.call({
					method: "frappe.client.delete_doc",
					args: {
						doctype: "Cache",
						name: `net_outstanding_${filters.company}_${filters.party_type}_${filters.to_date}`
					}
				}),
				frappe.call({
					method: "frappe.client.delete_doc",
					args: {
						doctype: "Cache",
						name: `ar_summary_${filters.company}_${filters.party_type}_${filters.to_date}`
					}
				})
			]).then(() => {
				report.refresh();
			});
		});

		let party_type = report.get_filter_value('party_type');
		let party = report.get_filter('party');
		let party_group = report.get_filter('party_group');

		party.df.label = __(party_type);
		party.df.options = party_type;
		party.refresh();

		party_group.df.label = __(party_type === "Customer" ? "Customer Group" : "Supplier Group");
		party_group.df.options = party_type === "Customer" ? "Customer Group" : "Supplier Group";
		party_group.refresh();

		frappe.ui.keys.add_shortcut({
			shortcut: 'ctrl+r',
			action: () => report.refresh(),
			description: __('Refresh Report')
		});
	},

	"tree": false,
	"initial_depth": 0,
	"print_first_row_bold": true,
	
	get_datatable_options(options) {
		return Object.assign(options, {
			orderCellsTop: true,
			fixedHeader: true,
			pageLength: 50,
			lengthMenu: [[50, 100, 250, -1], [50, 100, 250, "All"]],
			scrollX: true,
			scrollY: '400px',
			deferRender: true,
			scroller: true,
			stateSave: true
		});
	}
};

function format_currency(value) {
	return format_number(value, null, 2);
}
