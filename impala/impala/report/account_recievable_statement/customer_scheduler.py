# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date, timedelta
from frappe.utils import add_days,  cstr ,  getdate, formatdate, nowdate ,  get_first_day, date_diff, add_years  , flt, cint, getdate, now

from frappe.utils.pdf import get_pdf,cleanup
from frappe.core.doctype.access_log.access_log import make_access_log
from PyPDF2 import PdfFileWriter
import pdfkit
import json

from frappe.utils.file_manager import save_file




from frappe.utils.print_format import  report_to_pdf


from impala.impala.report.account_recievable_statement.report_execute import execute

# from frappe.email.email_body.Email import Email 




# def add_pdf_attachment(self, name, html, options=None):
# self.add_attachment(name, get_pdf(html, options), "application/octet-stream")


class CustomerScheduler(Document):

	def validate(self):
		print()
		# records = customer_report()
		# frappe.msgprint(cstr(records))





















@frappe.whitelist(allow_guest  = True)
def check_scheduler_date():
	doc = frappe.get_doc("Customer Scheduler" , "Customer Scheduler")
	child = doc.scheduler_items
	if child:
		for i in child:
			if i.customer_group and i.start_date and i.end_date and i.scheduler_date:
				if getdate(i.scheduler_date) == getdate(nowdate()):
					get_data_customer_group(i.customer_group  , i.start_date  ,  i.end_date , i.scheduler_date )




def get_data_customer_group(customer_group , start_date , end_date , scheduler_date):
	customer_list = frappe.db.get_list("Customer" ,  filters = {"customer_group" : customer_group } , fields =  ["name" , "email_id"])
	if customer_list:
		for i in customer_list:
			if i.name and i.email_id:
				get_single_customer_data(i.name , start_date ,  end_date , i.email_id , scheduler_date)






def get_single_customer_data(customer , start_date , end_date , email_id , scheduler_date):
	set_filters = {
		"customer" : str(customer), 
		"from_date" : 	"01-02-2022" , 
		"scheduler_date" : 	str(scheduler_date) , 
		"to_date" : "18-05-2022" , 
		"company" : str(frappe.db.get_value("Customer" , {"name" : customer} , "company")), 
		"age1" : str(30),
		"age2" : str(60),
		"age3" : str(90),
		"age4" : str(120),
	}
	frappe.log_error(cstr(set_filters))

	if set_filters:
		data = []
		data = execute(set_filters)
		frappe.msgprint(cstr(data))


		return data

		# return_single_customer_data = customer_report(set_filters)
		# # a =   customer_report(set_filters)
		# # frappe.msgprint(cstr(a))
		# if return_single_customer_data:
		# 	send_data_by_eamil_to_customer(customer_data = return_single_customer_data , email_id = email_id , set_filters = set_filters )


def send_data_by_eamil_to_customer(customer_data , email_id  , set_filters):
	if customer_data:
		attachments = []

		header_dict =  dict(customer_data.get("header_dict"))
		frappe.log_error(cstr(customer_data))
		# frappe.log_error(customer_data.get("header_dict"))
		customer_detail = customer_data.get("customer_detail")
		customer_summary = customer_data.get("customer_summary")
		customer_aging = customer_data.get("customer_aging")
		customer_data = customer_data.get("customer_data")


		# frappe.log_error(customer_data)
		# frappe.log_error(customer_aging)
		# frappe.log_error(customer_summary)

		if customer_detail:
			frappe.log_error("customer_detail")
			new_doc = frappe.new_doc("Customer Scheduler Report")
			frappe.log_error(cstr(set_filters))
			start_month = set_filters.get("from_date")
			sended_date = set_filters.get("scheduler_date")
			new_doc.customer =  customer_detail.get("customer")
			new_doc.company: header_dict.get("company")
			# new_doc.currency =  "KES"
			new_doc.customer_address = customer_detail.get("address")
			new_doc.phone = customer_detail.get("phone")
			new_doc.email = customer_detail.get("Email")
			new_doc.amount_due =  "0.0"
			new_doc.scheduler_date =  set_filters.get("scheduler_date")
			new_doc.start_date =  set_filters.get("from_date")
			new_doc.start_date =  set_filters.get("from_date")
			new_doc.end_date =  set_filters.get("to_date")
			new_doc.details = []
			if customer_data:
				for i in customer_data:
					new_doc.append("details" , {
						'date': i.get("date"), 
						"voucher_no" : i.get("docno"),
						"description" : i.get("doctype"),
						"allocation" : i.get("allocation"),
						"credit" : i.get("credit") or 0 ,
						"debit" : i.get("debit") or 0,
						"balance" : i.get("balance") or 0,
						})
			if customer_summary:
				new_doc.total_sales = customer_summary.get("sales")
				new_doc.total_payment =  customer_summary.get("payment")
				new_doc.total_sales_return =  customer_summary.get("sales_return")


			if customer_aging:
				frappe.log_error(cstr(customer_aging))
				new_doc.age_30 = customer_aging.get("30")
				new_doc.age_60 = customer_aging.get("60")
				new_doc.age_90 = customer_aging.get("90")
				new_doc.aage_above = customer_aging.get("Above")

			new_doc.save()
			frappe.db.commit()

			attachments = [frappe.attach_print("Customer Scheduler Report", new_doc.name, print_format="Customer Scheduler Report Template")]





		frappe.msgprint("Inside send_data_by_eamil_to_customer  ")

		content_template =  frappe.render_template('impala/templates/customer_sechedular_template.html', {
			"customer_data" : customer_data,
			"customer_summary" : customer_summary,
			"customer_detail" : customer_detail , 
			"customer_aging" : customer_aging,
			"mheading" : header_dict

		})

		# attachments = [frappe.attach_print("Customer Scheduler Report", new_doc.name, print_format="Customer Scheduler Report Template")]

		attachments = attachments

		frappe.sendmail(
			recipients = ["waliullahthebo@gmail.com"], #this is the email to your recipient as you want
			subject = "The subject of your email",
			content = "Monthly Report" , 
			attachments =  attachments ,
			now = True
		)








		# attachments: [frappe.attach_print(self.doctype, self.name, file_name=self.name, password=password)],



