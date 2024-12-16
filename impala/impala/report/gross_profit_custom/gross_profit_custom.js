// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gross Profit Custom"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		if (!data) return value;

		value = default_formatter(value, row, column, data);
		
		// Format Sales Invoice as link
		if (column.fieldname === "sales_invoice") {
			return `<a href="/app/sales-invoice/${data.sales_invoice}" style="font-weight: bold">${value}</a>`;
		}
		
		// Format Customer as link
		if (column.fieldname === "customer") {
			return `<a href="/app/customer/${data.customer}">${value}</a>`;
		}
		
		// Format Delivery Note as link(s)
		if (column.fieldname === "delivery_note" && value) {
			let notes = value.split(', ');
			if (notes.length > 1) {
				let links = notes.map(dn => `<a href="/app/delivery-note/${dn}">${dn}</a>`);
				return `${links[0]} (+${notes.length - 1})`;
			}
			return `<a href="/app/delivery-note/${value}">${value}</a>`;
		}
		
		// Format currency values
		if (["selling_amount", "buying_amount", "gross_profit"].includes(column.fieldname)) {
			value = format_currency(value, data.currency);
			
			if (column.fieldname === "gross_profit") {
				if (flt(value) < 0) {
					return `<span style="color: var(--red-500); font-weight: bold">${value}</span>`;
				}
				return `<span style="color: var(--green-500); font-weight: bold">${value}</span>`;
			}
			return `<span style="font-family: monospace">${value}</span>`;
		}
		
		// Format percentage values
		if (column.fieldname === "gross_profit_percent") {
			let gross_profit = flt(data.gross_profit);
			let selling_amount = flt(data.selling_amount);

			// Calculate percentage if not already calculated
			let percent = selling_amount ? (gross_profit / selling_amount) * 100 : 0;
			let formatted = percent.toFixed(2) + '%';

			if (percent < 0) {
				return `<span style="color: var(--red-500); font-weight: bold">${formatted}</span>`;
			} else if (percent < 15) {
				return `<span style="color: var(--orange-500); font-weight: bold">${formatted}</span>`;
			} else if (percent < 25) {
				return `<span style="color: var(--yellow-500); font-weight: bold">${formatted}</span>`;
			} else {
				return `<span style="color: var(--green-500); font-weight: bold">${formatted}</span>`;
			}
		}
		
		return value;
	},
	
	"get_datatable_options": function(options) {
		return Object.assign(options, {
			cellHeight: 40,
			editable: false,
			dropdownButton: false,
			inlineFilters: true
		});
	},
	
	onload: function(report) {
		// Add chart button
		report.page.add_inner_button(__('Show Chart'), function() {
			let chart_data = {
				data: {
					labels: report.data.map(d => d.sales_invoice),
					datasets: [
						{
							name: "Gross Profit",
							chartType: 'bar',
							values: report.data.map(d => flt(d.gross_profit))
						},
						{
							name: "Profit %",
							chartType: 'line',
							values: report.data.map(d => flt(d.gross_profit_percent))
						}
					]
				},
				type: 'axis-mixed',
				height: 300,
				colors: ['#28a745', '#5e64ff'],
				tooltipOptions: {
					formatTooltipY: (value, type) => {
						return type === 'line' ? 
							format_number(value, null, 2) + '%' :
							format_currency(value);
					}
				}
			};
			
			report.show_chart = !report.show_chart;
			if (report.show_chart) {
				report.chart_options = chart_data;
			} else {
				report.chart_options = null;
			}
			report.refresh();
		});
		
		// Add summary button
		report.page.add_inner_button(__('Show Summary'), function() {
			let summary = getSummary(report.data);
			let d = new frappe.ui.Dialog({
				title: __('Gross Profit Summary'),
				fields: [{
					fieldtype: 'HTML',
					fieldname: 'summary_html',
					options: `
						<div style="padding: 15px">
							<div style="margin-bottom: 15px; border-bottom: 1px solid #d1d8dd; padding-bottom: 10px">
								<div style="font-size: 12px; color: #666">Total Invoices</div>
								<div style="font-size: 24px; font-weight: bold">${summary.invoice_count}</div>
							</div>
							<div style="margin-bottom: 15px; border-bottom: 1px solid #d1d8dd; padding-bottom: 10px">
								<div style="font-size: 12px; color: #666">Total Sales</div>
								<div style="font-size: 20px; font-weight: bold">
									${format_currency(summary.total_sales)}
								</div>
							</div>
							<div style="margin-bottom: 15px; border-bottom: 1px solid #d1d8dd; padding-bottom: 10px">
								<div style="font-size: 12px; color: #666">Total Profit</div>
								<div style="font-size: 20px; font-weight: bold; color: ${summary.total_profit >= 0 ? '#28a745' : '#ff5858'}">
									${format_currency(summary.total_profit)}
								</div>
							</div>
							<div>
								<div style="font-size: 12px; color: #666">Average Profit %</div>
								<div style="font-size: 20px; font-weight: bold; color: ${getColorForProfit(summary.avg_profit_percent)}">
									${format_number(summary.avg_profit_percent, null, 2)}%
								</div>
							</div>
						</div>
					`
				}]
			});
			d.show();
		});
	}
};

function getSummary(data) {
	let summary = {
		total_sales: 0,
		total_profit: 0,
		invoice_count: data.length
	};
	
	data.forEach(row => {
		summary.total_sales += flt(row.selling_amount);
		summary.total_profit += flt(row.gross_profit);
	});
	
	summary.avg_profit_percent = (summary.total_profit / summary.total_sales * 100) || 0;
	
	return summary;
}

function getColorForProfit(percent) {
	if (percent < 0) return '#ff5858';
	if (percent < 15) return '#ff9f43';
	if (percent < 25) return '#ffc107';
	return '#28a745';
}

// Helper function to safely convert to float
function flt(value, precision = null) {
	if (value === null || value === undefined || value === '') return 0.0;
	let float_val = parseFloat(value);
	if (isNaN(float_val)) return 0.0;
	if (precision !== null) {
		return Number(float_val.toFixed(precision));
	}
	return float_val;
}
