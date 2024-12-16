// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Party Balances"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
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
				var party_type = query_report.get_filter_value("party_type");
				var party_field = query_report.get_filter("party");
				if (party_type) {
					party_field.df.options = party_type;
					party_field.refresh();
					query_report.refresh();
				}
			}
		},
		{
			"fieldname": "party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",			
			"get_options": function() {
				return frappe.query_report.get_filter_value('party_type');
			},
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value('party_type');
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt, {
					'disabled': frappe.query_report.get_filter_value("disabled_party")
				});
			}
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "division",
			"label": __("Division"),
			"fieldtype": "Link",
			"options": "Cost Center"
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
			"fieldname": "disabled_party",
			"label": __("Show Disabled Party"),
			"fieldtype": "Check",
			"hidden": 0,
			"default": "1",

		},
	],

	"formatter": function(value, row, column, data, default_formatter) {
		if (!data || !column.fieldname) return default_formatter(value, row, column, data);
		
		value = default_formatter(value, row, column, data);
		
		try {
			// Format currency fields
			const currencyFields = [
				"closing_balance_bc", "pd_cheques", "net_amount",
				"range1", "range2", "range3", "range4", "range5"
			];

			if (currencyFields.includes(column.fieldname)) {
				const amount = flt(data[column.fieldname], precision("Currency"));
				
				if (amount === null || amount === undefined) return value;

				// Add bold formatting for non-zero amounts
				if (amount !== 0) {
					value = `<b>${value}</b>`;

					// Add color coding with opacity for better visibility
					if (amount < 0) {
						value = `<span style='color:#ff5858'>${value}</span>`;
					} else if (amount > 0) {
						value = `<span style='color:#2e7d32'>${value}</span>`;
					}

					// Add thousands separator indicator for large amounts
					if (Math.abs(amount) >= 100000) {
						value = `<span style='border-bottom: 2px double #888'>${value}</span>`;
					}
				}

				// Handle aging buckets
				if (column.fieldname.startsWith("range") && amount !== 0) {
					const rangeMap = {
						range1: "Current to 30 days past due",
						range2: "31 to 60 days past due",
						range3: "61 to 90 days past due",
						range4: "91 to 120 days past due",
						range5: "More than 120 days past due"
					};

					// Calculate percentage only if closing balance exists and is not zero
					let percentageText = "";
					if (data.closing_balance_bc && data.closing_balance_bc !== 0) {
						const percentage = ((amount / data.closing_balance_bc) * 100).toFixed(1);
						percentageText = `\nPercentage: ${percentage}%`;
					}

					value = `<span title="${rangeMap[column.fieldname]}${percentageText}">${value}</span>`;
				}
			}

			// Enhanced party name formatting - only if value exists
			if (column.fieldname === "party_name" && value) {
				value = `<b style='color: #2c5282'>${value}</b>`;
			}

			// Party group formatting - only if value exists
			if (column.fieldname === "party_group" && value) {
				value = `<span style='color: #4a5568; font-style: italic'>${value}</span>`;
			}

			// Department and Division formatting - only if value exists
			if (["department", "cost_center"].includes(column.fieldname) && value) {
				value = `<span style='color: #718096; font-family: monospace'>${value}</span>`;
			}

			// Net amount special formatting - only if value exists and is not zero
			if (column.fieldname === "net_amount" && data.net_amount) {
				const amount = flt(data.net_amount);
				if (Math.abs(amount) > 0) {
					// Start with the basic value
					let formattedValue = value;

					// Add bold formatting
					formattedValue = `<b>${formattedValue}</b>`;

					// Add color based on amount
					formattedValue = amount < 0 ? 
						`<span style='color:#ff5858'>${formattedValue}</span>` : 
						`<span style='color:#2e7d32'>${formattedValue}</span>`;

					// Add left border and tooltip if PD cheques exist
					if (data.pd_cheques) {
						const pdPercentage = ((data.pd_cheques / amount) * 100).toFixed(1);
						value = `<div style='padding-left: 8px; border-left: 3px solid ${amount < 0 ? '#ff5858' : '#2e7d32'}'>
									<span title="PD Cheques: ${pdPercentage}% of Net Outstanding">
										${formattedValue}
									</span>
								</div>`;
					} else {
						value = formattedValue;
					}
				}
			}

			// PD Cheques highlighting - only if value exists and is greater than zero
			if (column.fieldname === "pd_cheques" && flt(data.pd_cheques) > 0) {
				value = `<span style='color: #2c5282; font-weight: bold'>${value}</span>`;
			}

		} catch (e) {
			console.error("Error in formatter:", e);
			return value; // Return original formatted value if there's an error
		}

		return value;
	},

	"onload": function(report) {
		// Debounce the refresh function
		const debouncedRefresh = frappe.utils.debounce(() => {
			report.refresh();
		}, 300);

		report.page.add_inner_button(__("Refresh"), debouncedRefresh);

		// Add export button
		report.page.add_inner_button(__("Export"), function() {
			const filters = report.get_values();
			frappe.set_route("query-report", "Party Balances", filters);
		});

		// Add loading state handler
		report.page.wrapper.on('show', () => {
			frappe.show_progress('Loading Report', 70, 100);
		});
	},

	"before_run": function(report) {
		// Clear cache if date changes
		const filters = report.get_values();
		const cacheKey = `party_balances_${filters.to_date}_${filters.party_type}`;
		
		if (this.last_cache_key && this.last_cache_key !== cacheKey) {
			frappe.provide('frappe.query_reports');
			delete frappe.query_reports[report.name].data;
			delete frappe.query_reports[report.name].columns;
		}
		this.last_cache_key = cacheKey;

		// Set a reasonable page length
		frappe.query_reports[report.name].page_length = 50;

		// Add progress indicator
		frappe.show_progress('Fetching Data', 30, 100);
	},

	"after_run": function(report) {
		frappe.hide_progress();
	},

	"data_cache": {},

	"tree": false,
	"initial_depth": 3,
	"is_tree": false,
	"name_field": "party",
	
	// Add totals for currency columns
	"get_datatable_options": function(options) {
		return Object.assign(options, {
			columnTotal: {
				"closing_balance_bc": true,
				"pd_cheques": true,
				"net_amount": true,
				"range1": true,
				"range2": true,
				"range3": true,
				"range4": true,
				"range5": true
			},
			inlineFilters: true,
			layout: 'fixed',
			cellHeight: 40,
			showTotalRow: 1,
			firstRowIndex: 1,
			treeView: false,
			events: {
				onRemoveColumn: null,
				onAddColumn: null
			},
			dropdownButton: 0,
			filterRows: false,
			// Add subtle row hover effect
			cssClass: {
				'dt-row': 'hover:bg-gray-50 transition-colors duration-150'
			}
		});
	},

	// Add a function to handle post-render styling
	"after_datatable_render": function(datatable) {
		try {
			// Apply zebra striping
			$(datatable.wrapper).find('.dt-row-odd').css('background-color', '#f8fafc');

			// Add mini sparkline bars for aging buckets
			this.add_aging_indicators(datatable);

			// Add balance trend indicator
			this.add_balance_indicators(datatable);

		} catch (e) {
			console.error("Error in after_datatable_render:", e);
		}
	},

	"add_aging_indicators": function(datatable) {
		datatable.getData().forEach((row, i) => {
			if (!row) return;
			
			const data = row;
			if (!data.closing_balance_bc) return;

			// Create aging distribution bar
			const total = Math.abs(data.range1) + Math.abs(data.range2) + 
						 Math.abs(data.range3) + Math.abs(data.range4) + 
						 Math.abs(data.range5);
			
			if (total === 0) return;

			const bars = [
				Math.abs(data.range1) / total * 100,
				Math.abs(data.range2) / total * 100,
				Math.abs(data.range3) / total * 100,
				Math.abs(data.range4) / total * 100,
				Math.abs(data.range5) / total * 100
			];

			const barHtml = `
				<div style="display: flex; height: 3px; width: 100%; margin-top: 2px;">
					<div style="width: ${bars[0]}%; background: #4CAF50; height: 100%;"></div>
					<div style="width: ${bars[1]}%; background: #FFC107; height: 100%;"></div>
					<div style="width: ${bars[2]}%; background: #FF9800; height: 100%;"></div>
					<div style="width: ${bars[3]}%; background: #FF5722; height: 100%;"></div>
					<div style="width: ${bars[4]}%; background: #F44336; height: 100%;"></div>
				</div>
			`;

			// Add the bar under the party name
			const cell = $(datatable.wrapper).find(`[data-row="${i}"][data-col="${1}"]`);
			cell.append(barHtml);
		});
	},

	"add_balance_indicators": function(datatable) {
		datatable.getData().forEach((row, i) => {
			if (!row) return;
			
			const data = row;
			if (!data.closing_balance_bc) return;

			// Add a subtle indicator arrow based on net amount
			const amount = flt(data.net_amount);
			if (amount === 0) return;

			const indicator = amount > 0 ? 
				`<span style="color: #4CAF50; font-size: 8px;">▲</span>` : 
				`<span style="color: #F44336; font-size: 8px;">▼</span>`;

			// Add indicator next to amount
			const cell = $(datatable.wrapper).find(`[data-row="${i}"][data-col="${5}"]`);
			cell.prepend(indicator);
		});
	}
};