@frappe.whitelist(allow_guest = True)
def customer_report(filters):
	filters = {
	"customer" : "AtoZGLASS" , 
	"from_date" : 	"01-04-2022" , 
	"to_date" : "30-04-2022",
	"company" : "Impala Glass Industries Ltd" , 
	"age1" : 30,
	"age2" : 60,
	"age3" : 90,
	"age4" : 120,
	}

	data = []
	
	frappe.log_error("customer_report" + cstr(filters))
	
	child_table_data = []
	customer_aging = {}
	customer_detail = {}
	header_dict = {}

	data = get_customer_data(filters)
	# chart = get_chart(filters)
	summary = get_summary(filters)

	header_dict = get_header(filters)
	if data:

		child_table_data = data.get("child_table_data")
		customer_aging = data.get("aging")

		customer_doc = frappe.get_doc("Customer" , filters.get("customer"))
		if customer_doc:
			customer_detail = {
				"customer" : customer_doc.name,
				"address" : customer_doc.primary_address

			}
	values = {
	"customer_detail" : customer_detail , 
	"customer_data" : child_table_data , 
	"customer_summary" : summary , 
	"customer_aging" : customer_aging ,
	"header_dict" : header_dict 
	}

	return values

@frappe.whitelist(allow_guest = True)
def get_summary(filters):

	# filters = {
	# "customer" : "AtoZGLASS" , 
	# "from_date" : 	"01-04-2022" , 
	# "to_date" : "30-04-2022",
	# "company" : "Impala Glass Industries Ltd" , 
	# "age1" : 30,
	# "age2" : 60,
	# "age3" : 90,
	# "age4" : 120,
	# }





	filter = ""
	if filters.get("from_date"):
		filter += " and posting_date >=  '{}'   ".format(filters.get("from_date")) 
	if filters.get("to_date"):
		# filter += ' and posting_date <= "' + filters.get("to_date") + '"'
		filter += " and posting_date <=  '{}'   ".format(filters.get("to_date")) 

	if filters.get("customer"):
		# filter += ' and customer = "' + filters.get("customer") + '"'
		filter += " and customer =  '{}' ".format(filters.get("customer"))

	sales = frappe.db.sql(
		"""
		SELECT
			sum(rounded_total) as total_sales
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
			sum(rounded_total) as total_return
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




	if filters.get("from_date"):
		pay_filter += " and posting_date >=  '{}'   ".format(filters.get("from_date")) 
	if filters.get("to_date"):
		# filter += ' and posting_date <= "' + filters.get("to_date") + '"'
		pay_filter += " and posting_date <=  '{}'   ".format(filters.get("to_date")) 

	if filters.get("customer"):
		# filter += ' and customer = "' + filters.get("customer") + '"'
		pay_filter += " and party  =  '{}' ".format(filters.get("customer"))




	# if filters.get("from_date"):
	# 	pay_filter += ' and posting_date >= "' + filters.get("from_date") + '"'
	# if filters.get("to_date"):
	# 	pay_filter += ' and posting_date <= "' + filters.get("to_date") + '"'
	# if filters.get("customer"):
	# 	pay_filter += ' and party = "' + filters.get("customer") + '"'





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
	return_dict = {
		"sales" : 0 , 
		"sales_return" : 0 , 
		"payment" : 0 , 
	}
	if sales:
		summary.append(
			{
				"label": "Sales",
				"value": frappe.utils.fmt_money(sales[0].total_sales or 0),
				"color": "#456789",
			}
		)
		return_dict["sales"] = frappe.utils.fmt_money(sales[0].total_sales or 0)
	if sales_return:
		summary.append(
			{
				"label": "Sales Return",
				"value": frappe.utils.fmt_money(sales_return[0].total_return or 0),
				"color": "#EE8888",
			}
		)
		return_dict["sales_return"] = frappe.utils.fmt_money(sales_return[0].total_return or 0)

	if payment:
		summary.append(
			{
				"label": "Payment",
				"value": frappe.utils.fmt_money(payment[0].total_payment or 0),
				"color": "#FFBB00",
			}
		)
		return_dict["payment"] = frappe.utils.fmt_money(payment[0].total_payment or 0)


	# return_dict = {

	# 		"sales" : sales , 
	# 		"payment" : payment , 
	# 		"sales_return" : sales_return , 

	# }
	return return_dict




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
	if filters.get("from_date"):
		filter += ' and posting_date >= "' + filters.get("from_date") + '"'
	if filters.get("to_date"):
		filter += ' and posting_date <= "' + filters.get("to_date") + '"'
	if filters.get("customer"):
		filter += ' and customer = "' + filters.get("customer") + '"'
	for mon in month:

		sales = frappe.db.sql(
			"""
			SELECT
				monthname(posting_date) as month,
				sum(rounded_total) as sales
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
				filter, mon, filters.get("to_date").split("-")[0]
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
				sum(rounded_total) as sales_return
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
				filter, mon, filters.get("to_date").split("-")[0]
			),
			as_dict=1,
		)
		if sales_return:
			chart["data"]["datasets"][1]["values"].append(sales[0]["sales_return"])
		else:
			chart["data"]["datasets"][1]["values"].append(0)
		pay_filter = ""
		if filters.get("from_date"):
			pay_filter += ' and posting_date >= "' + filters.get("from_date") + '"'
		if filters.get("to_date"):
			pay_filter += ' and posting_date <= "' + filters.get("to_date") + '"'
		if filters.get("customer"):
			pay_filter += ' and party = "' + filters.get("customer") + '"'

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
				pay_filter, mon, filters.get("to_date").split("-")[0]
			),
			as_dict=1,
		)
		if payment:
			chart["data"]["datasets"][2]["values"].append(payment[0]["payment"])
		else:
			chart["data"]["datasets"][2]["values"].append(0)
	return chart

