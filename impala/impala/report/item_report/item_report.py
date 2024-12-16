import frappe

def execute(filters=None):
    columns = [
        {
            "label": "Image",
            "fieldname": "image",
            "fieldtype": "Data"
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Data"
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data"
        },
        {
            "label": "UOM",
            "fieldname": "uom",
            "fieldtype": "Data"
        },
        {
            "label": "Price Excl",
            "fieldname": "price_excl",
            "fieldtype": "Currency"
        },
        {
            "label": "Price Incl",
            "fieldname": "price_incl",
            "fieldtype": "Currency"
        }
    ]

    if not filters or not filters.get("show_image"):
        columns = [col for col in columns if col['fieldname'] != 'image']
        data = fetch_data(filters)
        repeated_data = repeat_items(data)
        return columns, repeated_data

    else:
        data = fetch_data(filters)
        repeated_data = repeat_items(data)
        return columns, repeated_data

def fetch_data(filters):
    conditions = []
    item_name = filters.get("item_name")
    brand = filters.get("brand")
    item_group = filters.get("item_group")
    disabled = filters.get("disabled")

    if filters.get("item_name"):
        conditions.append(f"i.item_name LIKE '%%{item_name}%%'")
    if filters.get("brand"):
        conditions.append(f"i.brand LIKE '%%{brand}%%'")
    if filters.get("item_group"):
        conditions.append(f"i.item_group LIKE '%%{item_group}%%'")
    if filters.get("disabled"):
        conditions.append(f"i.disabled LIKE '%%{disabled}%%'")
    else:
        conditions.append(f"i.disabled = 0 OR i.disabled IS NULL")

    conditions_str = " AND ".join(conditions) if conditions else "1=1"
    if not filters.get("show_image"):
        sql_query = frappe.db.sql(f"""
            SELECT
                i.`name`,
                i.`item_code`,
                i.`brand`,
                i.`item_name`,
                i.`disabled`,
                i.`stock_uom` AS uom,
                (CASE
                    WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NOT NULL 
                    THEN COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00)
                    ELSE COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00)
                END) AS price_excl,
                (CASE
                    WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NOT NULL 
                    THEN COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00) * 1.16
                    ELSE COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00) * 1.16
                END) AS price_incl
            FROM
                `tabItem` AS i
            WHERE
                {conditions_str}
        """, as_dict=True)
    else:
        sql_query = frappe.db.sql(f"""
            SELECT
                CONCAT('<img src="', i.`image`, '" style="max-width:100px; max-height:100px;">') AS image,
                i.`name`,
                i.`item_code`,
                i.`brand`,
                i.`item_name`,
                i.`disabled`,
                i.`stock_uom` AS uom,
                (CASE
                    WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NOT NULL 
                    THEN COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00)
                    ELSE COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00)
                END) AS price_excl,
                (CASE
                    WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NOT NULL 
                    THEN COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00) * 1.16
                    ELSE COALESCE(
                        (SELECT ip.`price_list_rate` 
                        FROM `tabItem Price` ip 
                        WHERE ip.item_code = i.`name` 
                        ORDER BY ip.valid_from DESC 
                        LIMIT 1), 0.00) * 1.16
                END) AS price_incl
            FROM
                `tabItem` AS i
            WHERE
                {conditions_str}
        """, as_dict=True)

    return sql_query

def repeat_items(data):
    repeated_data = []
    for item in data:
        repeated_data.extend([item] * data.count(item))
    return repeated_data

def process_images(repeated_data):
    # Function to process data and add image display logic
    processed_data = []
    for item in repeated_data:
        # Assuming 'image' field contains the URL or path to the image
        if item.get("image"):
            # Display the image if 'image' field exists
            item["image"] = f'<img src="{item["image"]}" style="max-width:100px; max-height:100px;">'
        else:
            # If 'image' field doesn't exist or is empty, set it to an empty string
            item["image"] = ""

        processed_data.append(item)

    return processed_data



        # {
        #     "label": "Price Excl",
        #     "fieldname": "price_excl",
        #     "fieldtype": "Currency"
        # },
        # {
        #     "label": "Price Incl",
        #     "fieldname": "price_incl",
        #     "fieldtype": "Currency"
        # },


# (CASE
#                     WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NULL 
#                     THEN COALESCE(
#                         (SELECT ip.`price_list_rate` 
#                         FROM `tabItem Price` ip 
#                         WHERE ip.item_code = i.`name` 
#                         ORDER BY ip.valid_from DESC 
#                         LIMIT 1), 0.00)
#                 END) AS price_excl,
#                 (CASE
#                     WHEN (SELECT it.`name` FROM `tabItem Tax` it WHERE i.`name` = it.`parent` LIMIT 1) IS NOT NULL 
#                     THEN COALESCE(
#                         (SELECT ip.`price_list_rate` 
#                         FROM `tabItem Price` ip 
#                         WHERE ip.item_code = i.`name` 
#                         ORDER BY ip.valid_from DESC 
#                         LIMIT 1), 0.00)
#                 END) AS price_incl,
