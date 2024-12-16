# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, date, timedelta
from frappe.utils import cstr

def execute(filters=None):
    
    if filters.age1 and filters.age2 and filters.age1 > filters.age2:
        frappe.throw("Age 1 should be less than Age 2")
    if filters.age2 and filters.age3 and filters.age2 > filters.age3:
        frappe.throw("Age 2 should be less than Age 3")
    if filters.age3 and filters.age4 and filters.age3 > filters.age4:
        frappe.throw("Age 3 should be less than Age 4")

    columns, data = [], []
    columns = [
        {
            "fieldname": "date",
            "fieldtype": "Date",
            "label": "Date",
            "width": 125,
        },
        {
            "fieldname": "customer",
            "fieldtype": "Link",
            "label": "Customer",
            "options": "Customer",
            "width": 125,
        },
        {
            "fieldname": "docno",
            "fieldtype": "Data",
            "label": "No",
            "width": 125,
        },
        {
            "fieldname": "doctype",
            "fieldtype": "Data",
            "label": "Description",
            "width": 125,
        },
        {
            "fieldname": "alloc",
            "fieldtype": "Data",
            "label": "Allocation",
            "width": 125,
        },
        {
            "fieldname": "debit",
            "fieldtype": "Float",
            "label": "Debit",
            "width": 125,
        },
        {
            "fieldname": "credit",
            "fieldtype": "Float",
            "label": "Credit",
            "width": 125,
        },
        {
            "fieldname": "balance",
            "fieldtype": "Float",
            "label": "Balance",
            "width": 125,
        },
    ]
    data = get_customer_data(filters)
    chart = get_chart(filters)
    summary = get_summary(filters)
    data[-1]["sales"] = summary[0]["value"]
    data[-1]["sales_return"] = summary[1]["value"]
    data[-1]["payment"] = summary[2]["value"]
    if len(data) <= 2 and (
        ("debit" not in data[0])
        or ("debit" in data[0] and data[0]["debit"] != None)
        or ("credit" not in data[0])
        or ("credit" in data[0] and data[0]["credit"] != None)
    ):
        data = []

    return (columns, data, None, chart, summary)


def get_summary(filters):
    filter = ""
    if filters.from_date:
        filter += ' and posting_date >= "' + filters.from_date + '"'
    if filters.to_date:
        filter += ' and posting_date <= "' + filters.to_date + '"'
    if filters.customer:
        filter += ' and customer = "' + filters.customer + '"'
    sales = frappe.db.sql(
        """
        SELECT
            sum(grand_total) as total_sales
        FROM
            `tabSales Invoice`
        WHERE
            docstatus = 1 and is_return=0
            {0}
            """.format(
            filter
        ),
        as_dict=1,
    )
    sales_return = frappe.db.sql(
        """
        SELECT
            sum(grand_total) as total_return
        FROM
            `tabSales Invoice`
        WHERE
            docstatus = 1 and is_return=1
            {0}
            """.format(
            filter
        ),
        as_dict=1,
    )
    pay_filter = ""
    if filters.from_date:
        pay_filter += ' and posting_date >= "' + filters.from_date + '"'
    if filters.to_date:
        pay_filter += ' and posting_date <= "' + filters.to_date + '"'
    if filters.customer:
        pay_filter += ' and party = "' + filters.customer + '"'
    payment = frappe.db.sql(
        """
        select
            sum(paid_amount) as total_payment
        from
            `tabPayment Entry`
        where
            docstatus = 1
            {0}
            """.format(
            pay_filter
        ),
        as_dict=1,
    )
    summary = []
    if sales:
        summary.append(
            {
                "label": "Sales",
                "value": frappe.utils.fmt_money(sales[0].total_sales or 0),
                "color": "#456789",
            }
        )
    if sales_return:
        summary.append(
            {
                "label": "Sales Return",
                "value": frappe.utils.fmt_money(sales_return[0].total_return or 0),
                "color": "#EE8888",
            }
        )
    if payment:
        summary.append(
            {
                "label": "Payment",
                "value": frappe.utils.fmt_money(payment[0].total_payment or 0),
                "color": "#FFBB00",
            }
        )
    return summary


