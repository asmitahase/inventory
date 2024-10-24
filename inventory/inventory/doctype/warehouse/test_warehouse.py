# Copyright (c) 2024, Asmita Hase and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestWarehouse(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		create_warehouse()

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_create_warehouse(self):
		self.assertTrue(frappe.db.exists("Warehouse",{"warehouse_name":"Warehouse A"}))


def create_warehouse():
	if frappe.flags.test_warehouse_created:
		return

	doc = frappe.get_doc({
		"doctype":"Warehouse",
		"warehouse_name":"Warehouse A",
		"contact":"+918888888888",
		"is_group":0
	}).insert()

	frappe.flags.test_warehouse_created = True
