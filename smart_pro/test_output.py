#!/usr/bin/env python
import frappe
frappe.init(user="Administrator")
frappe.connect()
print("Hello from test script")
print("Smart Project count:", frappe.db.count("Smart Project"))
frappe.close()