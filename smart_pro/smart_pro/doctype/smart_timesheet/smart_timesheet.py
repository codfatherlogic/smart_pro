# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SmartTimesheet(Document):
    def validate(self):
        self.validate_hours()
        self.validate_task_project()
        self.fetch_employee_name()

    def validate_hours(self):
        """Validate hours worked is between 0 and 24"""
        if self.hours_worked:
            if flt(self.hours_worked) <= 0:
                frappe.throw("Hours worked must be greater than 0")
            if flt(self.hours_worked) > 24:
                frappe.throw("Hours worked cannot exceed 24 hours per day")

    def validate_task_project(self):
        """Validate that task belongs to the selected project"""
        if self.task and self.project:
            task_project = frappe.db.get_value("Smart Task", self.task, "project")
            if task_project != self.project:
                frappe.throw(f"Task '{self.task}' does not belong to project '{self.project}'")

    def fetch_employee_name(self):
        """Fetch employee name from employee"""
        if self.employee and not self.employee_name:
            self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")

    def before_save(self):
        """Auto-fetch task title"""
        if self.task and not self.task_title:
            self.task_title = frappe.db.get_value("Smart Task", self.task, "title")
