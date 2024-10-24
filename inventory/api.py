import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


@frappe.whitelist()
def get_item_stock(item,warehouse):
    sle_doctype = DocType('Stock Ledger Entry')
    query_result = (frappe.qb.from_(sle_doctype)
    .where((sle_doctype.item == item) & (sle_doctype.warehouse == warehouse))
    .select(Sum(sle_doctype.quantity_change).as_('item_stock'))).run(as_dict=True)[0]
    print(query_result.item_stock)
    return query_result.item_stock if query_result.item_stock else 0

@frappe.whitelist()
def get_valuation_rate(item,warehouse):
    sle_doctype = DocType("Stock Ledger Entry")
    query_result = (frappe.qb.from_(sle_doctype)
				.where((sle_doctype.item==item) & (sle_doctype.warehouse==warehouse))
				.select(
					Sum(sle_doctype.quantity_change*sle_doctype.valuation_rate).as_('balance_value'),
					Sum(sle_doctype.quantity_change).as_('total_quantity')
				)).run(as_dict=True)[0]
    """ {'balance_value': 300000000.0, 'total_quantity': 5000.0} """
    print(query_result)
    balance_value,total_quantity = (query_result.balance_value,query_result.total_quantity) if query_result.balance_value else (0,0)
    valuation_rate = (balance_value/total_quantity) if total_quantity else 0
    print(valuation_rate)
    return valuation_rate





