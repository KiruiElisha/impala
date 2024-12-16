# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate
from six import iteritems, itervalues

from impala.impala.report.customer_ledger_summary_impala.customer_ledger_summary_impala import (
	PartyLedgerSummaryReport,
)
def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return PartyLedgerSummaryReport(filters).run(args)