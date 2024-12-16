# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import cint, cstr
from six import iteritems

from erpnext.accounts.report.financial_statements import (
    get_columns,
    get_data,
    get_filtered_list_for_consolidated_report,
    get_period_list,
)
from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import (
    get_net_profit_loss,
)
from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
    test = []

    data = []
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    gle_conditions = get_gle_conditions(filters)
    grouping = get_grouping_by(filters)

    currency_groups = get_account_currency(conditions)
    grand_totals = {
        "account_currency": "<b>Grand Totals</b>",
        "base_flowout": 0.0,
        "base_flowin": 0.0,
        "transaction_flowout": 0.0,
        "transaction_flowin": 0.0,
    }
    for currency in currency_groups:
        currency_totals = {
            "account_currency": "<b>Totals</b>",
            "base_flowout": 0.0,
            "base_flowin": 0.0,
            "transaction_flowout": 0.0,
            "transaction_flowin": 0.0,
        }
        currency_row = {}
        currency_row["account_currency"] = currency.account_currency
        data.append(currency_row)

        accounts = get_accounts(currency.account_currency, conditions)
        for account in accounts:
            credit_opening_balance = frappe.db.sql(
                """ SELECT SUM(debit-credit) as base_opening_balance,
				SUM(debit_in_account_currency-credit_in_account_currency) as transaction_opening_balance from `tabGL Entry`
				where docstatus=1 and account='{}' and posting_date<'{}'
				""".format(
                    account.name, filters.from_date
                ),
                as_list=1,
                debug=True,
            )

            account_totals = {
                "account": "",
                "base_flowout": 0.0,
                "base_flowin": 0.0,
                "transaction_flowout": 0.0,
                "transaction_flowin": 0.0,
            }

            account_row = {}
            account_row["account"] = account.name
            account_row["against"] = "Opening Balance"
            account_row["base_flowout"] = credit_opening_balance[0][0] or 0.0
            account_row["transaction_flowout"] = credit_opening_balance[0][1] or 0.0
            data.append(account_row)

            against_accounts = get_account_wise_data(
                account.name, currency.account_currency, gle_conditions
            )
            for against in against_accounts:

                against_row = {}
                against_row["against"] = against.parent_account
                against_row["base_flowin"] = against.get("base_flowin") or 0.0
                against_row["base_flowout"] = against.get("base_flowout") or 0.0
                against_row["transaction_flowin"] = (
                    against.get("transaction_flowin") or 0.0
                )
                against_row["transaction_flowout"] = (
                    against.get("transaction_flowout") or 0.0
                )
                data.append(against_row)

                account_totals["base_flowout"] += against["base_flowout"] or 0.0
                account_totals["base_flowin"] += against["base_flowin"] or 0.0
                account_totals["transaction_flowout"] += (
                    against["transaction_flowout"] or 0.0
                )
                account_totals["transaction_flowin"] += (
                    against["transaction_flowin"] or 0.0
                )

                currency_totals["base_flowout"] += against["base_flowout"] or 0.0
                currency_totals["base_flowin"] += against["base_flowin"] or 0.0
                currency_totals["transaction_flowout"] += (
                    against["transaction_flowout"] or 0.0
                )
                currency_totals["transaction_flowin"] += (
                    against["transaction_flowin"] or 0.0
                )

                grand_totals["base_flowout"] += against["base_flowout"] or 0.0
                grand_totals["base_flowin"] += against["base_flowin"] or 0.0
                grand_totals["transaction_flowout"] += (
                    against["transaction_flowout"] or 0.0
                )
                grand_totals["transaction_flowin"] += (
                    against["transaction_flowin"] or 0.0
                )

            account_totals["account"] = f"<b>Totals for {account.name}</b>"
            data.append(account_totals)

        currency_totals[
            "account_currency"
        ] = f"<b>Totals for {currency.account_currency}</b>"
        data.append(currency_totals)
    # data.append(grand_totals)

    return columns, data


def get_account_currency(conditions):

    currencies = frappe.db.sql(
        """ SELECT account_currency from `tabAccount` where account_type IN ('Bank', 'Cash') {} GROUP BY account_currency""".format(
            conditions
        ),
        as_dict=1,
    )

    return currencies


