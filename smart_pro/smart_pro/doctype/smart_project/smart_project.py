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
    
    @staticmethod
    def get_non_filterable_fields():
        return ["converted"]

    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Title",
                "type": "Data",
                "key": "title",
                "width": "12rem",
            },
            # {
            # 	"label": "Organization",
            # 	"type": "Link",
            # 	"key": "organization",
            # 	"options": "CRM Organization",
            # 	"width": "10rem",
            # },
            {
                "label": "Status",
                "type": "Select",
                "key": "status",
                "width": "8rem",
            },
            {
                "label": "Start Date",
                "type": "Date",
                "key": "start_date",
                "width": "8rem",
            },
            {
                "label": "End Date",
                "type": "Date",
                "key": "end_date",
                "width": "8rem",
            },
            {
                "label": "Last Modified",
                "type": "Datetime",
                "key": "modified",
                "width": "8rem",
            },
        ]
        rows = [
            "name",
            "project_name",
        ]
        return {"columns": columns, "rows": rows}

    @staticmethod
    def default_kanban_settings():
        return {
            "column_field": "status",
            "title_field": "project_name",
            "kanban_fields": '["priority", "project_type", "modified", "_assign"]',
        }
