# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "cost_center", "label": "Division", "fieldtype": "Link", "options": "Cost Center", "width": 200},
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 200},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "qty_sold", "label": "Qty Sold", "fieldtype": "Float", "width": 200},
        {"fieldname": "uom", "label": "UOM", "fieldtype": "Link", "options": "UOM", "width": 200},
    ]

    data = []
    group_data = []
    additional_filters = {}
    if filters.get("cost_center"):
        group_data = filters.get("cost_center")
    else:
        group_data = frappe.get_all("Cost Center", pluck="name")

    if filters and filters.get("company"):
        additional_filters["company"] = filters.get("company")
    
    if filters and filters.get("item"):
        additional_filters["item_code"] = filters.get("item")

    # Define the limit filter
    limit = filters.get("limit")

    # Fetch the top N fast-moving items within additional filters
    sql_query = """
        SELECT item_code, item_name, SUM(qty) AS qty_sold, stock_uom
        FROM `tabSales Invoice Item`
        WHERE parent IN (
            SELECT name FROM `tabSales Invoice`
            WHERE docstatus = 1
            {company_condition}
            {cost_center_condition}
        )
        {item_condition}
        GROUP BY item_code, stock_uom
        ORDER BY qty_sold DESC
        LIMIT %(limit)s
    """.format(
        company_condition="AND company = %(company)s" if additional_filters.get("company") else "",
        cost_center_condition="AND cost_center = %(cost_center)s" if filters.get("cost_center") else "",
        item_condition="AND item_code = %(item_code)s" if additional_filters.get("item_code") else "",
    )

    # Define the parameter values as a dictionary
    params = {
        "company": additional_filters.get("company"),
        "cost_center": filters.get("cost_center"),
        "item_code": additional_filters.get("item_code"),
        "limit": limit
    }

    # Execute the query with parameters
    result = frappe.db.sql(sql_query, params, as_dict=True)
    for i in group_data:
        row = []
        row['cost_center'] = i        
        data.append(row)
        for row in result:           
                data.append({                    
                    "item_code": row["item_code"],
                    "item_name": row["item_name"],
                    "qty_sold": row["qty_sold"],
                    "uom": row["stock_uom"]
                })

    df = pd.DataFrame(data)

    pivot_table = pd.pivot_table(
        df,
        index="cost_center",
        columns="item_code",
        values=["qty_sold"],
        aggfunc="sum",
        fill_value=0.0,
    )

    # Reset the index if needed
    pivot_table.reset_index(inplace=True)

    # Convert the pivot table to a list of dictionaries
    pivot_data = pivot_table.to_dict(orient="records")

    # Return columns and pivot table data
    return columns, pivot_data

    return columns, data
