# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from frappe.utils import cstr, getdate


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    whvat_conditions = get_conditions_whvat(filters)
    data = []

    divisions = frappe.db.get_list(
        "Cost Center", filters={"company": filters.get("company")}, pluck="name"
    )

    total_sales = {}
    for d in divisions:
        total_sales[frappe.db.escape(d)] = 0.0

    total_out_tax = {}
    for d in divisions:
        total_out_tax[frappe.db.escape(d)] = 0.0

    total_purchases = {}
    for d in divisions:
        total_purchases[frappe.db.escape(d)] = 0.0

    total_in_tax = {}
    for d in divisions:
        total_in_tax[frappe.db.escape(d)] = 0.0

    # gen_sales = frappe.db.sql("""select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount
    # 	 	from `tabSales Invoice` s
    # 		inner join `tabSales Invoice Item` i on s.name = i.parent
    # 		inner join `tabCustomer` c on s.customer = c.name
    # 		where s.docstatus=1 and i.total_tax_percentage= '16%' {} group by s.cost_center order by 1""".format(conditions), as_dict=1)

    """ Qadeer Rizvi changed this query as General Rated sales was not matching with Break Down Summary Report  on Oct 14, 2023"""

    # registered_sales = frappe.db.sql(
    #     """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
	#  	from `tabSales Invoice` s 
	# 	inner join `tabSales Invoice Item` i on s.name = i.parent
	# 	inner join `tabCustomer` c on s.customer = c.name and c.unregistered=0
	# 	where s.docstatus=1 and i.item_tax_template NOT IN ('Zero Rated - IG', 'Zero Rated - IAL','Exempt - IG','Exempt - IAL') {} group by s.cost_center order by 1""".format(
    #         conditions
    #     ),
    #     as_dict=1,
    # )


    registered_sales = frappe.db.sql(
        """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
        from `tabSales Invoice` s 
        inner join `tabSales Invoice Item` i on s.name = i.parent
        inner join `tabCustomer` c on s.customer = c.name
        where s.docstatus=1 and c.unregistered=0 and i.total_tax_percentage='16' {} group by s.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
    )

    """ Qadeer Rizvi changed this query as General Rated sales was not matching with Break Down Summary Report  on Oct 14, 2023"""
    
    # unregistered_sales = frappe.db.sql(
    #     """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
	#  	from `tabSales Invoice` s 
	# 	inner join `tabSales Invoice Item` i on s.name = i.parent
	# 	inner join `tabCustomer` c on s.customer = c.name and c.unregistered=1
	# 	where s.docstatus=1 and i.item_tax_template NOT IN ('Zero Rated - IG', 'Zero Rated - IAL','Exempt - IG','Exempt - IAL') {} group by s.cost_center order by 1""".format(
    #         conditions
    #     ),
    #     as_dict=1,
    # )


    unregistered_sales = frappe.db.sql(
        """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
        from `tabSales Invoice` s 
        inner join `tabSales Invoice Item` i on s.name = i.parent
        inner join `tabCustomer` c on s.customer = c.name
        where s.docstatus=1 and c.unregistered=1 and i.total_tax_percentage='16' {} group by s.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
    )

    exports_sales = frappe.db.sql(
        """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
		 	from `tabSales Invoice` s 
			inner join `tabSales Invoice Item` i on s.name = i.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and c.unregistered=0 and i.item_tax_template IN ('Zero Rated - IG', 'Zero Rated - IAL' ) {} group by s.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
    )

    exempt_sales = frappe.db.sql(
        """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
		 	from `tabSales Invoice` s 
			inner join `tabSales Invoice Item` i on s.name = i.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and c.unregistered=0 and i.item_tax_template IN ('Exempt - IG','Exempt - IAL') {} group by s.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
    )

    gen_purchases = frappe.db.sql(
        """select s.cost_center as division, SUM(i.base_net_amount) as base_net_amount 
		 	from `tabPurchase Invoice` s 
			inner join `tabPurchase Invoice Item` i on s.name = i.parent
			inner join `tabSupplier` c on s.supplier = c.name
			where s.docstatus=1 and c.local_and_international='Local' and c.unregistered=0 and c.import=0 and i.total_tax_percentage= '16%' {} group by i.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
        debug=True,
    )

    import_purchases = frappe.db.sql(
        """select s.cost_center as division, SUM(s.taxes_and_charges_added) as base_net_amount
		 	from `tabPurchase Invoice` s 
			inner join `tabSupplier` c on s.supplier = c.name
			where s.docstatus=1 and c.unregistered=0 and c.import=1 {} group by s.cost_center order by 1""".format(
            conditions
        ),
        as_dict=1,
    )

    whvat_records = frappe.db.sql(
        """select c.cost_center as division, SUM(c.debit) as base_net_amount
            from `tabJournal Entry` s
            inner join `tabJournal Entry Account` c on s.name=c.parent and c.parenttype="Journal Entry"
            where s.docstatus=1 and s.is_opening="No" and c.account_type = "Tax" and c.account="1500-03 - VAT Withholding - IG" {} group by c.cost_center order by 1""".format(
            whvat_conditions
        ),
        as_dict=1,
        debug=1,
    )

    # import_purchases = frappe.db.sql("""select s.cost_center as division, s.bill_no as supp_inv, s.bill_date as supp_inv_date, s.shipment_no as shipment_no, c.local_and_international as local_and_international, c.tax_id as pin_no, s.supplier as supplier, s.posting_date as posting_date, s.name as name,
    # 		s.description as description, s.return_against return_against, s.is_return as is_return, (select posting_date from `tabPurchase Invoice` where name=s.return_against) as cnote_date,
    # 		s.taxes_and_charges_added as base_net_amount
    # 	 	from `tabPurchase Invoice` s
    # 		inner join `tabPurchase Invoice Item` i on s.name = i.parent
    # 		inner join `tabSupplier` c on s.supplier = c.name
    # 		where s.docstatus=1 and c.unregistered=0 and c.import=1 {} group by s.cost_center order by s.posting_date DESC""".format(conditions), as_dict=1)

    #  whvat_records = frappe.db.sql(
    #      """select i.cost_center as division, SUM(s.withholding_amount) as base_net_amount
    # 	from `tabWithholding Records` s
    # inner join `tabSales Invoice` i on s.sales_invoice = i.name
    # inner join `tabCustomer` c on s.customer = c.name
    # where  1=1 and s.posted='Yes' {} group by i.cost_center order by 1""".format(
    #          whvat_conditions
    #      ),
    #      as_dict=1,
    #  )

    row1 = {}
    row1["details"] = "<h5>OUTPUT</h5>"
    data.append(row1)

    totals2 = 0.0
    row2 = {}
    row2["details"] = "Registered Sales"
    for d in registered_sales:
        row2[frappe.db.escape(d.division)] = d.get("base_net_amount")
        totals2 += d.get("base_net_amount")
        total_sales[frappe.db.escape(d.division)] += d.get("base_net_amount")
        total_out_tax[frappe.db.escape(d.division)] += (
            16 * d.get("base_net_amount")
        ) / 100
    row2["totals"] = totals2
    data.append(row2)

    totals2ur = 0.0
    rowur2 = {}
    rowur2["details"] = "Unregistered Sales"
    for d in unregistered_sales:
        rowur2[frappe.db.escape(d.division)] = d.get("base_net_amount")
        totals2ur += d.get("base_net_amount")
        total_sales[frappe.db.escape(d.division)] += d.get("base_net_amount")
        total_out_tax[frappe.db.escape(d.division)] += (
            16 * d.get("base_net_amount")
        ) / 100
    rowur2["totals"] = totals2ur
    data.append(rowur2)

    totals3 = 0.0
    row3 = {}
    row3["details"] = "EXPORT"
    for d in exports_sales:
        row3[frappe.db.escape(d.division)] = d.get("base_net_amount")
        totals3 += d.get("base_net_amount")
        total_sales[frappe.db.escape(d.division)] += d.get("base_net_amount")
    row3["totals"] = totals3
    data.append(row3)

    totals4 = 0.0
    row4 = {}
    row4["details"] = "Exemption availed"
    for d in exempt_sales:
        row4[frappe.db.escape(d.division)] = d.get("base_net_amount")
        totals4 += d.get("base_net_amount")
    row4["totals"] = totals4
    data.append(row4)

    totals5 = 0.0
    row5 = {}
    row5["details"] = "<h5>Total sales</h5>"
    for d in divisions:
        row5[frappe.db.escape(d)] = total_sales[frappe.db.escape(d)]
        totals5 += total_sales[frappe.db.escape(d)]
    row5["totals"] = totals5
    data.append(row5)

    totals6 = 0.0
    row6 = {}
    row6["details"] = "<h5>Output Tax 16%</h5>"
    for d in divisions:
        row6[frappe.db.escape(d)] = total_out_tax[frappe.db.escape(d)]
        totals6 += total_out_tax[frappe.db.escape(d)]
    row6["totals"] = totals6
    data.append(row6)

    row7 = {}
    data.append(row7)

    row8 = {}
    row8["details"] = "<h5>INPUT</h5>"
    data.append(row8)

    totals9 = 0.0
    row9 = {}
    row9["details"] = "GenRatePurchase @ 16%"
    for d in gen_purchases:
        row9[frappe.db.escape(d.division)] = d.get("base_net_amount")
        totals9 += d.get("base_net_amount")
        if d.division:
            total_purchases[frappe.db.escape(d.division)] += d.get("base_net_amount")
            total_in_tax[frappe.db.escape(d.division)] += (
                16 * d.get("base_net_amount")
            ) / 100
    row9["totals"] = totals9
    data.append(row9)

    totals10 = 0.0
    row10 = {}
    row10["details"] = "Imports"

    for d in import_purchases:
        # if d.is_return == 1:
        # 	row10[frappe.db.escape(d.division)] = -abs(d.get("base_net_amount"))
        # else:
        to_show = d.get("base_net_amount") / 0.16
        row10[frappe.db.escape(d.division)] = (d.get("base_net_amount") / 0.16) or 0
        totals10 += row10[frappe.db.escape(d.division)]
        if d.division:
            total_purchases[frappe.db.escape(d.division)] += row10[
                frappe.db.escape(d.division)
            ]
            total_in_tax[frappe.db.escape(d.division)] += (16 * to_show) / 100
    row10["totals"] = totals10
    data.append(row10)

    totals11 = 0.0
    row11 = {}
    row11["details"] = "<h5>Total Purchases</h5>"
    for d in divisions:
        totals11 += total_purchases[frappe.db.escape(d)]
        row11[frappe.db.escape(d)] = total_purchases[frappe.db.escape(d)]
    row11["totals"] = totals11
    data.append(row11)

    totals12 = 0.0
    row12 = {}
    row12["details"] = "<h5>Input Tax at 16%</h5>"
    for d in divisions:
        totals12 += total_in_tax[frappe.db.escape(d)]
        row12[frappe.db.escape(d)] = total_in_tax[frappe.db.escape(d)]
    row12["totals"] = totals12
    data.append(row12)

    row13 = {}
    data.append(row13)
    row14 = {}
    data.append(row14)

    totals15 = 0.0
    row15 = {}
    row15["details"] = "Output - input"
    for d in divisions:
        row15[frappe.db.escape(d)] = (
            total_out_tax[frappe.db.escape(d)] - total_in_tax[frappe.db.escape(d)]
        )
        totals15 += row15[frappe.db.escape(d)]
    row15["totals"] = totals15
    data.append(row15)

    totals16 = 0.0
    row16 = {}
    row16["details"] = "<h6>less: WHVAT</h6>"
    for d in whvat_records:
        row16[frappe.db.escape(d.division)] = d.get("base_net_amount") or 0.0
        totals16 += d.get("base_net_amount")
    row16["totals"] = totals16
    data.append(row16)

    row17 = {}
    data.append(row17)

    totals18 = 0.0
    row18 = {}
    row18["details"] = "PAYABLE/(REFUND)"
    for d in divisions:
        try:
            c15 = row15[frappe.db.escape(d)]
        except KeyError:
            c15 = 0.0

        try:
            c16 = row16[frappe.db.escape(d)]
        except KeyError:
            c16 = 0.0

        row18[frappe.db.escape(d)] = c15 - c16
        totals18 += row18[frappe.db.escape(d)]
    row18["totals"] = totals18
    data.append(row18)

    row19 = {}
    row19["details"] = "PAYABLE/(REFUND) B/F"
    # for d in exempt_sales:
    # 	row5[frappe.db.escape(d.division)] = d.get("base_net_amount")
    data.append(row19)

    return columns, data


def get_columns(filters):

    columns = []

    columns.append(
        {
            "fieldname": "details",
            "label": _("Description"),
            "fieldtype": "Data",
            # "options": "Purchase Invoice",
            "width": 200,
        }
    )

    if filters.get("company"):
        divisions = frappe.db.get_list(
            "Cost Center",
            filters={"company": filters.get("company"), "is_group": 0},
            pluck="name",
        )
    else:
        divisions = frappe.db.get_list("Cost Center", pluck="name")

    for dv in divisions:
        columns.append(
            {
                "fieldname": frappe.db.escape(dv),
                "label": _(dv),
                "fieldtype": "Float",
                # "options": "Purchase Invoice",
                "width": 150,
            }
        )

    columns.append(
        {"fieldname": "totals", "label": _("TOTAL"), "fieldtype": "Float", "width": 150}
    )

    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " and s.company =  '{}' ".format(filters.get("company"))
    if filters.get("cost_center"):
        conditions += " and s.cost_center =  '{}' ".format(filters.get("cost_center"))
    if filters.get("month"):
        conditions += " and MONTHNAME(s.posting_date) = '{}' ".format(
            filters.get("month")
        )
    if filters.get("fiscal_year"):
        fyr_start_date = frappe.db.get_value(
            "Fiscal Year", filters.get("fiscal_year"), "year_start_date"
        )
        fiscal_year = getdate(fyr_start_date).year
        conditions += " and YEAR(s.posting_date) =  '{}' ".format(fiscal_year)

    return conditions


def get_conditions_whvat(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " and s.company =  '{}' ".format(filters.get("company"))
    if filters.get("cost_center"):
        conditions += " and c.cost_center =  '{}' ".format(filters.get("cost_center"))
    if filters.get("month"):
        conditions += " and MONTHNAME(s.posting_date) = '{}' ".format(
            filters.get("month")
        )
    if filters.get("fiscal_year"):
        fyr_start_date = frappe.db.get_value(
            "Fiscal Year", filters.get("fiscal_year"), "year_start_date"
        )
        fiscal_year = getdate(fyr_start_date).year
        conditions += " and YEAR(s.posting_date) =  '{}' ".format(fiscal_year)

    return conditions
