# Copyright (c) 2024, Asmita Hase and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Items(Document):
	
	def before_validate(self):
		if self.is_entry_type_recieve() and not self.opening_warehouse:
			self.opening_warehouse = frappe.db.get_single_value('Settings','default_warehouse')

	def validate(self):
		if self.is_entry_type_recieve():
			self.validate_opening()

	def validate_opening(self):
		if not self.opening_quantity:
			frappe.throw("Opening quantity for item is not set")
		if not self.opening_valuation_rate:
			frappe.throw('Opening valuation rate for item is not set')


	def after_insert(self):
		self.create_stock_entry()

	def create_stock_entry(self):
		stock_entry_document = frappe.new_doc(
			'Stock Entry',
			entry_type='Receive',
			valuation_method='Moving Average',
			)
		stock_entry_document.append(
			'items',
			{
				'item':self.item_code,
				'quantity':self.opening_quantity,
				'rate':self.opening_valuation_rate,
				'target_warehouse':self.opening_warehouse
			})
		stock_entry_document.insert()
		stock_entry_document.submit()

	def is_entry_type_recieve(self):
		return self.opening_valuation_rate or self.opening_quantity
	
	

		
		
			
		


