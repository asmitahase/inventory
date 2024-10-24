# Copyright (c) 2024, Asmita Hase and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Round

def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data(filters)
	print(data)
	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		 {
            "fieldname": "posting_date",
            "label": "Posting Date",
            "fieldtype": "date",
            "options": "Posting Date",
			"width":150,
        },
        {
            "fieldname": "posting_time",
            "label": "Posting Time",
            "fieldtype": "time",
            "options": "Posting Time",
			"width":150,
        },
        {
			"fieldname": "item", 
			"label": "Item",
			"fieldtype": "Link", 
			"options": "Items",
			"width":150,
		},
        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
			"width":150,
        },
        {
            "fieldname": "quantity_change",
            "label": "Quantity Change",
            "fieldtype": "int",
            "options": "Quantity Change",
			"width":150,
        },
        {
            "fieldname": "in_out_rate",
            "label": "In/Out Rate",
            "fieldtype": "float",
            "options": "In/Out Rate",
			"width":150,
        },
        {
            "fieldname": "valuation_rate",
            "label": "Valuation Rate",
            "fieldtype": "float",
            "options": "Valuation Rate",
			"width":150,
        },
        {
            "fieldname": "balance_value",
            "label": "Balance Value",
            "fieldtype": "float",
            "options": "Balance Value",
			"width":150,
        },
	]


def get_data(filters) -> list[list]:
	data = get_stock_ledger_entries(filters)
	return data

def get_stock_ledger_entries(filters):
	sle = DocType("Stock Ledger Entry")
	query = (frappe.qb.from_(sle)
		  .select(
			  sle.posting_date,
			  sle.posting_time,
			  sle.item,
			  sle.warehouse,
			  sle.quantity_change,
			  sle.stock_entry,
			  Round(sle.in_out_rate,2).as_('in_out_rate'),
			  Round(sle.valuation_rate,2).as_('valuation_rate'),
			  Round(sle.quantity_change*sle.valuation_rate,2).as_('balance_value')
		  )
		  .where(sle.docstatus<2)
		  .orderby(sle.creation)
		)
	query = apply_filters(query,sle,filters)
	data = query.run(as_dict=True)
	return data

def apply_filters(query,sle,filters):
	for key,value in filters.items():
		if key not in ['from_date','to_date'] and value:
			query = query.where(sle[key]==filters[key])
		if filters.get('from_date'):
			query = query.where(sle.posting_date >= filters.get('from_date'))
		if filters.get('to_date'):
			query = query.where(sle.posting_date <= filters.get('to_date'))
	return query