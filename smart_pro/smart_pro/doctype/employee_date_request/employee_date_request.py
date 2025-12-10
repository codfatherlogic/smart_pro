# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_days, getdate


class EmployeeDateRequest(Document):
    def validate(self):
        self.validate_dates()
        self.fetch_employee_name()
        self.calculate_total_days()
        self.link_assignment()
        self.set_default_approver()

    def validate_dates(self):
        if self.from_date and self.to_date and getdate(self.from_date) > getdate(self.to_date):
            frappe.throw("From Date cannot be after To Date")

    def fetch_employee_name(self):
        if self.employee and not self.employee_name:
            self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")

    def calculate_total_days(self):
        """Calculate total days between from_date and to_date"""
        if self.from_date and self.to_date:
            self.total_days = date_diff(self.to_date, self.from_date) + 1

    def link_assignment(self):
        """Link to Employee Project Assignment if project is selected and fetch project scope"""
        if self.request_type == "Project Date Update" and self.project and self.employee and not self.assignment:
            assignment = frappe.db.get_value(
                "Employee Project Assignment",
                {"employee": self.employee, "project": self.project, "status": "Active"},
                ["name", "project_scope"],
                as_dict=True
            )
            if assignment:
                self.assignment = assignment.name
                # Fetch project scope from assignment if not already set
                if assignment.project_scope and not self.project_scope:
                    self.project_scope = assignment.project_scope

        # Also fetch project_scope if assignment is already set but scope is empty
        if self.assignment and not self.project_scope:
            scope = frappe.db.get_value("Employee Project Assignment", self.assignment, "project_scope")
            if scope:
                self.project_scope = scope

    def set_default_approver(self):
        """Set default approver from Employee Project Assignment, fallback to project manager"""
        if not self.approver and self.project and self.employee:
            # Get the user_id of the employee making the request
            employee_user = frappe.db.get_value("Employee", self.employee, "user_id")

            # First, try to get approver from the Employee Project Assignment
            assignment_approver = None
            if self.assignment:
                assignment_approver = frappe.db.get_value("Employee Project Assignment", self.assignment, "approver")
            else:
                # Try to find the assignment if not already linked
                assignment_data = frappe.db.get_value(
                    "Employee Project Assignment",
                    {"employee": self.employee, "project": self.project, "status": "Active"},
                    ["name", "approver"],
                    as_dict=True
                )
                if assignment_data:
                    assignment_approver = assignment_data.get("approver")

            if assignment_approver and assignment_approver != employee_user:
                # Use the approver from the assignment
                self.approver = assignment_approver
            else:
                # Fallback to project manager
                project_manager = frappe.db.get_value("Smart Project", self.project, "project_manager")

                # If the employee is NOT the project manager, set project manager as approver
                if project_manager and project_manager != employee_user:
                    self.approver = project_manager
                # If the employee IS the project manager, they can self-approve (no approver needed)

    def on_submit(self):
        if self.status == "Draft":
            self.db_set("status", "Pending Approval")

    def after_insert(self):
        """Send notification to approver when request is created"""
        self.send_request_notification()

    def on_update(self):
        """Handle status changes"""
        if self.has_value_changed("status"):
            if self.status == "Approved":
                self.on_approval()
                self.send_status_notification("approved")
            elif self.status == "Rejected":
                self.on_rejection()
                self.send_status_notification("rejected")

    def send_request_notification(self):
        """Send notification to approver for new request"""
        from smart_pro.smart_pro.notifications import PushNotificationManager
        try:
            PushNotificationManager.send_date_request_notification(self)
        except Exception as e:
            frappe.log_error(str(e), "Date Request Notification Error")

    def send_status_notification(self, status):
        """Send notification to employee when request status changes"""
        try:
            if self.employee:
                user_id = frappe.db.get_value("Employee", self.employee, "user_id")
                if user_id:
                    from smart_pro.smart_pro.notifications import PushNotificationManager
                    title = f"Date Request {status.title()}"
                    body = f"Your {self.request_type} request ({self.from_date} to {self.to_date}) has been {status}"
                    PushNotificationManager._send_notification(
                        user_id,
                        title,
                        body,
                        {
                            "type": f"date_request_{status}",
                            "doctype": "Employee Date Request",
                            "name": self.name
                        }
                    )
        except Exception as e:
            frappe.log_error(str(e), "Date Request Status Notification Error")

    def on_approval(self):
        """Actions when request is approved"""
        if self.request_type == "Project Date Update" and self.project:
            # Update project dates
            self.update_project_dates()

            # Update assignment dates
            if self.assignment:
                self.update_assignment_dates()

            # Auto-create tasks if enabled
            if self.auto_create_tasks:
                self.create_project_tasks()

            frappe.msgprint(f"Project dates updated and tasks created for {self.project_title or self.project}")

    def on_rejection(self):
        """Actions when request is rejected"""
        # Send notification to employee
        pass

    def update_project_dates(self):
        """Update project start and end dates"""
        if self.project and self.from_date and self.to_date:
            frappe.db.set_value("Smart Project", self.project, {
                "start_date": self.from_date,
                "end_date": self.to_date,
                "status": "Active"
            })

    def update_assignment_dates(self):
        """Update assignment dates"""
        if self.assignment and self.from_date and self.to_date:
            frappe.db.set_value("Employee Project Assignment", self.assignment, {
                "start_date": self.from_date,
                "end_date": self.to_date
            })

    def create_project_tasks(self):
        """Auto-create a single task for the project"""
        if not self.project or not self.employee:
            return

        # Get employee's user_id
        user_id = frappe.db.get_value("Employee", self.employee, "user_id")
        if not user_id:
            frappe.msgprint("Employee does not have a linked user. Task will be created without assignment.")

        project_title = self.project_title or frappe.db.get_value("Smart Project", self.project, "title")

        # Check if task already exists for this project
        existing_task = frappe.db.exists("Smart Task", {
            "project": self.project,
            "title": project_title
        })

        if not existing_task:
            task = frappe.get_doc({
                "doctype": "Smart Task",
                "title": project_title,
                "project": self.project,
                "assigned_to": user_id,
                "status": "Open",
                "priority": "Medium",
                "start_date": self.from_date,
                "due_date": self.to_date,
                "progress": 0,
                "description": f"Task for {project_title}",
                "project_scope": self.project_scope
            })
            task.insert(ignore_permissions=True)
            frappe.msgprint(f"Created task: {task.title}")
