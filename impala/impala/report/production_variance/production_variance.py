import frappe
import datetime

def fetch_work_orders(filters):
    # Filter work orders by status, if provided
    work_order_filters = {"qty": (">", 0)}
    
    if filters.get("work_order"):
        work_order_filters["name"] = filters.get("work_order")
    
    if filters.get("status"):
        work_order_filters["status"] = filters.get("status")
    
    return frappe.get_all("Work Order", fields=["name", "production_item", "qty", "planned_start_date", "status"], filters=work_order_filters)

def fetch_required_materials(work_order):
    return frappe.get_all("Work Order Item", filters={"parent": work_order.name}, fields=["item_code", "item_name", "required_qty"])

def fetch_stock_entries(filters):
    stock_entry_filters = {"work_order": filters.get("work_order"), "stock_entry_type": "Manufacture"}
    stock_entry_name = filters.get("stock_entry")
    if stock_entry_name:
        stock_entry_filters["name"] = stock_entry_name
    return frappe.get_all("Stock Entry", filters=stock_entry_filters, fields=["name", "fg_completed_qty"])

def calculate_percentage(produced_qty, required_qty):    
    result = (produced_qty / required_qty) * 100 if required_qty > 0 else 0
    return round(result, 2)

def execute(filters=None):
    columns = [
        {"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": "Item to Manufacture", "fieldname": "production_item", "fieldtype": "Data", "width": 150},
        {"label": "WO Qty", "fieldname": "work_order_qty", "fieldtype": "Data", "width": 100},
        {"label": "Produced Qty", "fieldname": "fg_completed_qty", "fieldtype": "Data", "width": 150},        
        {"label": "Required Items", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Required Qty", "fieldname": "required_qty", "fieldtype": "Data", "width": 100},
        {"label": "Material Used", "fieldname": "produced_qty", "fieldtype": "Data", "width": 150},
        {"label": "Material Required", "fieldname": "material_required", "fieldtype": "Data", "width": 150},               
        {"label": "Consumption(%)", "fieldname": "percentage", "fieldtype": "Data", "width": 150},
        {"label": "Work Order Status", "fieldname": "status", "fieldtype": "Data", "width": 100},  # Added status column
    ]
    
    report_data = []

    # Fetch work orders with the status filter
    work_orders = fetch_work_orders(filters)
    for work_order in work_orders:
        planned_start_date = work_order.get("planned_start_date")
        planned_start_date_str = planned_start_date.strftime("%Y-%m-%d") if planned_start_date else None
        
        # Apply date range filtering if provided
        if filters.get("from_date") and filters.get("to_date") and planned_start_date:
            if filters.get("from_date") <= planned_start_date_str <= filters.get("to_date"):
                stock_entries = fetch_stock_entries({"work_order": work_order.name})
                total_fg_completed_qty = sum(entry.get('fg_completed_qty', 0) for entry in stock_entries)
                qty = work_order.get("qty")
                pivot = total_fg_completed_qty / float(qty) if float(qty) > 0 else 0      

                if work_order.get("production_item"):
                    required_materials = fetch_required_materials(work_order)
                    
                    report_data.append({     
                        "work_order": work_order.get('name'),                            
                        "fg_completed_qty": total_fg_completed_qty,
                        "production_item": "<b>" + str(work_order.production_item) + "</b>",
                        "work_order_qty": "<b>" + str(qty) + "</b>",
                        "status": work_order.get("status")  # Include work order status in the report                   
                    })
                    
                    stock_entry_items_qty = {}
                    
                    # Collect quantities from stock entries
                    for stock_entry in stock_entries:
                        stock_entry_items = frappe.get_all("Stock Entry Detail", filters={"parent": stock_entry.name}, fields=["item_code", "item_name", "qty"])
        
                        for item in stock_entry_items:
                            item_code = item.item_code
                            transfer_qty = item.qty
                            
                            stock_entry_items_qty[item_code] = stock_entry_items_qty.get(item_code, 0) + transfer_qty
                
                    # Calculate material usage and consumption for required materials
                    for material in required_materials:
                        item_code = material.item_code
                        required_qty = material.required_qty
                        produced_qty = stock_entry_items_qty.get(item_code, 0)
                        material_required = required_qty * pivot
                        
                        # If the item is not part of the WO items, indicate it with a custom message
                        percentage = calculate_percentage(produced_qty, material_required)
                        percentage_consumption = str(percentage) + "%" if produced_qty > 0 else "Not part of WO items"
                        
                        report_data.append({                    
                            "item_code": material.item_code,                    
                            "work_order_qty": " ",
                            "required_qty": round(required_qty, 3),
                            "stock_entry": "",
                            "fg_completed_qty": " ",
                            "produced_qty": round(produced_qty, 3),
                            "material_required": round(material_required, 3),
                            "percentage": percentage_consumption
                        })

    return columns, report_data