def get_chart(filters):
    chart = {
        "data": {
            "labels": [],
            "datasets": [
                {"name": "Sales", "values": []},
                {"name": "Return", "values": []},
                {"name": "Payment", "values": []},
            ],
        },
        "type": "bar",
        "colors": ["#456789", "#EE8888", "#7E77BF"],
    }

    month = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    filter = ""
    if filters.from_date:
        filter += ' and posting_date >= "' + filters.from_date + '"'
    if filters.to_date:
        filter += ' and posting_date <= "' + filters.to_date + '"'
    if filters.customer:
        filter += ' and customer = "' + filters.customer + '"'
    for mon in month:
        sales = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(grand_total) as sales
            FROM
                `tabSales Invoice`
            WHERE
                docstatus = 1 and is_return=0
                and monthname(posting_date)='{1}'
                and YEAR(posting_date)='{2}'
                {0}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                filter, mon, filters.to_date.split("-")[0]
            ),
            as_dict=1,
        )
        if sales:
            chart["data"]["labels"].append(sales[0]["month"])
            chart["data"]["datasets"][0]["values"].append(sales[0]["sales"])
        else:
            chart["data"]["labels"].append(mon)
            chart["data"]["datasets"][0]["values"].append(0)

        sales_return = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(grand_total) as sales_return
            FROM
                `tabSales Invoice`
            WHERE
                docstatus = 1 and is_return=1
                and monthname(posting_date)='{1}'
                and YEAR(posting_date)='{2}'
                {0}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                filter, mon, filters.to_date.split("-")[0]
            ),
            as_dict=1,
        )
        if sales_return:
            chart["data"]["datasets"][1]["values"].append(sales[0].get("sales_return"))
        else:
            chart["data"]["datasets"][1]["values"].append(0)
        pay_filter = ""
        if filters.from_date:
            pay_filter += ' and posting_date >= "' + filters.from_date + '"'
        if filters.to_date:
            pay_filter += ' and posting_date <= "' + filters.to_date + '"'
        if filters.customer:
            pay_filter += ' and party = "' + filters.customer + '"'

        payment = frappe.db.sql(
            """
            SELECT
                monthname(posting_date) as month,
                sum(paid_amount) as payment
            FROM
                `tabPayment Entry`
            WHERE
                docstatus = 1
                and monthname(posting_date)='{1}'
                and YEAR(posting_date)='{2}'
                {0}
                group by month(posting_date)
                order by month(posting_date) asc
                """.format(
                pay_filter, mon, filters.to_date.split("-")[0]
            ),
            as_dict=1,
        )
        if payment:
            chart["data"]["datasets"][2]["values"].append(payment[0]["payment"])
        else:
            chart["data"]["datasets"][2]["values"].append(0)
    return chart


def get_customer_data(filters):
    filt = ""
    from_date = ""
    to_date = ""

    data = []

    total_amount = 0

    if filters.customer:
        filt += " and customer = '{0}'".format(filters.customer)

    if filters.from_date:
        opening = frappe.db.sql(
            """ select sum(outstanding_amount) as outstanding from `tabSales Invoice` where docstatus=1  and outstanding_amount>0 and posting_date <'{1}' and  company='{2}' {0} """.format(
                filt, filters.from_date, filters.company
            ),
            as_dict=True,
        )
        opening = opening[0].outstanding or 0 if opening and opening[0] else 0
        opening_payment = frappe.db.sql(
            """ select sum(paid_amount) as paid_amount from `tabPayment Entry` where docstatus=1 and payment_type='Receive' and paid_amount>0 and party='{0}' and posting_date<'{1}' and company='{2}' """.format(
                filters.customer, filters.from_date, filters.company
            ),
            as_dict=True,
        )
        total_paid = opening_payment[0].paid_amount or 0 if opening_payment else 0
        data.append(
            {
                "docno": "Opening",
                "debit": opening or 0,
                "credit": total_paid or 0,
                "balance": opening - total_paid,
            }
        )
        total_amount = (opening or 0) - (total_paid or 0)
        from_date = datetime.strptime(str(filters.from_date), "%Y-%m-%d").date()
        # filt += " and posting_date >= '{0}'".format(filters.from_date)
    else:
        sales = frappe.db.sql(
            """ select posting_date from `tabSales Invoice` where docstatus=1 and is_pos=0 and outstanding_amount > 0 and company='{1}' {0} order by posting_date ASC """.format(
                filt, filters.company
            )
        )
        pay = frappe.db.sql(
            """ select posting_date from `tabPayment Entry` where docstatus=1 and party='{0}' and company='{1}' order by posting_date ASC """.format(
                filters.customer, filters.company
            )
        )
        min_date = min(
            sales[0][0] if sales else datetime.now().date(),
            pay[0][0] if pay else datetime.now().date(),
        )
        if min_date:
            from_date = min_date
            # filt += " and posting_date >= '{0}'".format(filters.from_date)
        else:
            if filters.to_date:
                from_date = datetime.strptime(str(filters.to_date), "%Y-%m-%d").date()
    if filters.to_date:
        to_date = datetime.strptime(str(filters.to_date), "%Y-%m-%d").date()
        # filt += " and posting_date <= '{0}'".format(filters.to_date)

    period = to_date - from_date
    si_filt = ""
    pe_filt = ""
    if filters.customer:
        si_filt += " and customer='{0}'".format(filters.customer)
        pe_filt += " and party='{0}'".format(filters.customer)

    for i in range(period.days + 1):
        date = from_date + timedelta(days=i)
        date_filt = " and posting_date = '{0}'".format(date)
        si_data = frappe.db.sql(
            """ select posting_date, customer, name, rounded_total, grand_total from `tabSales Invoice` where docstatus=1 and is_pos=0 and posting_date='{0}' and company='{2}' {1} """.format(
                date, si_filt, filters.company
            ),
            as_dict=1,
        )
        for j in si_data:
            total_amount +=  j.grand_total
            data.append(
                {
                    "date": j.posting_date,
                    "customer": j.customer,
                    "docno": frappe.utils.get_link_to_form("Sales Invoice", j.name),
                    "doctype": "Sales Invoice",
                    "debit":  j.grand_total or 0,
                    "credit": 0,
                    "balance": total_amount or 0,
                }
            )
        pe_data = frappe.db.sql(
            """ select posting_date, party, name, paid_amount from `tabPayment Entry` where docstatus=1 and payment_type="Receive" and posting_date='{0}' and company='{2}' {1} """.format(
                date, pe_filt, filters.company
            ),
            as_dict=1,
        )
        for j in pe_data:
            total_amount -= j.paid_amount or 0
            pe = frappe.get_doc("Payment Entry", j.name)
            aloc = [
                frappe.utils.get_link_to_form(k.reference_doctype, k.reference_name)
                for k in pe.references
            ]
            aloc = ", ".join(aloc)
            data.append(
                {
                    "date": j.posting_date,
                    "customer": j.party,
                    "docno": frappe.utils.get_link_to_form("Payment Entry", j.name),
                    "doctype": "Payment Entry",
                    "alloc": aloc,
                    "credit": j.paid_amount or 0,
                    "debit": 0,
                    "balance": total_amount or 0,
                }
            )

    filtr = ""
    if filters.from_date:
        filtr += " and posting_date >= '{0}'".format(filters.from_date)
    if filters.customer:
        filtr += " and customer = '{0}'".format(filters.customer)
    ageing = frappe.db.sql(
        """ select posting_date, sum(outstanding_amount) as outstanding from `tabSales Invoice` where docstatus=1 and is_pos=0 and outstanding_amount>0 and posting_date<='{0}' and company='{2}' {1} group by posting_date""".format(
            filters.to_date, filtr, filters.company
        ),
        as_dict=1,
    )
    header = get_header(filters)
    dic = {
        filters.age1: 0,
        filters.age2: 0,
        filters.age3: 0,
        filters.age4: 0,
        "Above": 0,
        "age1": filters.age1,
        "age2": filters.age2,
        "age3": filters.age3,
        "age4": filters.age4,
        "age5": "Above",
        "bal": data[-1]["balance"] if len(data) and "balance" in data[-1] else 0,
        "header": header,
        "customer_name": frappe.db.get_value(
            "Customer", filters.customer, "customer_name"
        ),
    }
    for i in data:
        if "date" in i:
            age = get_age(i["date"], filters.to_date, filters)
            if "debit" in i:
                dic[age] += i["debit"]
            if "credit" in i:
                dic[age] -= i["credit"]

    if filters.customer:
        dic["address"] = frappe.db.get_value(
            "Customer", filters.customer, "primary_address"
        )
    data.append(dic)
    return data