@frappe.whitelist()
def get_customer_data(filters = None):
	filters = {
	"customer" : "AtoZGLASS" , 
	"from_date" : 	"2022-04-01" , 
	"to_date" : "2022-04-30",
	"company" : "Impala Glass Industries Ltd" , 
	"age1" : 30,
	"age2" : 60,
	"age3" : 90,
	"age4" : 120,
	}
	frappe.log_error("get_customer_data - filters" + cstr(filters))

	final_data = []

	condition = ""

	condition_customer_1 = ""
	condition_customer_2 = ""

	data = []
	child_table_data = []
	total_amount = 0
	opening = []
	opening_payment = []

	opening_balance_detail = {
				"docno": "Opening",
				"debit": 0,
				"credit": 0,
				"balance": 0,


	}


	if filters.get("company"):
		condition += " and company = '{}' ".format(filters.get("company"))

	if filters.get("customer"):
		condition_customer_1 += " and customer = '{}' ".format(filters.get("customer"))
		condition_customer_2 += " and party = '{}' ".format(filters.get("customer"))


	if filters.get("from_date") and  filters.get("to_date"):
		condition += " and posting_date between  {} and {} ".format(filters.get("from_date") , filters.get("to_date"))
		condition += " and posting_date between  '{}' and '{}' ".format(filters.get("from_date") , filters.get("to_date"))


	if condition:
		opening = frappe.db.sql(
			""" select SUM(outstanding_amount) as outstanding from `tabSales Invoice` 
			where docstatus=1 and is_pos=0 and 
			outstanding_amount>0 {} {} """.format(condition , condition_customer_1),
			as_dict=True,debug = 1)

		if opening:
			opening = opening[0].outstanding or  0
		else:
			opening = 0.0



		opening_payment = frappe.db.sql(
			""" select paid_amount as paid_amount from `tabPayment Entry` 
			where docstatus=1 and payment_type='Receive' and paid_amount>0 
			{} {} """.format(condition , condition_customer_2),
			as_dict=True, debug = 1
		)


		if opening_payment:
			total_paid = opening_payment[0].paid_amount or 0
		else:
			total_paid = 0

		opening_balance_detail.update(
			{
				"docno": "Opening",
				"debit": opening,
				"credit": total_paid,
				"balance": opening - total_paid,
			}
			)



		sales_invoice_sales_data = frappe.db.sql(
			""" select posting_date, customer, name as voucher_no, rounded_total as debit 
			from `tabSales Invoice` 
			where docstatus=1 and is_pos=0  {} {} order by posting_date ASC  """.format(condition , condition_customer_1 ),
		as_dict=1, debug  =1)


		payment_entery_data = frappe.db.sql(
			""" select posting_date, party as customer, name as voucher_no, paid_amount as credit from `tabPayment Entry` 
			where docstatus=1 {} {} order by posting_date ASC """.format(condition , condition_customer_2)
		)

		final_data = []


		for i in sales_invoice_sales_data:
			row = {
				"docno" : "" , 
				"date" : i.get("posting_date") , 
				"customer" : i.get("customer") , 
				"voucher_no" : i.get("voucher_no") , 
				"debit" : i.get("debit") , 
				"balance" : "" , 
			}
			final_data.append(row)


		for i in payment_entery_data:
			row = {
				"docno" : "" , 
				"date" : i.get("posting_date") , 
				"customer" : i.get("customer") , 
				"voucher_no" : i.get("voucher_no") , 
				"debit" : i.get("debit") , 
				"credit" : i.get("credit") , 
				"balance" : "" , 
			}
			final_data.append(row)
	
	return final_data







