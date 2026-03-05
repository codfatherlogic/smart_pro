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

    def after_insert(self):
        # Send notification for new task assignment
        self.send_assignment_notification()

    def on_update(self):
        # Auto-update status based on progress
        if self.progress == 100 and self.status != "Completed":
            self.status = "Completed"
        elif self.progress > 0 and self.status == "Open":
            self.status = "Working"

        # Send notification for task updates
        if self.has_value_changed("status") or self.has_value_changed("assigned_to"):
            self.send_update_notification()

    def send_assignment_notification(self):
        """Send notification when task is assigned"""
        from smart_pro.smart_pro.notifications import PushNotificationManager
        try:
            PushNotificationManager.send_task_assignment_notification(self)
        except Exception as e:
            frappe.log_error(str(e), "Task Assignment Notification Error")

    def send_update_notification(self):
        """Send notification when task is updated"""
        from smart_pro.smart_pro.notifications import PushNotificationManager
        try:
            PushNotificationManager.send_task_update_notification(self)
        except Exception as e:
            frappe.log_error(str(e), "Task Update Notification Error")


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
            {
            	"label": "Project",
            	"type": "Link",
            	"key": "project",
            	"options": "Smart Project",
            	"width": "10rem",
            },
            {
                "label": "Status",
                "type": "Select",
                "key": "status",
                "width": "8rem",
            },
            {
                "label": "Priority",
                "type": "Select",
                "key": "priority",
                "width": "8rem",
            },
            {
                "label": "Progress",
                "type": "Data",
                "key": "progress",
                "width": "12rem",
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
            "title",
            "project",
        ]
        return {"columns": columns, "rows": rows}

    @staticmethod
    def default_kanban_settings():
        return {
            "column_field": "status",
            "title_field": "title",
            "kanban_fields": '["project", "priority", "modified", "_assign"]',
        }