def get_accounts(currency, conditions):

    accounts = frappe.db.sql(
        """ SELECT name from `tabAccount`
		where account_type IN ("Bank", "Cash") and account_currency='{}' {} GROUP BY name """.format(
            currency, conditions
        ),
        as_dict=1,
    )
    return accounts


def get_account_wise_data(account, currency, gle_conditions):
    data = frappe.db.sql(
        """
			SELECT ac.parent_account, gl.against, SUM(gl.debit_in_account_currency) as transaction_flowin, SUM(gl.credit_in_account_currency) as transaction_flowout,
			SUM(gl.debit) as base_flowin, SUM(gl.credit) as base_flowout
			FROM `tabGL Entry` gl
			INNER JOIN `tabAccount` ac on ac.name = gl.against 
			WHERE gl.docstatus=1 and gl.account = "{}" and gl.account_currency='{}' {} GROUP BY ac.parent_account ORDER BY ac.parent_account 
		""".format(
            account, currency, gle_conditions
        ),
        as_dict=1,
        debug=True,
    )

    return data


def get_conditions(filters):
    conditions = ""

    if filters.company:
        conditions += " and company='{}'".format(filters.company)

    return conditions


def get_gle_conditions(filters):
    conditions = ""
    if filters.company:
        conditions += " and gl.company='{}'".format(filters.company)
    if filters.from_date:
        conditions += " and gl.posting_date>='{}'".format(filters.from_date)
    if filters.to_date:
        conditions += " and gl.posting_date<='{}'".format(filters.to_date)

    return conditions


def get_grouping_by(filters):
    grouping = ""
    if filters.get("group_by") == "Currency":
        grouping = "GROUP BY account_currency ORDER BY account_currency"
    if filters.get("group_by") == "Main Account":
        grouping = "GROUP BY parent_account ORDER BY parent_account"

    return grouping


def get_columns(filters):
    columns = []
    if filters.show_by == "All":
        columns = [
            {
                "fieldname": "account_currency",
                "label": _("Account Currency"),
                "fieldtype": "Link",
                "options": "Currency",
                "width": 200,
            },
            {
                "fieldname": "account",
                "label": _("Account"),
                "fieldtype": "Data",
                "options": "",
                "width": 200,
            },
            {
                "fieldname": "against",
                "label": _("Against Account"),
                "fieldtype": "Link",
                "options": "Account",
                "width": 200,
            },
            {
                "fieldname": "base_flowin",
                "label": _("Base Currency Debit"),
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "fieldname": "base_flowout",
                "label": _("Base Currency Credit"),
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "fieldname": "transaction_flowin",
                "label": _("Transaction Currency Debit"),
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "fieldname": "transaction_flowout",
                "label": _("Transaction Currency Credit"),
                "fieldtype": "Float",
                "width": 150,
            },
        ]
    if filters.show_by == "Receipts":
        columns = [
            {
                "fieldname": "account_currency",
                "label": _("Account Currency"),
                "fieldtype": "Link",
                "options": "Currency",
                "width": 200,
            },
            {
                "fieldname": "account",
                "label": _("Account"),
                "fieldtype": "Data",
                "options": "",
                "width": 200,
            },
            {
                "fieldname": "against",
                "label": _("Against Account"),
                "fieldtype": "Link",
                "options": "Account",
                "width": 200,
            },
            {
                "fieldname": "base_flowin",
                "label": _("Base Currency Debit"),
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "fieldname": "transaction_flowin",
                "label": _("Transaction Currency Debit"),
                "fieldtype": "Float",
                "width": 150,
            },
        ]

    if filters.show_by == "Payments":
        columns = [
            {
                "fieldname": "account_currency",
                "label": _("Account Currency"),
                "fieldtype": "Link",
                "options": "Currency",
                "width": 200,
            },
            {
                "fieldname": "account",
                "label": _("Account"),
                "fieldtype": "Data",
                "options": "",
                "width": 200,
            },
            {
                "fieldname": "against",
                "label": _("Against Account"),
                "fieldtype": "Link",
                "options": "Account",
                "width": 200,
            },
            {
                "fieldname": "base_flowout",
                "label": _("Base Currency Credit"),
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "fieldname": "transaction_flowout",
                "label": _("Transaction Currency Credit"),
                "fieldtype": "Float",
                "width": 150,
            },
        ]

    return columns
