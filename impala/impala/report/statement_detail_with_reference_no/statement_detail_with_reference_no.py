# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import cstr, getdate
from datetime import datetime, date
from six import iteritems

from erpnext import get_company_currency, get_default_company
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
    get_dimension_with_children,
)
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.utils import get_account_currency
from frappe.utils import (
    add_days,
    getdate,
    formatdate,
    nowdate,
    today,
    get_first_day,
    date_diff,
    add_years,
    flt,
    cint,
    getdate,
    now,
)

# to cache translations
TRANSLATIONS = frappe._dict()


def execute(filters=None):
    if not filters:
        return [], []
    ageing_data = {"30": 0.0, "60": 0.0, "90": 0.0, "120": 0.0, "above": 0.0}
    account_details = {}

    if (
        filters
        and filters.get("print_in_account_currency")
        and not filters.get("account")
    ):
        frappe.throw(_("Select an account to print in account currency"))

    for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
        account_details.setdefault(acc.name, acc)

    if filters.get("party"):
        filters.party = frappe.parse_json(filters.get("party"))

    validate_filters(filters, account_details)

    validate_party(filters)

    filters = set_account_currency(filters)

    columns = get_columns(filters)

    update_translations()

    data = get_result(filters, account_details, ageing_data)
    summary = []

    summary_sales_return = get_supplier_customer_sales_return(filters)

    data[-1]["sales_to_return"] = summary_sales_return
    data[-1]["ageing_data"] = ageing_data

    headers = get_header(filters)

    chart = get_chart(filters)

    cheque_list_detail = get_pd_cheque_detail(filters)
    total_final_dues_after_pd = 0.0
    total_pd_amount = 0.00

    totals_pds = {}
    totals_balance = {}
    totals_after_pd = {}
    if cheque_list_detail:
        for d in cheque_list_detail:
            # due_n_balance = data[-1]["balance"]
            # check_amount_total = cheque_list_detail[-1]["p_paid_amount"] or 0.0
            # final_dues_after_pd = due_n_balance - check_amount_total
            total_pd_amount += d.get("p_paid_amount")

        total_final_dues_after_pd = data[-1]["balance"] - total_pd_amount
        totals_pds.update(
            {"pd_reference_no": "Total PDs", "p_paid_amount": total_pd_amount}
        )
        totals_balance.update(
            {"pd_reference_no": "Due Amount", "p_paid_amount": data[-1]["balance"]}
        )
        totals_after_pd.update(
            {
                "pd_reference_no": "Due Amount After PDs",
                "p_paid_amount": total_final_dues_after_pd,
            }
        )

    customer_personal_detial = {}
    customer_detail = ""
    address_doc = ""

    if filters.get("party_type") and filters.get("party"):
        filters.party = frappe.parse_json(filters.get("party"))

        party = str(filters.party[0])

        if filters.get("party_type") == "Supplier":

            customer_detail = frappe.db.get_value(
                "Supplier",
                {"name": party},
                ["supplier_name", "supplier_primary_address", "company"],
                as_dict=1,
            )
            if customer_detail:
                customer_personal_detial["customer_name"] = customer_detail.get(
                    "supplier_name"
                )
                if customer_detail.get("supplier_primary_address"):
                    address_doc = frappe.get_doc(
                        "Address", customer_detail.get("supplier_primary_address")
                    )

        elif filters.get("party_type") == "Customer":
            customer_detail = frappe.db.get_value(
                "Customer",
                {"name": party},
                ["customer_name", "customer_primary_address", "company"],
                as_dict=1,
            )

            if customer_detail:
                customer_personal_detial["customer_name"] = customer_detail.get(
                    "customer_name"
                )
                if customer_detail.get("customer_primary_address"):
                    address_doc = frappe.get_doc(
                        "Address", customer_detail.get("customer_primary_address")
                    )

        if customer_detail:
            if address_doc:
                customer_personal_detial["email_id"] = address_doc.get("email_id") or ""
                customer_personal_detial["address_line1"] = (
                    address_doc.get("address_line1") or ""
                )
                customer_personal_detial["city"] = address_doc.get("city") or ""
                customer_personal_detial["country"] = address_doc.get("country") or ""
                customer_personal_detial["pincode"] = address_doc.get("pincode") or ""
            else:
                customer_personal_detial["email_id"] = ""
                customer_personal_detial["address_line1"] = ""
                customer_personal_detial["city"] = ""
                customer_personal_detial["country"] = ""
                customer_personal_detial["pincode"] = ""
            customer_personal_detial["due_balance"] = frappe.utils.fmt_money(
                data[-1]["balance"] or 0
            )
            customer_personal_detial["currency"] = frappe.db.get_value(
                "Customer", {"name": party}, "default_currency"
            )
    if data[-1]:
        summary.append(
            {
                "label": "Sales",
                "value": frappe.utils.fmt_money(data[-2]["debit"] or 0),
                "color": "#456789",
            }
        )
        summary.append(
            {
                "label": "Sales Return",
                "value": frappe.utils.fmt_money(summary_sales_return or 0),
                "color": "#EE8888",
            }
        )
        summary.append(
            {
                "label": "Payment",
                "value": frappe.utils.fmt_money(data[-2]["credit"] or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Due Balance",
                "value": frappe.utils.fmt_money(data[-1]["balance"] or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Age 30",
                "value": frappe.utils.fmt_money(ageing_data.get("30") or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Age 60",
                "value": frappe.utils.fmt_money(ageing_data.get("60") or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Age 90",
                "value": frappe.utils.fmt_money(ageing_data.get("90") or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Age 120",
                "value": frappe.utils.fmt_money(ageing_data.get("120") or 0),
                "color": "#FFBB00",
            }
        )

        summary.append(
            {
                "label": "Age 120 +",
                "value": frappe.utils.fmt_money(ageing_data.get("above") or 0),
                "color": "#FFBB00",
            }
        )
        summary.append(
            {
                "label": "PD Cheques Totals",
                "value": total_pd_amount,
                "color": "#FFBB00",
            }
        )

    data[-1]["headers"] = headers
    data[-1]["customer_personal_detial"] = customer_personal_detial
    data[-1]["cheque_list"] = cheque_list_detail
    data[-1]["totals_pds"] = totals_pds
    data[-1]["totals_balance"] = totals_balance
    data[-1]["totals_after_pd"] = totals_after_pd

    return (columns, data, None, chart, summary)


def update_translations():
    TRANSLATIONS.update(
        dict(
            OPENING=_("Opening"),
            TOTAL=_("Total"),
            CLOSING_TOTAL=_("Closing (Opening + Total)"),
        )
    )


def validate_filters(filters, account_details):
    if not filters.get("company"):
        frappe.throw(_("{0} is mandatory").format(_("Company")))

    if not filters.get("from_date") and not filters.get("to_date"):
        frappe.throw(
            _("{0} and {1} are mandatory").format(
                frappe.bold(_("From Date")), frappe.bold(_("To Date"))
            )
        )

    if filters.get("account"):
        filters.account = frappe.parse_json(filters.get("account"))
        for account in filters.account:
            if not account_details.get(account):
                frappe.throw(_("Account {0} does not exists").format(account))

    if filters.get("account") and filters.get("group_by") == "Group by Account":
        filters.account = frappe.parse_json(filters.get("account"))
        for account in filters.account:
            if account_details[account].is_group == 0:
                frappe.throw(
                    _("Can not filter based on Child Account, if grouped by Account")
                )

    if filters.get("voucher_no") and filters.get("group_by") in ["Group by Voucher"]:
        frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"))

    if filters.get("project"):
        filters.project = frappe.parse_json(filters.get("project"))

    if filters.get("cost_center"):
        filters.cost_center = frappe.parse_json(filters.get("cost_center"))


def validate_party(filters):
    party_type, party = filters.get("party_type"), filters.get("party")

    if party and party_type:
        for d in party:
            if not frappe.db.exists(party_type, d):
                frappe.throw(_("Invalid {0}: {1}").format(party_type, d))


def set_account_currency(filters):
    if filters.get("account") or (filters.get("party") and len(filters.party) == 1):
        filters["company_currency"] = frappe.get_cached_value(
            "Company", filters.company, "default_currency"
        )
        account_currency = None

        if filters.get("account"):
            if len(filters.get("account")) == 1:
                account_currency = get_account_currency(filters.account[0])
            else:
                currency = get_account_currency(filters.account[0])
                is_same_account_currency = True
                for account in filters.get("account"):
                    if get_account_currency(account) != currency:
                        is_same_account_currency = False
                        break

                if is_same_account_currency:
                    account_currency = currency

        elif filters.get("party"):
            gle_currency = frappe.db.get_value(
                "GL Entry",
                {
                    "party_type": filters.party_type,
                    "party": filters.party[0],
                    "company": filters.company,
                },
                "account_currency",
            )

            if gle_currency:
                account_currency = gle_currency
            else:
                account_currency = (
                    None
                    if filters.party_type
                    in ["Employee", "Student", "Shareholder", "Member"]
                    else frappe.db.get_value(
                        filters.party_type, filters.party[0], "default_currency"
                    )
                )

        filters["account_currency"] = account_currency or filters.company_currency
        if (
            filters.account_currency != filters.company_currency
            and not filters.presentation_currency
        ):
            filters.presentation_currency = filters.account_currency

    return filters


def get_result(filters, account_details, ageing_data):
    accounting_dimensions = []
    if filters.get("include_dimensions"):
        accounting_dimensions = get_accounting_dimensions()

    gl_entries = get_gl_entries(filters, accounting_dimensions)

    data = get_data_with_opening_closing(
        filters, account_details, accounting_dimensions, gl_entries, ageing_data
    )

    result = get_result_as_list(data, filters)

    return result


def get_gl_entries(filters, accounting_dimensions):
    currency_map = get_currency(filters)
    select_fields = """, debit, credit, debit_in_account_currency,
        credit_in_account_currency """

    order_by_statement = "order by posting_date, account, creation"

    if filters.get("include_dimensions"):
        order_by_statement = "order by posting_date, creation"

    if filters.get("group_by") == "Group by Voucher":
        order_by_statement = "order by posting_date, voucher_type, voucher_no"
    if filters.get("group_by") == "Group by Account":
        order_by_statement = "order by account, posting_date, creation"

    if filters.get("include_default_book_entries"):
        filters["company_fb"] = frappe.db.get_value(
            "Company", filters.get("company"), "default_finance_book"
        )

    dimension_fields = ""
    if accounting_dimensions:
        dimension_fields = ", ".join(accounting_dimensions) + ","

    distributed_cost_center_query = ""
    if filters and filters.get("cost_center"):
        select_fields_with_percentage = """, debit*(DCC_allocation.percentage_allocation/100) as debit,
        credit*(DCC_allocation.percentage_allocation/100) as credit,
        debit_in_account_currency*(DCC_allocation.percentage_allocation/100) as debit_in_account_currency,
        credit_in_account_currency*(DCC_allocation.percentage_allocation/100) as credit_in_account_currency """

        distributed_cost_center_query = """
        UNION ALL
        SELECT name as gl_entry,
            posting_date,
            account,
            party_type,
            party,
            voucher_type,
            voucher_no, {dimension_fields}
            cost_center, project,
            against_voucher_type,
            against_voucher,
            account_currency,
            remarks, against,
            is_opening, `tabGL Entry`.creation {select_fields_with_percentage}
        FROM `tabGL Entry`,
        (
            SELECT parent, sum(percentage_allocation) as percentage_allocation
            FROM `tabDistributed Cost Center`
            WHERE cost_center IN %(cost_center)s
            AND parent NOT IN %(cost_center)s
            GROUP BY parent
        ) as DCC_allocation
        WHERE company=%(company)s
        {conditions}
        AND posting_date <= %(to_date)s
        AND cost_center = DCC_allocation.parent
        """.format(
            dimension_fields=dimension_fields,
            select_fields_with_percentage=select_fields_with_percentage,
            conditions=get_conditions(filters).replace(
                "and cost_center in %(cost_center)s ", ""
            ),
        )

    gl_entries = frappe.db.sql(
        """
        select
            name as gl_entry, posting_date, account, party_type, party,
            voucher_type, voucher_no, {dimension_fields}
            cost_center, project,
            against_voucher_type, against_voucher, account_currency,
            remarks, against, is_opening, creation {select_fields}
        from `tabGL Entry`
        where company=%(company)s {conditions}
        {distributed_cost_center_query}
        {order_by_statement}
        """.format(
            dimension_fields=dimension_fields,
            select_fields=select_fields,
            conditions=get_conditions(filters),
            distributed_cost_center_query=distributed_cost_center_query,
            order_by_statement=order_by_statement,
        ),
        filters,
        as_dict=1,
    )

    if filters.get("presentation_currency"):
        return convert_to_presentation_currency(
            gl_entries, currency_map, filters.get("company")
        )
    else:
        return gl_entries


def get_conditions(filters):
    conditions = []

    if filters.get("account"):
        filters.account = get_accounts_with_children(filters.account)
        conditions.append("account in %(account)s")

    if filters.get("cost_center"):
        filters.cost_center = get_cost_centers_with_children(filters.cost_center)
        conditions.append("cost_center in %(cost_center)s")

    if filters.get("voucher_no"):
        conditions.append("voucher_no=%(voucher_no)s")

    if filters.get("group_by") == "Group by Party" and not filters.get("party_type"):
        conditions.append("party_type in ('Customer', 'Supplier')")

    if filters.get("party_type"):
        conditions.append("party_type=%(party_type)s")

    if filters.get("party"):
        conditions.append("party in %(party)s")

    if not (
        filters.get("account")
        or filters.get("party")
        or filters.get("group_by") in ["Group by Account", "Group by Party"]
    ):
        conditions.append("posting_date >=%(from_date)s")

    conditions.append("(posting_date <=%(to_date)s or is_opening = 'Yes')")

    if filters.get("project"):
        conditions.append("project in %(project)s")

    if filters.get("finance_book"):
        if filters.get("include_default_book_entries"):
            conditions.append(
                "(finance_book in (%(finance_book)s, %(company_fb)s, '') OR finance_book IS NULL)"
            )
        else:
            conditions.append("finance_book in (%(finance_book)s)")

    if not filters.get("show_cancelled_entries"):
        conditions.append("is_cancelled = 0")

    from frappe.desk.reportview import build_match_conditions

    match_conditions = build_match_conditions("GL Entry")

    if match_conditions:
        conditions.append(match_conditions)

    if filters.get("include_dimensions"):
        accounting_dimensions = get_accounting_dimensions(as_list=False)

        if accounting_dimensions:
            for dimension in accounting_dimensions:
                if not dimension.disabled:
                    if filters.get(dimension.fieldname):
                        if frappe.get_cached_value(
                            "DocType", dimension.document_type, "is_tree"
                        ):
                            filters[dimension.fieldname] = get_dimension_with_children(
                                dimension.document_type,
                                filters.get(dimension.fieldname),
                            )
                            conditions.append(
                                "{0} in %({0})s".format(dimension.fieldname)
                            )
                        else:
                            conditions.append(
                                "{0} in (%({0})s)".format(dimension.fieldname)
                            )

    return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_accounts_with_children(accounts):
    if not isinstance(accounts, list):
        accounts = [d.strip() for d in accounts.strip().split(",") if d]

    all_accounts = []
    for d in accounts:
        if frappe.db.exists("Account", d):
            lft, rgt = frappe.db.get_value("Account", d, ["lft", "rgt"])
            children = frappe.get_all(
                "Account", filters={"lft": [">=", lft], "rgt": ["<=", rgt]}
            )
            all_accounts += [c.name for c in children]
        else:
            frappe.throw(_("Account: {0} does not exist").format(d))

    return list(set(all_accounts))


def get_data_with_opening_closing(
    filters, account_details, accounting_dimensions, gl_entries, ageing_data
):
    data = []

    gle_map = initialize_gle_map(gl_entries, filters)

    totals, entries = get_accountwise_gle(
        filters, accounting_dimensions, gl_entries, gle_map, ageing_data
    )

    # Opening for filtered account
    data.append(totals.opening)

    if filters.get("group_by") != "Group by Voucher (Consolidated)":
        for acc, acc_dict in iteritems(gle_map):
            # acc
            if acc_dict.entries:
                # opening
                data.append({})
                if filters.get("group_by") != "Group by Voucher":
                    data.append(acc_dict.totals.opening)

                data += acc_dict.entries

                # totals
                data.append(acc_dict.totals.total)

                # closing
                if filters.get("group_by") != "Group by Voucher":
                    data.append(acc_dict.totals.closing)
        data.append({})
    else:
        data += entries

    # totals
    data.append(totals.total)

    # closing
    data.append(totals.closing)

    return data


def get_totals_dict():
    def _get_debit_credit_dict(label):
        return _dict(
            account="'{0}'".format(label),
            debit=0.0,
            credit=0.0,
            debit_in_account_currency=0.0,
            credit_in_account_currency=0.0,
        )

    return _dict(
        opening=_get_debit_credit_dict(TRANSLATIONS.OPENING),
        total=_get_debit_credit_dict(TRANSLATIONS.TOTAL),
        closing=_get_debit_credit_dict(TRANSLATIONS.CLOSING_TOTAL),
    )


def group_by_field(group_by):
    if group_by == "Group by Party":
        return "party"
    elif group_by in ["Group by Voucher (Consolidated)", "Group by Account"]:
        return "account"
    else:
        return "voucher_no"


def initialize_gle_map(gl_entries, filters):
    gle_map = OrderedDict()
    group_by = group_by_field(filters.get("group_by"))

    for gle in gl_entries:
        gle_map.setdefault(
            gle.get(group_by), _dict(totals=get_totals_dict(), entries=[])
        )
    return gle_map


def get_accountwise_gle(
    filters, accounting_dimensions, gl_entries, gle_map, ageing_data
):
    totals = get_totals_dict()
    entries = []
    consolidated_gle = OrderedDict()
    group_by = group_by_field(filters.get("group_by"))
    group_by_voucher_consolidated = (
        filters.get("group_by") == "Group by Voucher (Consolidated)"
    )

    if filters.get("show_net_values_in_party_account"):
        account_type_map = get_account_type_map(filters.get("company"))

    def update_value_in_dict(data, key, gle):
        data[key].debit += gle.debit
        data[key].credit += gle.credit

        data[key].debit_in_account_currency += gle.debit_in_account_currency
        data[key].credit_in_account_currency += gle.credit_in_account_currency

        if filters.get("show_net_values_in_party_account") and account_type_map.get(
            data[key].account
        ) in ("Receivable", "Payable"):
            net_value = data[key].debit - data[key].credit
            net_value_in_account_currency = (
                data[key].debit_in_account_currency
                - data[key].credit_in_account_currency
            )

            if net_value < 0:
                dr_or_cr = "credit"
                rev_dr_or_cr = "debit"
            else:
                dr_or_cr = "debit"
                rev_dr_or_cr = "credit"

            data[key][dr_or_cr] = abs(net_value)
            data[key][dr_or_cr + "_in_account_currency"] = abs(
                net_value_in_account_currency
            )
            data[key][rev_dr_or_cr] = 0
            data[key][rev_dr_or_cr + "_in_account_currency"] = 0

        if data[key].against_voucher and gle.against_voucher:
            data[key].against_voucher += ", " + gle.against_voucher

    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    show_opening_entries = filters.get("show_opening_entries")

    # frappe.msgprint(str(filters.get("party")))
    if filters.get("party"):
        party = list(filters.get("party"))
        party = party[0]
    else:
        party = []
    # frappe.msgprint(str(party))

    summary_filters = {
        "company": filters.get("company"),
        "report_date": filters.get("to_date"),
        "ageing_based_on": "Posting Date",
        "range1": 30,
        "range2": 60,
        "range3": 90,
        "range4": 120,
        "customer": party,
    }

    summary_data = get_summary(summary_filters)
    # frappe.log_error(summary_data, "statement detail report summary_data")
    if summary_data[1]:
        summary_data = summary_data[1][0]
        ageing_data["30"] = summary_data.get("range1") or 0
        ageing_data["60"] = summary_data.get("range2") or 0
        ageing_data["90"] = summary_data.get("range3") or 0
        ageing_data["120"] = summary_data.get("range4") or 0
        ageing_data["above"] = summary_data.get("range5") or 0

    for gle in gl_entries:
        # previous used function 'get_ageing' code job is done here

        net_value = gle.debit - gle.credit
        # if from_date and to_date:
        #     difference_days = to_date - gle.posting_date
        #     if difference_days.days <= 30:
        #         ageing_data["30"] += net_value
        #     if difference_days.days >= 31 and difference_days.days <= 60:
        #         ageing_data["60"] += net_value
        #     if difference_days.days >= 61 and difference_days.days <= 90:
        #         ageing_data["90"] += net_value
        #     if difference_days.days >= 91 and difference_days.days <= 120:
        #         ageing_data["120"] += net_value
        #     if difference_days.days >= 121:
        #         ageing_data["above"] += net_value

        # ends here aging

        group_by_value = gle.get(group_by)

        if gle.posting_date < from_date or (
            cstr(gle.is_opening) == "Yes" and not show_opening_entries
        ):
            if not group_by_voucher_consolidated:
                update_value_in_dict(gle_map[group_by_value].totals, "opening", gle)
                update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)

            update_value_in_dict(totals, "opening", gle)
            update_value_in_dict(totals, "closing", gle)

        elif gle.posting_date <= to_date:
            if not group_by_voucher_consolidated:
                update_value_in_dict(gle_map[group_by_value].totals, "total", gle)
                update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)
                update_value_in_dict(totals, "total", gle)
                update_value_in_dict(totals, "closing", gle)

                gle_map[group_by_value].entries.append(gle)

            elif group_by_voucher_consolidated:
                keylist = [
                    gle.get("voucher_type"),
                    gle.get("voucher_no"),
                    gle.get("account"),
                ]
                if filters.get("include_dimensions"):
                    for dim in accounting_dimensions:
                        keylist.append(gle.get(dim))
                    keylist.append(gle.get("cost_center"))

                key = tuple(keylist)
                if key not in consolidated_gle:
                    consolidated_gle.setdefault(key, gle)
                else:
                    update_value_in_dict(consolidated_gle, key, gle)

    for key, value in consolidated_gle.items():
        update_value_in_dict(totals, "total", value)
        update_value_in_dict(totals, "closing", value)
        entries.append(value)

    return totals, entries


def get_account_type_map(company):
    account_type_map = frappe._dict(
        frappe.get_all(
            "Account",
            fields=["name", "account_type"],
            filters={"company": company},
            as_list=1,
        )
    )

    return account_type_map


def get_result_as_list(data, filters):
    balance, balance_in_account_currency = 0, 0
    inv_details = get_supplier_invoice_details()
    # frappe.msgprint(str(inv_details))
    # frappe.msgprint(str(data))
    for d in data:
        if not d.get("posting_date"):
            balance, balance_in_account_currency = 0, 0

        balance = get_balance(d, balance, "debit", "credit")
        d["balance"] = balance

        d["account_currency"] = filters.account_currency
        d["bill_no"] = inv_details.get(d.get("against_voucher"), "")

        if d.get("voucher_type") == "Sales Invoice":
            ref = frappe.db.get_value(
                "Sales Invoice", {"name": d.get("voucher_no")}, "customer_order_number"
            )

            d["outstanding"] = frappe.db.get_value(
                "Sales Invoice", {"name": d.get("voucher_no")}, "outstanding_amount"
            )
            d["client_project_reference"] = frappe.db.get_value(
                "Sales Invoice",
                {"name": d.get("voucher_no")},
                "client_project_reference",
            )
            d["ref_number"] = ref
        elif d.get("voucher_type") == "Payment Entry":
            ref = frappe.db.get_value(
                "Payment Entry", {"name": d.get("voucher_no")}, "reference_no"
            )
            d["ref_number"] = ref
        else:
            d["ref_number"] = ""

    return data


def get_supplier_invoice_details():
    inv_details = {}
    for d in frappe.db.sql(
        """ select name, bill_no from `tabPurchase Invoice`
        where docstatus = 1 and bill_no is not null and bill_no != '' """,
        as_dict=1,
    ):
        inv_details[d.name] = d.bill_no

    return inv_details


def get_balance(row, balance, debit_field, credit_field):
    balance += row.get(debit_field, 0) - row.get(credit_field, 0)

    return balance


def get_columns(filters):
    if filters.get("presentation_currency"):
        currency = filters["presentation_currency"]
    else:
        if filters.get("company"):
            currency = get_company_currency(filters["company"])
        else:
            company = get_default_company()
            currency = get_company_currency(company)

    columns = [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90,
        },
        {"label": _("Description"), "fieldname": "voucher_type", "width": 140},
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180,
        },
        {
            "label": _("Refrence/Cheque No"),
            "fieldname": "ref_number",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Client Project Reference"),
            "fieldname": "client_project_reference",
            "fieldtype": "Data",
            "width": 180,
        },
        {"label": _("Allocation"), "fieldname": "against_voucher", "width": 140},
        {
            "label": _("Invoice Outstanding"),
            "fieldname": "outstanding",
            "fieldtype": "Float",
            "width": 150,
        },
        {"label": _("Debit"), "fieldname": "debit", "fieldtype": "Float", "width": 100},
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Float",
            "width": 130,
        },
    ]

    return columns


