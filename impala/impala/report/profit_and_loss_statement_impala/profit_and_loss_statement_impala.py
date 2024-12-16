# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import add_days, add_months, cint, cstr, flt, formatdate, get_first_day, getdate
from past.builtins import cmp
from six import itervalues
from impala.impala.report.financial_statements_customized import (
	get_columns,
	get_filtered_list_for_consolidated_report,
	get_period_list,
	get_accounts,
	filter_accounts,
	add_total_row,
	get_additional_conditions,
	set_gl_entries_by_account,
)


def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.period_start_date, filters.period_end_date, filters.filter_based_on, filters.periodicity,
		company=filters.company)

	conversion_factor = 1.0
	millions = 1.0
	if filters.presentation_currency and filters.conversion_rate:
		conversion_factor = filters.conversion_rate
	if filters.show_in_millions==1:
		millions = 1000000.0

	income = get_data(conversion_factor, filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	expense = get_data(conversion_factor, filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company, filters.presentation_currency)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)

	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	currency = filters.presentation_currency or frappe.get_cached_value('Company', filters.company, "default_currency")
	report_summary = get_report_summary(period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters)

	return columns, data, None, chart, report_summary

def get_report_summary(period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False):
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

	# from consolidated financial statement
	if filters.get('accumulated_in_group_company'):
		period_list = get_filtered_list_for_consolidated_report(filters, period_list)

	for period in period_list:
		key = period if consolidated else period.key
		if income:
			net_income += income[-2].get(key)
		if expense:
			net_expense += expense[-2].get(key)
		if net_profit_loss:
			net_profit += net_profit_loss.get(key)

	if (len(period_list) == 1 and periodicity== 'Yearly'):
			profit_label = _("Profit This Year")
			income_label = _("Total Income This Year")
			expense_label = _("Total Expense This Year")
	else:
		profit_label = _("Net Profit")
		income_label = _("Total Income")
		expense_label = _("Total Expense")

	return [
		{
			"value": net_income,
			"label": income_label,
			"datatype": "Currency",
			"currency": currency
		},
		{ "type": "separator", "value": "-"},
		{
			"value": net_expense,
			"label": expense_label,
			"datatype": "Currency",
			"currency": currency
		},
		{ "type": "separator", "value": "=", "color": "blue"},
		{
			"value": net_profit,
			"indicator": "Green" if net_profit > 0 else "Red",
			"label": profit_label,
			"datatype": "Currency",
			"currency": currency
		}
	]


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({'name': _('Income'), 'values': income_data})
	if expense_data:
		datasets.append({'name': _('Expense'), 'values': expense_data})
	if net_profit:
		datasets.append({'name': _('Net Profit/Loss'), 'values': net_profit})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	chart["fieldtype"] = "Currency"

	return chart


def get_data(
		conversion_factor, company, root_type, balance_must_be, period_list, filters=None,
		accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
		ignore_accumulated_values_for_fy=False , total = True):

	accounts = get_accounts(company, root_type)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	company_currency = get_appropriate_currency(company, filters)

	gl_entries_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):

		set_gl_entries_by_account(
			company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt, filters,
			gl_entries_by_account, ignore_closing_entries=ignore_closing_entries
		)

	calculate_values(filters, conversion_factor,
		accounts_by_name, gl_entries_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list)
	out = prepare_data(accounts, balance_must_be, period_list, company_currency, filters)
	out = filter_out_zero_value_rows(out, parent_children_map)

	if out and total:
		add_total_row(out, root_type, balance_must_be, period_list, company_currency)

	return out


def get_appropriate_currency(company, filters=None):
	if filters and filters.get("presentation_currency"):
		return filters["presentation_currency"]
	else:
		return frappe.get_cached_value('Company',  company,  "default_currency")


def calculate_values(filters, conversion_factor, 
		accounts_by_name, gl_entries_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy):
	for entries in itervalues(gl_entries_by_account):
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			if not d:
				frappe.msgprint(
					_("Could not retrieve information for {0}.").format(entry.account), title="Error",
					raise_exception=1
				)
			for period in period_list:
				# check if posting date is within the period

				if entry.posting_date <= period.to_date:
					if (accumulated_values or entry.posting_date >= period.from_date) and \
						(not ignore_accumulated_values_for_fy or
							entry.fiscal_year == period.to_date_fiscal_year):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit)/conversion_factor - flt(entry.credit)/conversion_factor

			if entry.posting_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0)/conversion_factor + flt(entry.debit)/conversion_factor - flt(entry.credit)/conversion_factor


def accumulate_values_into_parents(accounts, accounts_by_name, period_list):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = \
					(accounts_by_name[d.parent_account].get(period.key, 0.0) + d.get(period.key, 0.0))

			accounts_by_name[d.parent_account]["opening_balance"] = \
				(accounts_by_name[d.parent_account].get("opening_balance", 0.0) + d.get("opening_balance", 0.0))


def prepare_data(accounts, balance_must_be, period_list, company_currency, filters):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	millions = 1.0
	for d in accounts:
		# add to output
		has_value = False
		total = 0
		if d.indent==2:
			row = frappe._dict({
				"account": _(d.name),
				# "parent_account": _(d.parent_account) if d.parent_account else '',
				# "indent": flt(d.indent),
				"year_start_date": year_start_date,
				"year_end_date": year_end_date,
				"currency": company_currency,
				"include_in_gross": d.include_in_gross,
				"account_type": d.account_type,
				"is_group": d.is_group,
				"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1),
				"account_name": ('%s - %s' %(_(d.account_number), _(d.account_name))
					if d.account_number else _(d.account_name))
			})
			for period in period_list:
				if d.get(period.key) and balance_must_be == "Credit":
					# change sign based on Debit or Credit, since calculation is done using (debit - credit)
					d[period.key] *= -1
				if filters.show_in_millions==1:
					millions = 1000000.0
					row[period.key] = flt(d.get(period.key, 0.0), 3)/millions
				else:
					row[period.key] = flt(d.get(period.key, 0.0), 3)
				if abs(row[period.key]) >= 0.005:
					# ignore zero values
					has_value = True
					total += flt(row[period.key])

			row["has_value"] = has_value
			if filters.show_in_millions==1:
				millions = 1000000.0
				row["total"] = total/millions
			else:
				row["total"] = total
			data.append(row)

	return data


def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break

	return data_with_value