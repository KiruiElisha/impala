# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 300},
        {"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "width": 300},
        {"fieldname": "total_invoice_amount", "label": "Total Invoice Amount", "fieldtype": "Currency", "width": 200},        
    ]

    data = []

    # Define additional filters based on user input
    additional_filters = {}
    
    if filters.get("company"):
        additional_filters["company"] = filters.get("company")
    
    if filters.get("cost_center"):
        additional_filters["cost_center"] = filters.get("cost_center")

    limit = filters.get("limit", 20)

    # Fetch the top 20 customers based on total invoice amounts within the selected date range and additional filters
    sql_query = """
        SELECT customer, customer_name, SUM(base_grand_total) AS total_invoice_amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
            {company_condition}
            {cost_center_condition}
            {date_condition}
        GROUP BY customer
        ORDER BY total_invoice_amount DESC
        LIMIT {limit}
    """.format(
        company_condition="AND company = %(company)s" if filters.get("company") else "",
        cost_center_condition="AND cost_center = %(cost_center)s" if filters.get("cost_center") else "",
        date_condition="AND (posting_date BETWEEN %(from_date)s AND %(to_date)s)" if filters.get("from_date") and filters.get("to_date") else "",
        limit=limit
    )

    result = frappe.db.sql(sql_query, {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "company": filters.get("company"),
        "cost_center": filters.get("cost_center")
    }, as_dict=True)

    for row in result:
        data.append({
            "customer": row.customer,
            "customer_name": row.customer_name,
            "total_invoice_amount": row.total_invoice_amount,            
        })

    return columns, data