def get_supplier_customer_sales_return(filters):

    totol_return = 0.0
    doctype_name = "Sales Invoice"

    conditions = ""
    supplier_conditions = ""
    if filters.get("party_type") and filters.get("party"):
        filters.party = frappe.parse_json(filters.get("party"))
        party = str(filters.party[0])

        if filters.get("party_type") == "Customer":
            conditions += " and customer =  '{}' ".format(party)

        if filters.get("party_type") == "Supplier":
            conditions += " and supplier =  '{}' ".format(party)
            doctype_name = "Purchase Invoice"

    if filters.get("from_date"):
        conditions += " and posting_date >= '{}' ".format(filters.get("from_date"))

    if filters.get("to_date"):
        conditions += " and posting_date <= '{}' ".format(filters.get("to_date"))

    sales_return = frappe.db.sql(
        """ SELECT sum(grand_total) as total_return 
        FROM `tab{}` WHERE docstatus = 1 and is_return=1 
        {} """.format(
            doctype_name, conditions
        ),
        as_dict=1,
    )
    if sales_return:
        if sales_return[0].get("total_return"):
            totol_return = sales_return[0].get("total_return")

    return totol_return


def get_pd_cheque_detail(filters):
    cheque_list = []
    if filters.get("party_type") and filters.get("party"):
        filters.party = frappe.parse_json(filters.get("party"))
        party = str(filters.party[0])
        data = []
        
        cheque_list = frappe.db.sql(
            """ 
            select name as pd_cheque_name, DATE_FORMAT(posting_date, "%d/%m/%Y") as pd_posting_date,   
            reference_no  as pd_reference_no,
            DATE_FORMAT(reference_date,"%d/%m/%Y") as pd_reference_date, 
            base_amount as p_paid_amount
            from `tabPosted Dated Cheques`
            where docstatus=1 and status='Pending' and party_type = '{}' and party = '{}'

         """.format(
                filters.get("party_type"), party
            ),
            as_dict=1,
        )

    return cheque_list


