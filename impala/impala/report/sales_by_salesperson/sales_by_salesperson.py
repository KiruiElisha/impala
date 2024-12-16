# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "sales_person", "label": "Sales Person", "fieldtype": "Link", "options": "Sales Person", "width": 300},
        {"fieldname": "total_sales", "label": "Total Contribution", "fieldtype": "Currency", "width": 300},
    ]

    data = []

    # Define additional filters based on user input
    additional_filters = {}

    if filters.get("from_date") and filters.get("to_date"):
        additional_filters["from_date"] = filters.get("from_date")
        additional_filters["to_date"] = filters.get("to_date")

    if filters.get("company"):
        additional_filters["company"] = filters.get("company")

    # Remove the limit filter
    limit = None

    # Fetch sales by salespersons within the selected date range, company, and additional filters
    sql_query = """
        SELECT st.sales_person, SUM(si.base_net_total) AS total_sales, si.cost_center
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Team` st ON si.name = st.parent
        WHERE si.docstatus = 1
        {date_condition}
        {company_condition}
        {cost_center_condition}
        GROUP BY st.sales_person, si.cost_center
        ORDER BY total_sales DESC
        {limit_clause}
    """.format(
        date_condition="AND (posting_date >= %(from_date)s AND posting_date <= %(to_date)s)" if filters.get("from_date") and filters.get("to_date") else "",
        company_condition="AND si.company = %(company)s" if filters.get("company") else "",
        cost_center_condition="AND si.cost_center = %(cost_center)s" if filters.get("cost_center") else "",
        limit_clause=f"LIMIT {limit}" if limit is not None else ""
    )
    result = frappe.db.sql(sql_query, {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "company": filters.get("company"),
        "cost_center": filters.get("cost_center"),
    }, as_dict=True)

    for row in result:
        data.append({
            "sales_person": row.sales_person,
            "total_sales": row.total_sales,
        })

    return columns, data
