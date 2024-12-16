frappe.query_reports["Sales Analysis Multi Level"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			"default" : frappe.datetime.month_start(),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			"default" : frappe.datetime.month_end(),
			reqd: 1
		},


		{
			fieldname: "level_1",
			label: __("Level 1"),
			fieldtype: "Select",
			options: ["" , "Customer", "Item Group" , "Item", "Division", "Department", "Territory", "Local/Export"],
		},


		{
			fieldname: "level_2",
			label: __("Level 2"),
			fieldtype: "Select",
			options: ["","Customer", "Item Group" , "Item" , "Division","Department", "Territory", "Local/Export"],
		},


		{
			fieldname: "level_3",
			label: __("Level 3"),
			fieldtype: "Select",
			options: ["","Customer", "Item Group" , "Item" , "Division","Department", "Territory", "Local/Export"],
		},


		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: ["","Week","Month","Quarter","Year","Day"]
			// default : "Week"
			
			// on_change: function() {
			// 	if (filters.range !=""){

			// 		frappe.query_report.set_filter_value('value', "qty");
			// 	}
			// } ,


		} ,



		{
			fieldname: "value",
			label: __("Value"),
			fieldtype: "Select",
			options: ["","Qty","Amount Exclusive",  "Amount Inclusive"]
			// default : "qty"
		},


		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["","Draft","On Hold",   "To Deliver and Bill" , "To Bill" , "To Deliver", "Completed" , "Cancelled" , "Closed" ]
			// default : "qty"
		},





		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},

		{
			fieldname: "local_and_international",
			label: __("Local/International"),
			fieldtype: "Select",
			options: ["", "Local", "Export"],
			default: "",
		},
		{
			fieldname: "only_summary",
			label: __("Summary"),
			fieldtype: "Check",
			default: 0,
		}	
	],

	"formatter": function(value, row, column, data, default_formatter) {
		// body...
		value = default_formatter(value, row, column, data);

		if (column.fieldname=='rate' && data.rate==null){
			value = ""
		}
		if (column.fieldname=='qty' && data.qty==null){
			value = ""
		}
		if (column.fieldname=='amount' && data.amount==null){
			value = ""
		}

		if (column.fieldname=='item_cost' && data.item_cost==null){
			value = ""
		}

		if (column.fieldname=='amount_inclusive' && data.amount_inclusive==null){
			value = ""
		}
		
		if (column.fieldname=='amount_exclusive' && data.amount_exclusive==null){
			value = ""
		}

		if (column.fieldname=='gross_profit' && data.gross_profit==null){
			value = ""
		}

		if (column.fieldname=='sales_person_contrib' && data.sales_person_contrib==null){
			value = ""
		}

		return value

		
		
	}
}