def get_header(filters):
    header = frappe.db.get_value("Letter Head", {"is_default": 1}, "content")
    company_details = frappe.db.get_list(
        "Company",
        filters={"name": filters.company},
        fields=[
            "company_name",
            "phone_no",
            "email",
            "tax_id",
            "company_logo",
            "website",
        ],
    )
    comapny_address_line1 = ""
    comapny_city = ""
    comapny_counrty = ""
    comapny_state = ""
    phone = ""

    company_address_name = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": filters.company},
        "parent",
    )

    if company_address_name:
        address = frappe.db.get_value(
            "Address",
            company_address_name,
            [
                "address_line1",
                "address_title",
                "city",
                "country",
                "state",
                "email_id",
                "phone",
            ],
            as_dict=1,
        )

        comapny_address_line1 = address.address_line1
        comapny_city = address.city
        comapny_counrty = address.country
        comapny_state = address.state

        phone = address.phone
    header_updated = frappe.render_template(
        header,
        {
            "company": company_details[0].company_name,
            "company_address": comapny_address_line1,
            "city": comapny_city,
            "country": comapny_counrty,
            "state": comapny_state,
            "phone_no": phone,
            "email": company_details[0].email,
            "pin_no": company_details[0].tax_id,
            "company_logo": company_details[0].company_logo,
            "website": company_details[0].website,
        },
    )
    # data = """<div id="header-html" class = "margin-top-15"   style = " margin-top:-20px  !important; width:92.2%; margin-left:15px !important">
    # <div class = "row" style = "">
    #   <div class = "col-xs-8" style = "width:100%;   float:left; border:1px solid black ">

    #       {0}

    #           <b>Customer Statement</b>

    #   </div>

    # </div>"""

    import datetime

    d = datetime.date.today()
    today_date = d.strftime("%d-%m-%Y")

    data = """ 
<div id="header-html" class = "margin-top-15"   style = " margin-top:-20px  !important; width:92.2%; margin-left:15px !important">
    <div class = "row" style = "">

        <div class = "col-xs-10" style = "width:100%;   float:left; border:1px solid black ">
            
            
            {}
                      

            <table  class = "table table-sm" style = "width:28%; font-size:10px  "> 
                <tr>
                    <td colspan = "2"> <center>  <span style = ""> 
                    <b style = "font-size:11px">   {} Statement </b> </span> </center>  </td>
                </tr>

                <tr>
                    <td colspan = "2"> <center>  <span style = ""> 
                    <b style = "font-size:11px">  Date {}  </b> </span> </center>  </td>
                </tr>


            </table>


        </div>
</div>


</div>


    """

    return data.format(header_updated, filters.get("party_type"), today_date)


