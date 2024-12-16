// Copyright (c) 2023, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["User Roles Report"] = {
	"filters": [
		{
			"fieldname" : "user",
			"fieldtype": "MultiSelectList",
			"label": "User",
			"options": "User",
			get_data: function (txt) {
				return frappe.db.get_link_options("User", txt, {
					'enabled' : 1

				})
			}
		}
	]
};