def get_age(posting_date, to_date, filters):
    posting_date = datetime.strptime(str(posting_date), "%Y-%m-%d").date()
    to_date = datetime.strptime(str(to_date), "%Y-%m-%d").date()
    period = (to_date - posting_date).days + 1

    if filters.age1 and period <= filters.age1:
        return filters.age1
    elif filters.age2 and period <= filters.age2:
        return filters.age2
    elif filters.age3 and period <= filters.age3:
        return filters.age3
    elif filters.age4 and period <= filters.age4:
        return filters.age4
    else:
        return "Above"


def get_header(filters):
    header = frappe.db.get_value("Letter Head", {"is_default": 1}, "content")
    company_details = frappe.db.get_list(
        "Company",
        filters={"name": filters.company},
        fields=[
            "company_name",
            "phone_no",
            "email",
            "tax_id",
            "company_logo",
            "website",
        ],
    )
    comapny_address_line1 = ""
    comapny_city = ""
    comapny_counrty = ""
    comapny_state = ""
    phone = ""

    company_address_name = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": filters.company},
        "parent",
    )

    if company_address_name:
        address = frappe.db.get_value(
            "Address",
            company_address_name,
            [
                "address_line1",
                "address_title",
                "city",
                "country",
                "state",
                "email_id",
                "phone",
            ],
            as_dict=1,
        )

        comapny_address_line1 = address.address_line1
        comapny_city = address.city
        comapny_counrty = address.country
        comapny_state = address.state

        phone = address.phone
    header_updated = frappe.render_template(
        header,
        {
            "company": company_details[0].company_name,
            "company_address": comapny_address_line1,
            "city": comapny_city,
            "country": comapny_counrty,
            "state": comapny_state,
            "phone_no": phone,
            "email": company_details[0].email,
            "pin_no": company_details[0].tax_id,
            "company_logo": company_details[0].company_logo,
            "website": company_details[0].website,
        },
    )
    data = """<div id="header-html" class = "margin-top-15"   style = " margin-top:-20px  !important; width:92.2%; margin-left:15px !important">
    <div class = "row" style = "">

        <div class = "col-xs-10" style = "width:100%;   float:left; border:1px solid black ">

            {0}

        </div>
    </div>"""
    return data.format(header_updated)


