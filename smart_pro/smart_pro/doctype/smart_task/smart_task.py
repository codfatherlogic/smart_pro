import frappe
from frappe.model.document import Document

class SmartTask(Document):
    def before_insert(self):
        # Set default values if not provided
        if not self.status:
            self.status = "Open"
        if not self.priority:
            self.priority = "Medium"
        if not self.progress:
            self.progress = 0

    def validate(self):
        self.validate_dates()
        self.validate_progress()

    def validate_dates(self):
        if self.start_date and self.due_date and self.start_date > self.due_date:
            frappe.throw("Start Date cannot be after Due Date")

    def validate_progress(self):
        if self.progress and (self.progress < 0 or self.progress > 100):
            frappe.throw("Progress must be between 0 and 100")

    def on_update(self):
        # Auto-update status based on progress
        if self.progress == 100 and self.status != "Completed":
            self.status = "Completed"
        elif self.progress > 0 and self.status == "Open":
            self.status = "Working"