def get_chart(filters):
    chart = {
        "data": {
            "labels": [],
            "datasets": [
                {"name": "Sales", "values": []},
                {"name": "Return", "values": []},
                {"name": "Payment", "values": []},
            ],
        },
        "type": "bar",
        "colors": ["#456789", "#EE8888", "#7E77BF"],
    }

    month = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    payment_conditions_supplier = ""
    payment_conditions = ""
    payment_doctype = "Purchase Entry"
    conditions = ""
    doctype_name = "Sales Invoice"

    if filters.get("from_date"):
        conditions += " and posting_date >=  '{}' ".format(filters.get("from_date"))
        payment_conditions += " and posting_date >=  '{}' ".format(
            filters.get("from_date")
        )

    if filters.get("to_date"):
        conditions += " and posting_date <=  '{}' ".format(filters.get("to_date"))
        payment_conditions += " and posting_date <=  '{}' ".format(
            filters.get("to_date")
        )

    if filters.get("party_type") and filters.get("party"):
        filters.party = frappe.parse_json(filters.get("party"))
        party = str(filters.party[0])

        if filters.get("party_type") == "Customer":
            doctype_name = "Sales Invoice"
            conditions += "and customer =  '{}' ".format(
                filters.get("party_type"), party
            )
            payment_conditions += "and party_type = '{}'  and party =  '{}' ".format(
                filters.get("party_type"), party
            )

        elif filters.get("party_type") == "Supplier":
            doctype_name = "Purchase Invoice"
            conditions += " and supplier =  '{}' ".format(
                filters.get("party_type"), party
            )
            payment_conditions += "and party_type = '{}'  and party =  '{}' ".format(
                filters.get("party_type"), party
            )
            # payment_doctype = "Purchase Invoice"

    for mon in month:
        sales = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(grand_total) as sales
            FROM
                `tab{}`
            WHERE
                docstatus = 1 and is_return=0
                and monthname(posting_date)='{}'
                and YEAR(posting_date)='{}'
                {}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                doctype_name, mon, filters.get("to_date").split("-")[0], conditions
            ),
            as_dict=1,
        )
        if sales:
            chart["data"]["labels"].append(sales[0]["month"])
            chart["data"]["datasets"][0]["values"].append(sales[0]["sales"])
        else:
            chart["data"]["labels"].append(mon)
            chart["data"]["datasets"][0]["values"].append(0)

        sales_return = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(grand_total) as sales_return
            FROM
                `tab{}`
            WHERE
                docstatus = 1 and is_return=1
                and monthname(posting_date)='{}'
                and YEAR(posting_date)='{}'
                {}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                doctype_name, mon, filters.get("to_date").split("-")[0], conditions
            ),
            as_dict=1,
        )
        if sales_return:
            chart["data"]["datasets"][1]["values"].append(sales[0].get("sales_return"))
        else:
            chart["data"]["datasets"][1]["values"].append(0)

        payment = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(paid_amount) as payment
            FROM
                `tabPayment Entry`
            WHERE
                docstatus = 1
                and monthname(posting_date)='{}'
                and YEAR(posting_date)='{}'
                {}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                mon,
                filters.get("to_date").split("-")[0],
                payment_conditions,
            ),
            as_dict=1,
        )
        if payment:
            chart["data"]["datasets"][2]["values"].append(payment[0]["payment"])
        else:
            chart["data"]["datasets"][2]["values"].append(0)
    return chart


