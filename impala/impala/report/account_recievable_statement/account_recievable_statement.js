// Copyright (c) 2022, Codes Soft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Account Recievable Statement"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      reqd: 1,
      default: frappe.defaults.get_user_default("Company"),
    },
    {
      fieldname: "from_date",
      fieldtype: "Date",
      label: "From Date",
      reqd: 0,
    },
    {
      fieldname: "to_date",
      fieldtype: "Date",
      label: "To Date",
      default: frappe.datetime.get_today(),
      reqd: 1,
    },
    {
      fieldname: "customer",
      fieldtype: "Link",
      label: "Customer",
      options: "Customer",
      reqd: 1,
    },
    {
      fieldname: "age1",
      label: "Age 1",
      fieldtype: "Int",
      default: 30,
    },
    {
      fieldname: "age2",
      label: "Age 2",
      fieldtype: "Int",
      default: 60,
    },
    {
      fieldname: "age3",
      label: "Age 3",
      fieldtype: "Int",
      default: 90,
    },
    {
      fieldname: "age4",
      label: "Age 4",
      fieldtype: "Int",
      default: 120,
    },
  ],
  onload: function (frm) {
    frappe.query_report._get_filters_html_for_print =
      frappe.query_report.get_filters_html_for_print;
    frappe.query_report.get_filters_html_for_print = (print_settings) => {
      const me = frappe.query_report,
        encode = (svg) =>
          "data:image/svg+xml;base64," +
          btoa(new XMLSerializer().serializeToString(svg));
      let applied_filters = "";

      if (me.chart && me.chart.svg) {
        applied_filters += `<hr><img alt="${__("Chart")}" src="${encode(
          me.chart.svg
        )}" />`;
      }
      console.log(applied_filters);
      return applied_filters;
    };
  },
};
