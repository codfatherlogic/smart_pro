import frappe
from frappe.model.document import Document

class SmartProject(Document):
    def before_insert(self):
        # Set project manager to current user if not set
        if not self.project_manager:
            self.project_manager = frappe.session.user

    def validate(self):
        self.validate_dates()
        self.update_project_status()

    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("Start Date cannot be after End Date")

    def update_project_status(self):
        # Auto-update status based on dates
        if self.status == "Planning" and self.start_date:
            from frappe.utils import today
            if self.start_date <= today():
                self.status = "Active"