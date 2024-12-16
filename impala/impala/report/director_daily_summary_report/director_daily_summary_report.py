# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt
import frappe
import frappe.utils

# from impala.impala.report.customer_wise_sales_collections_and_outstanding.customer_wise_sales_collections_and_outstanding import (
#     execute as customer_wise_sales_collections_and_outstanding_execute,
# )
from impala.impala.report.division_wise_sales_and_collections.division_wise_sales_and_collections import (
    execute as division_wise_sales_and_collections_execute,
)

from impala.impala.report.sales_by_item_group.sales_by_item_group import (
    execute as sales_by_item_group_execute,
)

from impala.impala.report.production_operation_wise_summary.production_operation_wise_summary import (
    execute as production_operation_wise_summary_execute,
)
from impala.impala.report.daily_collection_report.daily_collection_report import (
    execute as daily_collection_report_execute,
)


def execute(filters=None):
    columns = get_columns()
    data = []

    # data2 = set_up_new_report(
    #     filters,
    #     columns,
    #     customer_wise_sales_collections_and_outstanding_execute,
    #     "<b>Customer Wise Sales Collections and Outstanding</b>",
    # )
    # data.extend(data2)

    data3 = set_up_new_report(
        filters,
        columns,
        division_wise_sales_and_collections_execute,
        "<b>Division Wise Sales and Collections</b>",
        format_currency=True,
    )
    data.extend(data3)

    data4 = set_up_new_report(
        filters,
        columns,
        sales_by_item_group_execute,
        "<b>Sales by Item Group</b>",
        format_currency=True,
    )
    data.extend(data4)

    data5 = set_up_new_report(
        filters,
        columns,
        production_operation_wise_summary_execute,
        "<b>Production Operation Wise Summary</b>",
        format_currency=False,
    )
    data.extend(data5)

    data6 = set_up_new_report(
        filters,
        columns,
        daily_collection_report_execute,
        "<b>POS Daily Collection Report</b>",
        format_currency=True,
    )
    data.extend(data6)
    # frappe.log_error(data)
    return columns, data


def get_columns():
    cols = []
    for i in range(8):
        cols.append(
            {
                "fieldname": f"abc{i}",
                "label": "",
                "fieldtype": "Data",
                "width": 200,
            }
        )
    return cols


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}


def Sh00_dict(d, keys, format_currency):
    if format_currency:
        return {
            x: '<span style="float:right;">Sh 0.00</span>' for x in d if x not in keys
        }
    else:
        return {x: '<span style="float:right;">0.0</span>' for x in d if x not in keys}


def set_up_new_report(filters, columns, exe_funct, report_name, format_currency=False):
    data = []
    data.append({"abc0": report_name})
    new_cols = []
    columns2, data2 = exe_funct(filters)
    new_data = []
    new_cols_row = {}
    # new_cols_row[0] = f"<b>Columns Names</b>"
    for col in range(len(columns2)):
        new_cols_row[
            "abc" + str(col)
        ] = f"""<b>{str(columns2[col].get("label")).title()}</b>"""
        columns2[col]["fieldname"] = f"abc{col}"
    data.append(new_cols_row)

    for dat in data2:
        col_count = 0
        reo = {}
        for key, val in dat.items():
            if isinstance(val, int) or isinstance(val, float):
                if format_currency:
                    reo[
                        "abc" + str(col_count)
                    ] = f"""<span style="float:right;">{frappe.utils.fmt_money(
                        val,
                        currency="KES",
                        precision=2,
                    )}</span>"""
                else:
                    reo[
                        "abc" + str(col_count)
                    ] = f"""<span style="float:right;">{val}</span>"""
            else:
                reo["abc" + str(col_count)] = val
            col_count += 1
        wk = without_keys(reo, {"abc0"})
        Sh00 = Sh00_dict(reo, {"abc0"}, format_currency)
        if wk != Sh00:
            new_data.append(reo)
    data.extend(new_data)
    data.append({})
    return data
