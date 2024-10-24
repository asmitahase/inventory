# Copyright (c) 2024, Asmita Hase and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum

class StockEntry(Document):

	def validate(self):
		if self.entry_type in ['Transfer','Consume']:
			self.validate_item_stock(warehouse_type='source_warehouse')

	def on_submit(self):
		if self.entry_type == "Receive":
			self.submit_receive()
		if self.entry_type == "Transfer":
			self.submit_transfer()
		if self.entry_type == "Consume":
			self.submit_consume()

	def on_cancel(self):
		if self.entry_type == "Receive":
			self.cancel_receive()
		if self.entry_type == "Transfer":
			self.cancel_transfer()
		if self.entry_type == "Consume":
			self.cancel_consume()
		

	def cancel_receive(self):
		self.validate_item_stock(warehouse_type='source_warehouse')
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.source_warehouse,
				-abs(item.quantity),
				item.rate,
				self.name
			)
	def cancel_consume(self):
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.source_warehouse,
				abs(item.quantity),
				item.rate,
				self.name
			)
	def cancel_transfer(self):
		self.validate_item_stock(warehouse_type='target_warehouse')
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.source_warehouse,
				abs(item.quantity),
				item.rate,
				self.name
			)
			create_stock_ledger_entry(
				item.item,
				item.target_warehouse,
				-abs(item.quantity),
				item.rate,
				self.name
			)
	def submit_receive(self):
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.target_warehouse,
				item.quantity,
				item.rate,
				self.name
			)
	def submit_transfer(self):
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.target_warehouse,
				item.quantity,
				item.rate,
				self.name
			)
			create_stock_ledger_entry(
				item.item,
				item.source_warehouse,
				-abs(item.quantity),
				item.rate,
				self.name
			)
	def submit_consume(self):
		for item in self.items:
			create_stock_ledger_entry(
				item.item,
				item.source_warehouse,
				-abs(item.quantity),
				item.rate,
				self.name
			)
	def validate_item_stock(self,warehouse_type):
		grouped_items = group_items_by_warehouse(self.items,warehouse_type)
		for item in grouped_items:
			item_stock = get_item_stock(item['item'], item['warehouse'])
			if item_stock < item['quantity']:
				frappe.throw(
					_("Insufficient stock of item {0} available at warehouse {1}".format(item["item"], item["warehouse"]))
				)

def create_stock_ledger_entry(item,warehouse,quantity,rate,stock_entry):
	stock_ledger_entry = frappe.new_doc(
		"Stock Ledger Entry",
		item=item,
		warehouse=warehouse,
		quantity_change=quantity,
		in_out_rate=rate,
		valuation_rate = calculate_valuation_rate(item,warehouse,rate,quantity),
		stock_entry=stock_entry
		)
	stock_ledger_entry.insert()
	
def calculate_valuation_rate(item,warehouse,rate,quantity):
	sle_doctype = DocType("Stock Ledger Entry")
	query_result = (frappe.qb.from_(sle_doctype)
				.where((sle_doctype.item==item) & (sle_doctype.warehouse==warehouse))
				.select(
					Sum(sle_doctype.quantity_change*sle_doctype.valuation_rate).as_('balance_value'),
					Sum(sle_doctype.quantity_change).as_('total_quantity')
				)).run(as_dict=True)[0]
	""" {'balance_value': 300000000.0, 'total_quantity': 5000.0} """
	balance_value,total_quantity = (query_result.balance_value,query_result.total_quantity)\
		  							if query_result.balance_value else (0,0)
	new_valuation_rate = (balance_value + (rate*quantity))/(total_quantity + quantity)
	return new_valuation_rate

def get_item_stock(item, warehouse):
	sle_doctype = DocType("Stock Ledger Entry")
	query_result = (
		frappe.qb.from_(sle_doctype)
		.where((sle_doctype.item == item) & (sle_doctype.warehouse == warehouse))
		.select(Sum(sle_doctype.quantity_change).as_('item_stock'))
	).run(as_dict=True)[0]
	return query_result.item_stock or 0

def group_items_by_warehouse(items,warehouse_type):
	grouped_items = {}
	for item in items:
		warehouse = item.source_warehouse if (warehouse_type=='source_warehouse') else item.target_warehouse
		key = f"{item.item}-{warehouse}"
		if key not in grouped_items:
			grouped_items[key] = {
				'item':item.item,
				'warehouse':warehouse,
				'quantity':item.quantity
			}
		grouped_items[key]["quantity"] += item.quantity 
	return list(grouped_items.values())

	
	