# # this below function is no longer in use because its job is replaced inside the above functions

# def get_ageing(filters):
#     sales_conditions = ""
#     doctype_name = "GL Entry"

#     ageing_data = {}

#     # if filters.get("to_date"):
#     #   sales_conditions += " and posting_date <=  '{}' ".format(filters.get("to_date"))

#     if filters.get("party_type") and filters.get("party"):
#         filters.party = frappe.parse_json(filters.get("party"))
#         party = str(filters.party[0])

#         if filters.get("party_type") == "Customer":
#             # doctype_name = "GL Entry"
#             sales_conditions += "and party =  '{}' ".format(party)
#             # sales_conditions += " and is_pos=0 and  outstanding_amount != 0 "

#         elif filters.get("party_type") == "Supplier":
#             # doctype_name = "GL Entry"
#             sales_conditions += "and party =  '{}' ".format(party)
#             # sales_conditions += " and  outstanding_amount != 0 "

#     update_age_30 = 0
#     update_age_60 = 0
#     update_age_90 = 0
#     update_age_120 = 0
#     update_age_above = 0

#     summary_filters = {
#             "company" : filters.get("company"),
#             "report_date" : filters.get("to_date"),
#             "ageing_based_on" : "Posting Date",
#             "range1" : 30,
#             "range2" : 60,
#             "range3" : 90,
#             "range4" : 120,
#             "customer" : filters.get("party"),
#     }

