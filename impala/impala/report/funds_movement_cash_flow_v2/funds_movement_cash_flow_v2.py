# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import cint, cstr
from six import iteritems


def execute(filters=None):
    if (filters.get("currency_exchange")) and (filters.get("exchange_rate") == 0):
        frappe.throw("Please provide currency exchange rates")
    if filters.get("un_group") == 1:
        test = []
        data = []
        columns = get_columns(filters)
        conditions = get_conditions(filters)
        gle_conditions = get_gle_conditions(filters)
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
            currency_row["currency"] = currency.account_currency
            data.append(currency_row)
            accounts = get_account_wise_data(
                currency.account_currency, gle_conditions, filters
            )
            for account in accounts:
                credit_opening_balance = frappe.db.sql(
                    """ SELECT SUM(debit-credit) as base_opening_balance,
					SUM(debit_in_account_currency-credit_in_account_currency) as transaction_opening_balance from `tabGL Entry`
					where docstatus=1 and account='{}' and posting_date<'{}'
					""".format(
                        account.against, filters.from_date
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
                account_row["account"] = account.against
                against_accounts = get_parent_account_wise_data(
                    account.against, currency.account_currency, gle_conditions, filters
                )

                account_row["currency"] = currency.account_currency
                data.append(account_row)
                for against in against_accounts:

                    against_row = {}

                    against_row["against"] = against.account
                    against_row["currency"] = currency.account_currency
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
                    account_totals["currency"] = currency.account_currency
                    account_totals["base_flowin"] += against["base_flowin"] or 0.0
                    account_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    account_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                    currency_totals["base_flowout"] += against["base_flowout"] or 0.0
                    currency_totals["currency"] = currency.account_currency
                    currency_totals["base_flowin"] += against["base_flowin"] or 0.0
                    currency_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    currency_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                    grand_totals["base_flowout"] += against["base_flowout"] or 0.0
                    grand_totals["currency"] = currency.account_currency
                    grand_totals["base_flowin"] += against["base_flowin"] or 0.0
                    grand_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    grand_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                account_totals["account"] = f"<b>Totals for {account.against}</b>"
                data.append(account_totals)
                data.append({})

            currency_totals[
                "account_currency"
            ] = f"<b>Totals for {currency.account_currency}</b>"
            data.append(currency_totals)
        data = currency_conversion(data, filters)
        return columns, data
    else:
        test = []
        data = []
        columns = get_columns(filters)
        conditions = get_conditions(filters)
        gle_conditions = get_gle_conditions(filters)
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
            currency_row["currency"] = currency.account_currency
            data.append(currency_row)

            accounts = get_account_wise_data(
                currency.account_currency, gle_conditions, filters
            )
            for account in accounts:
                credit_opening_balance = frappe.db.sql(
                    """ SELECT SUM(debit-credit) as base_opening_balance,
					SUM(debit_in_account_currency-credit_in_account_currency) as transaction_opening_balance from `tabGL Entry`
					where docstatus=1 and account='{}' and posting_date<'{}'
					""".format(
                        account.against, filters.from_date
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
                account_row["account"] = account.parent_account

                accs = get_child_accounts_as_list(account.parent_account)
                against_accounts = get_parent_account_wise_data(
                    accs,
                    currency.account_currency,
                    gle_conditions,
                    filters,
                )
                account_row["currency"] = currency.account_currency
                data.append(account_row)
                for against in against_accounts:

                    against_row = {}

                    against_row["against"] = against.account
                    against_row["currency"] = currency.account_currency
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
                    account_totals["currency"] = currency.account_currency
                    account_totals["base_flowin"] += against["base_flowin"] or 0.0
                    account_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    account_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                    currency_totals["base_flowout"] += against["base_flowout"] or 0.0
                    currency_totals["currency"] = currency.account_currency
                    currency_totals["base_flowin"] += against["base_flowin"] or 0.0
                    currency_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    currency_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                    grand_totals["base_flowout"] += against["base_flowout"] or 0.0
                    grand_totals["currency"] = currency.account_currency
                    grand_totals["base_flowin"] += against["base_flowin"] or 0.0
                    grand_totals["transaction_flowout"] += (
                        against["transaction_flowout"] or 0.0
                    )
                    grand_totals["transaction_flowin"] += (
                        against["transaction_flowin"] or 0.0
                    )

                account_totals[
                    "account"
                ] = f"<b>Totals for {account.parent_account}</b>"
                data.append(account_totals)
                data.append({})

            currency_totals[
                "account_currency"
            ] = f"<b>Totals for {currency.account_currency}</b>"
            data.append(currency_totals)
        data = currency_conversion(data, filters)
    return columns, data


def get_child_accounts_as_list(parent):
    accs = []
    if parent:
        query_data = frappe.db.sql(
            f"""Select name from `tabAccount` where parent_account ='{parent}' """,
            as_dict=1,
        )
        if query_data:
            for i in query_data:
                accs.append(i.get("name"))
            return tuple(accs)
        else:
            return ()
    else:
        return ()


def currency_conversion(data, filters):
    exchange_rate = filters.get("exchange_rate") or 1
    for d in data:
        if filters.get("currency_exchange"):
            if (d.get("currency") == "USD") and (
                filters.get("currency_exchange") == "UGX"
            ):
                for key, val in d.items():
                    if isinstance(val, int) or isinstance(val, float):
                        d[key] = val * exchange_rate
            elif (d.get("currency") == "UGX") and (
                filters.get("currency_exchange") == "USD"
            ):
                for key, val in d.items():
                    if isinstance(val, int) or isinstance(val, float):
                        d[key] = val / exchange_rate

    return data


def get_account_currency(conditions):

    currencies = frappe.db.sql(
        """ SELECT account_currency from `tabAccount` where account_type IN ('Bank', 'Cash') {} GROUP BY account_currency""".format(
            conditions
        ),
        as_dict=1,
    )

    return currencies


def get_account_wise_data(currency, gle_conditions, filters):
    if filters.get("un_group") == 1:
        data = frappe.db.sql(
            """
				SELECT gl.against 
				FROM `tabGL Entry` gl
				INNER JOIN `tabAccount` ac on ac.name = gl.against 
				WHERE gl.docstatus=1 and gl.account_currency='{}' {} GROUP BY gl.against ORDER BY gl.against 
			""".format(
                currency, gle_conditions
            ),
            as_dict=1,
            debug=True,
        )
    else:
        data = frappe.db.sql(
            """
				SELECT gl.against, ac.parent_account
				FROM `tabGL Entry` gl
				INNER JOIN `tabAccount` ac on ac.name = gl.against 
				WHERE gl.docstatus=1 and gl.account_currency='{}' {} GROUP BY ac.parent_account ORDER BY ac.parent_account 
			""".format(
                currency, gle_conditions
            ),
            as_dict=1,
            debug=True,
        )

    return data


def get_parent_account_wise_data(name, currency, gle_conditions, filters):
    if filters.get("un_group") == 1:
        data = frappe.db.sql(
            """
				SELECT gl.account, ac.parent_account, gl.against, SUM(gl.debit_in_account_currency) as transaction_flowin, SUM(gl.credit_in_account_currency) as transaction_flowout,
				SUM(gl.debit) as base_flowin, SUM(gl.credit) as base_flowout, ac.is_group as is_group 
				FROM `tabGL Entry` gl
				Inner JOIN `tabAccount` ac on ac.name = gl.account
				WHERE ac.account_type IN ("Bank", "Cash") and gl.docstatus=1 and gl.against = '{}' and ac.account_currency='{}' {} GROUP BY gl.account ORDER BY gl.account 
			""".format(
                name, currency, gle_conditions
            ),
            as_dict=1,
            debug=True,
        )
    else:
        if len(name) > 1:
            data = frappe.db.sql(
                """
					SELECT gl.account, ac.parent_account, gl.against, SUM(gl.debit_in_account_currency) as transaction_flowin, SUM(gl.credit_in_account_currency) as transaction_flowout,
					SUM(gl.debit) as base_flowin, SUM(gl.credit) as base_flowout, ac.is_group as is_group 
					FROM `tabGL Entry` gl
					Inner JOIN `tabAccount` ac on ac.name = gl.account
					WHERE ac.account_type IN ("Bank", "Cash") and gl.docstatus=1 and gl.against in {} and ac.account_currency='{}' {} GROUP BY gl.account ORDER BY gl.account 
				""".format(
                    name, currency, gle_conditions
                ),
                as_dict=1,
                debug=True,
            )
        elif len(name) == 1:
            data = frappe.db.sql(
                """
					SELECT gl.account, ac.parent_account, gl.against, SUM(gl.debit_in_account_currency) as transaction_flowin, SUM(gl.credit_in_account_currency) as transaction_flowout,
					SUM(gl.debit) as base_flowin, SUM(gl.credit) as base_flowout, ac.is_group as is_group 
					FROM `tabGL Entry` gl
					Inner JOIN `tabAccount` ac on ac.name = gl.account
					WHERE ac.account_type IN ("Bank", "Cash") and gl.docstatus=1 and gl.against = '{}' and ac.account_currency='{}' {} GROUP BY gl.account ORDER BY gl.account 
				""".format(
                    name[0], currency, gle_conditions
                ),
                as_dict=1,
                debug=True,
            )
        else:
            data = []

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


def get_columns(filters):
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

    return columns
