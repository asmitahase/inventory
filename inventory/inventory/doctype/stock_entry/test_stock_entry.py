# Copyright (c) 2024, Asmita Hase and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..items.test_items import create_items


class TestStockEntry(FrappeTestCase):
	
	def setUp(self):
		frappe.set_user("Administrator")
	
	def tearDown(self):
		frappe.set_user("Administrator")


		
		



