// Copyright (c) 2024, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Price Report"] = {
	"filters": [
		        {
            "fieldname": "item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        },
        {
            "fieldname": "price_list",
            "label": __("Price List"),
            "fieldtype": "Link",
            "options": "Price List"
        },
        {
            "fieldname": "item_category",
            "label": __("Item Category"),
            "fieldtype": "Link",
            "options": "Item Category"
        },
       {
            "fieldname": "show_all_prices",
            "label": __("Show All Prices"),
            "fieldtype": "Check",
            "default": 0 // 0 for unchecked (latest prices only), 1 for checked (all prices)
        }
	]
};
