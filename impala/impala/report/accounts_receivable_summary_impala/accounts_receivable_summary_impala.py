# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


import frappe
from frappe import _, scrub
from frappe.utils import cint, flt, cstr
from six import iteritems

from erpnext.accounts.party import get_partywise_advanced_payment_amount
from impala.impala.report.accounts_receivable_impala.accounts_receivable_impala import ReceivablePayableReport


def execute(filters=None):
	args = {
		"party_type": "Customer",
		"naming_by": ["Selling Settings", "cust_master_name"],
	}

	return AccountsReceivableSummary(filters).run(args)

class AccountsReceivableSummary(ReceivablePayableReport):
	def run(self, args):
		self.party_type = args.get('party_type')
		self.party_naming_by = frappe.db.get_value(args.get("naming_by")[0], None, args.get("naming_by")[1])
		self.get_columns()
		self.get_data(args)
		return self.columns, self.data

	def get_data(self, args):
		self.data = []

		self.receivables = ReceivablePayableReport(self.filters).run(args)[1]

		self.get_party_total(args)

		party_advance_amount = get_partywise_advanced_payment_amount(self.party_type,
			self.filters.report_date, self.filters.show_future_payments, self.filters.company) or {}

		if self.filters.show_gl_balance:
			gl_balance_map = get_gl_balance(self.filters.report_date)

		for party, party_dict in iteritems(self.party_total):
			if party_dict.outstanding == 0:
				continue

			row = frappe._dict()

			row.party = party
			if frappe.db.exists('Customer', party):
				doc = frappe.get_doc('Customer', party)
				row.party_name = doc.customer_name
			else:
				party_name = party

			if self.party_naming_by == "Naming Series":
				row.party_name = frappe.get_cached_value(self.party_type, party, scrub(self.party_type) + "_name")
			row.update(party_dict)

			# Advance against party
			row.advance = party_advance_amount.get(party, 0)

			# In AR/AP, advance shown in paid columns,
			# but in summary report advance shown in separate column
			row.paid -= row.advance

			if self.filters.show_gl_balance:
				# row.gl_balance = "Sh " + str("{:,}".format(float(gl_balance_map.get(party))))
				row.gl_balance = gl_balance_map.get(party)
				row.diff = flt(row.outstanding) - flt(gl_balance_map.get(party))


			party_pdcheques = frappe.db.sql("""select GROUP_CONCAT(name SEPARATOR ', ') as pdcheques, SUM(base_amount) as pdc_amount
			from `tabPosted Dated Cheques`
			where company='{}' and docstatus=1 and status='Pending' and party_type='Customer' and party = "{}"
			""".format(self.filters.company, party), as_dict=1)

			row["pdcheques"] = party_pdcheques[0]["pdcheques"]
			row["pdc_amount"] = party_pdcheques[0]["pdc_amount"]
			row["net_outstanding"] =  (row.outstanding if row.outstanding else 0.0) - (party_pdcheques[0]["pdc_amount"] if party_pdcheques[0]["pdc_amount"] else 0.0)
			self.data.append(row)

	def get_party_total(self, args):
		self.party_total = frappe._dict()

		for d in self.receivables:
			self.init_party_total(d)

			# Add all amount columns
			for k in list(self.party_total[d.party]):
				if k not in ["currency", "sales_person"]:
					self.party_total[d.party][k] += d.get(k, 0.0)

			# set territory, customer_group, sales person etc
			self.set_party_details(d)

	def init_party_total(self, row):
		

		self.party_total.setdefault(row.party, frappe._dict({
			"invoiced": 0.0,
			"paid": 0.0,
			"credit_note": 0.0,
			"outstanding": 0.0,
			"range1": 0.0,
			"range2": 0.0,
			"range3": 0.0,
			"range4": 0.0,
			"range5": 0.0,
			"total_due": 0.0,
			"sales_person": [],
		}))

	def set_party_details(self, row):
		self.party_total[row.party].currency = row.currency

		for key in ('territory', 'customer_group', 'supplier_group'):
			if row.get(key):
				self.party_total[row.party][key] = row.get(key)

		if row.sales_person:
			self.party_total[row.party].sales_person.append(row.sales_person)

	def get_columns(self):
		self.columns = []
		self.add_column(label=_(self.party_type), fieldname='party',
			fieldtype='Link', options=self.party_type, width=180)

		self.add_column(label=_('Party Name'), fieldname='party_name',
			fieldtype='Data', width=200)

		if self.party_naming_by == "Naming Series":
			self.add_column(_('{0} Name').format(self.party_type),
				fieldname = 'party_name', fieldtype='Data')

		credit_debit_label = "Credit Note" if self.party_type == 'Customer' else "Debit Note"

		self.add_column(_('Advance Amount'), fieldname='advance')
		self.add_column(_('Invoiced Amount'), fieldname='invoiced')
		self.add_column(_('Paid Amount'), fieldname='paid')
		self.add_column(_(credit_debit_label), fieldname='credit_note')
		self.add_column(_('Outstanding Amount'), fieldname='outstanding')
		if self.filters.show_gl_balance:
			self.columns.append(
				{
					'label' : _('GL Balance'), 'fieldname':'gl_balance', 'fieldtype':'Data', 'align':'right', 'width': 180})
			# self.add_column(_('GL Balance'), fieldname='gl_balance', fieldtype='Data', align='right')
			self.add_column(_('Difference'), fieldname='diff')

		self.setup_ageing_columns()

		if self.party_type == "Customer":
			self.add_column(label=_('Territory'), fieldname='territory', fieldtype='Link',
				options='Territory')
			self.add_column(label=_('Customer Group'), fieldname='customer_group', fieldtype='Link',
				options='Customer Group')
			if self.filters.show_sales_person:
				self.add_column(label=_('Sales Person'), fieldname='sales_person', fieldtype='Data')
		else:
			self.add_column(label=_('Supplier Group'), fieldname='supplier_group', fieldtype='Link',
				options='Supplier Group')

		self.add_column(label=_('Currency'), fieldname='currency', fieldtype='Link',
			options='Currency', width=80)
		self.add_column(_('PD Cheques'), fieldname='pdcheques', fieldtype='Data')
		self.add_column(_('PDC Amount'), fieldname='pdc_amount', fieldtype='Currency')
		self.add_column(_('Net Outstanding'), fieldname='net_outstanding', fieldtype='Currency')
	def setup_ageing_columns(self):
		for i, label in enumerate(["0-{range1}".format(range1=self.filters["range1"]),
			"{range1}-{range2}".format(range1=cint(self.filters["range1"])+ 1, range2=self.filters["range2"]),
			"{range2}-{range3}".format(range2=cint(self.filters["range2"])+ 1, range3=self.filters["range3"]),
			"{range3}-{range4}".format(range3=cint(self.filters["range3"])+ 1, range4=self.filters["range4"]),
			"{range4}-{above}".format(range4=cint(self.filters["range4"])+ 1, above=_("Above"))]):
				self.add_column(label=label, fieldname='range' + str(i+1))

		# Add column for total due amount
		self.add_column(label="Total Amount Due", fieldname='total_due')

def get_gl_balance(report_date):

	return frappe._dict(frappe.db.get_all("GL Entry", fields=['party', 'sum(debit -  credit)'],
		filters={'posting_date': ("<=", report_date), 'is_cancelled': 0}, group_by='party', as_list=1))