#     summary_data = get_summary(summary_filters)
#     frappe.msgprint(str(summary_data))
#     frappe.msgprint(str(summary_data[1][0]))
#     frappe.msgprint(str(summary_data[0][1]))
#     if summary_data:
#         summary_data = summary_data[1][0]
#         update_age_30 = summary_data.get("range1") or 0
#         update_age_60 = summary_data.get("range2") or 0
#         update_age_90 = summary_data.get("range3") or 0
#         update_age_120 = summary_data.get("range4") or 0
#         update_age_above = summary_data.get("range5") or 0

#     # ageing = frappe.db.sql(
#     #     """ select posting_date, (sum(debit_in_account_currency) - sum(credit_in_account_currency)) as outstanding from
#     #     `tabGL Entry` where company=%(company)s and docstatus=1 {}
#     #     group by posting_date order by posting_date""".format(get_conditions(filters)), filters, as_dict=1, debug=True)

#     # from datetime import datetime

#     # if ageing:
#     #     d_to_date = datetime.strptime(str(today()), "%Y-%m-%d")
#     #     if d_to_date:
#     #         for d in ageing:
#     #             posting_date = str(d.get("posting_date"))
#     #             d_from_date = datetime.strptime(posting_date, "%Y-%m-%d")
#     #             if d_from_date:
#     #                 difference_days = d_to_date - d_from_date
#     #                 if difference_days.days <= 30:
#     #                     update_age_30 += d.outstanding
#     #                 if difference_days.days >= 31 and difference_days.days <= 60:
#     #                     update_age_60 += d.outstanding
#     #                 if difference_days.days >= 61 and difference_days.days <= 90:
#     #                     update_age_90 += d.outstanding
#     #                 if difference_days.days >= 91 and difference_days.days <= 120:
#     #                     update_age_120 += d.outstanding
#     #                 if difference_days.days >= 121:
#     #                     update_age_above += d.outstanding

#     ageing_data = {
#         "30": update_age_30,
#         "60": update_age_60,
#         "90": update_age_90,
#         "120": update_age_120,
#         "above": update_age_above,
#     }
#     return ageing_data


@frappe.whitelist()
def get_summary(filters):
    from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
        execute,
    )

    return execute(filters)