def get_age(posting_date, to_date, filters):


	to_date = str(to_date)

	a_y = to_date.split("-")[0]
	a_m = to_date.split("-")[1]
	a_d = to_date.split("-")[2]

	c = a_d + "-" + a_m + "-" + a_y
	print(c)
	frappe.log_error(c)





	posting_date = datetime.strptime(str(posting_date), "%Y-%m-%d").date()
	to_date = datetime.strptime(str(c), "%d-%m-%Y").date()
	period = (to_date - posting_date).days + 1

	if filters.get("age1") and period <= filters.get("age1"):
		return filters.get("age1")
	elif filters.get("age2") and period <= filters.get("age2"):
		return filters.get("age2")
	elif filters.get("age3") and period <= filters.get("age3"):
		return filters.get("age3")
	elif filters.get("age4") and period <= filters.get("age4"):
		return filters.get("age4")
	else:
		return "Above"

@frappe.whitelist(allow_guest  = True)
def get_header(filters):
	# filters = {
	# "customer" : "AtoZGLASS" , 
	# "from_date" : 	"01-04-2022" , 
	# "to_date" : "30-04-2022",
	# "company" : "Impala Glass Industries Ltd" , 
	# "age1" : 30,
	# "age2" : 60,
	# "age3" : 90,
	# "age4" : 120,
	# }



	company_details = frappe.db.get_list(
		"Company",
		filters={"name": filters.get("company")},
		fields=[
			"company_name",
			"phone_no",
			"email",
			"tax_id",
			"company_logo",
			"website",
		],
	)

	header_dict = {
		"comapny_address_line1" : "" , 
		"company": "",
		"company_address": "",
		"city": "",
		"country": "",
		"state": "",
		"phone_no": "",
		"email": "",
		"pin_no": "",
		"company_logo": "",
		"website": "",
	}


	company_address_name = frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Company", "link_name": filters.get("company")},
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

	header_dict.update( 
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
	})



	return  header_dict







# def send_data_by_eamil_to_customer():

# 	content_template =  frappe.render_template('impala/templates/customer_sechedular_template.html', {
# 		'customer_name': "Waliullah",
# 		"child_table_data" : child_table_data
# 	if child_table_data:
# 		child_table_data = child_table_data

# 	})






