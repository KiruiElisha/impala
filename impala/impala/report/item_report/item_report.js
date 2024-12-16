// Copyright (c) 2023, Impala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Report"] = {
	"filters": [
    {
			"fieldname": 'show_image',
			"label": __('Check to show Image'),
			"fieldtype": 'Check'
		},
  {
      fieldname: "item_name",
      label: ("Item Name"),
      fieldtype: "Link",
      options: "Item",
      width: 100,
      reqd: 0,
    },
    {
      fieldname: "item_group",
      label: ("Item Group"),
      fieldtype: "Link",
      options: "Item Group",
      width: 100,
      reqd: 0,
    },
    {
      fieldname: "brand",
      label: ("Brand"),
      fieldtype: "Link",
      options: "Brand",
      width: 100,
      reqd: 0,
    },
    {
			"fieldname": 'disabled',
			"label": __('Check to show Disabled Item'),
			"fieldtype": 'Check'
		},
	]
};
