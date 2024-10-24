# Copyright (c) 2024, Asmita Hase and Contributors
# See license.txt

import frappe
import frappe.tests
from frappe.tests.utils import FrappeTestCase


class TestItems(FrappeTestCase):
	
	def setUp(self):
		frappe.set_user("Administrator")
		create_items()
	
	def tearDown(self):
		frappe.set_user("Administrator")

	def test_item_created(self):
		self.assertTrue(frappe.db.exists("Items",{"item_name":"Item 1"}))
	
	def test_default_warehouse(self):
		self.assertEqual(frappe.get_doc("Items",{"item_name":"Item 1"}).opening_warehouse,
				   frappe.db.get_single_value("Settings",'default_warehouse'))

def create_items():
	if frappe.flags.test_items_created:
		return
	if not frappe.db.exists("Items",{"item_code":"TEST-001"}):
		doc = frappe.get_doc({
				"doctype":"Items",
				"item_name":"Item 1",
				"item_code":"TEST-001",
				"opening_quantity":10,
				"opening_valuation_rate":100.0		
			}).insert()
	frappe.flags.test_items_created = True
			


	