@frappe.whitelist(allow_guest  = True)
def b():
	child_table_data = customer_report()
	return child_table_data
	doc  = {
		"customer_name" : "Waliullah"
	}
	if child_table_data:
		child_table_data = child_table_data

	content =  frappe.render_template('impala/templates/customer_sechedular_template.html', {
			'customer_name': "Waliullah",
			"child_table_data" : child_table_data
		})



	# attachment=[{"file_url":"my_file_path.pdf","name":"1a0ec47280","is_private":1}]
 



	get_pdf_m  = frappe.utils.pdf.get_pdf(content)

	f = save_file(fname = "waliw.pdf", content = get_pdf_m, dt = "Customer Scheduler", dn = "Customer Scheduler", 
		folder=None, decode=False, is_private=0, df=None)

	frappe.log_error(type(f))




	attachments = '[frappe.attach_print("Customer Scheduler", "Customer Scheduler" , file_name="waliwe91daf.pdf")]'




	# file_url = f.file_url
	# name = f.name
	# is_private = f.is_private
	# attachment = "{'file_url' : '{}' , 'name' : '{}' , 'is_private' : '{}' } ".format(file_url , name , is_private)
	# attachment='[attachment]'

		# return attachment




	# {"message":{"name":"a09ff2233e",
	# "owner":"Administrator","creation":"2022-05-09 19:27:36.405827",
	# "modified":"2022-05-09 19:27:36.405827",
	# "modified_by":"Administrator","idx":0,"docstatus":0,
	# "file_name":"wali.pdf","is_private":0,"is_home_folder":0,
	# "is_attachments_folder":0,"file_size":21730,
	# "file_url":"/files/wali.pdf","folder":"Home/Attachments",
	# "is_folder":0,"attached_to_doctype":"Customer Scheduler",
	# "attached_to_name":"Customer Scheduler",
	# "content_hash":"f9a0c1e2e0aee73b73d0124633e91daf",
	# "uploaded_to_dropbox":0,"uploaded_to_google_drive":0,"doctype":"File"}}




	# _file = frappe.get_doc("File", f.name)
	# fcontent = _file.get_content()
	# attachments = {"fid": fcontent }

	frappe.sendmail(
		recipients = ["waliullahthebo@gmail.com" , "irfansalman88@gmail.com"], #this is the email to your recipient as you want
		subject = "The subject of your email",
		content = content , 
		attachments=attachments,
		now = True
	)



	# output  = frappe.get_print(doctype="Customer", name="EZYabdinoorkilas", print_format="Scheduler Report", style=None, html=None, as_pdf=True, doc=doc, output = None, no_letterhead = 0)

	# attachments =  [frappe.attach_print("Customer" ,  'EZYabdinoorkilas' , file_name="EZYabdinoorkilas")],

	# html = frappe.get_print(doctype = "Customer", name = "EZYabdinoorkilas", format, doc=doc, no_letterhead=no_letterhead)
	# frappe.local.response.filename = "Waliullah"
	# att = frappe.local.response.filecontent = get_pdf(content)
	# frappe.local.response.type = "pdf"







		# if receiver:
		# 	email_args = {
		# 		"recipients": [receiver],
		# 		"message": _("Please see attachment"),
		# 		"subject": 'Salary Slip - from {0} to {1}'.format(self.start_date, self.end_date),
		# 		"attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
		# 		"reference_doctype": self.doctype,
		# 		"reference_name": self.name
		# 		}
		# 	enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)


@frappe.whitelist(allow_guest = True)
def gernerate_pdf():
	html = frappe.get_print(doctype, name, format, doc=doc, no_letterhead=no_letterhead)
	frappe.local.response.filename = "Waliullah"
	frappe.local.response.filecontent = get_pdf(html)
	frappe.local.response.type = "pdf"









@frappe.whitelist()
def download_pdf(doctype, name, format=None, doc=None, no_letterhead=0):
	html = frappe.get_print(doctype, name, format, doc=doc, no_letterhead=no_letterhead)
	frappe.local.response.filename = "{name}.pdf".format(
		name=name.replace(" ", "-").replace("/", "-")
	)
	frappe.local.response.filecontent = get_pdf(html)
	frappe.local.response.type = "pdf"


def save_and_attach(content, to_doctype = "Customer Scheduler", to_name = "Customer Scheduler", folder = "Public"):
	"""
	Save content to disk and create a File document.
	File document is linked to another document.
	"""
	file_name = "{}.pdf".format(to_name.replace(" ", "-").replace("/", "-"))
	save_file(file_name, content, to_doctype,
			  to_name, folder=folder, is_private=1)



