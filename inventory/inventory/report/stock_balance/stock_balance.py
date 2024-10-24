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

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"fieldname": "item", 
			"label": "Item",
			"fieldtype": "Link", 
			"options": "Items",
			"width":200,
		},
        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
			"width":200,
        },
        {
            "fieldname": "balance_quantity",
            "label": "Balance Quantity",
            "fieldtype": "int",
            "options": "Balance Quantity",
			"width":200,
        },
        {
            "fieldname": "valuation_rate",
            "label": "Valuation Rate",
            "fieldtype": "float",
            "options": "Valuation Rate",
			"width":200,
        },
        {
            "fieldname": "balance_value",
            "label": "Balance Value",
            "fieldtype": "float",
            "options": "Balance Value",
			"width":200,
        },
	]
def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	sle = DocType("Stock Ledger Entry")
	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item,
			sle.warehouse,
			Round(sle.valuation_rate,2).as_('valuation_rate'),
			Sum(sle.quantity_change).as_('balance_quantity'),
			Round(Sum(sle.quantity_change*sle.valuation_rate),2).as_('balance_value')
			)	
		.groupby(sle.item, sle.warehouse)
	)
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




    
