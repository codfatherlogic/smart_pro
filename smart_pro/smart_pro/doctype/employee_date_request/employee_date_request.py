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
        """Set default approver as project manager"""
        if not self.approver and self.project:
            project_manager = frappe.db.get_value("Smart Project", self.project, "project_manager")
            if project_manager:
                self.approver = project_manager

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
        """Auto-create tasks for the project based on duration"""
        if not self.project or not self.employee:
            return

        # Get employee's user_id
        user_id = frappe.db.get_value("Employee", self.employee, "user_id")
        if not user_id:
            frappe.msgprint("Employee does not have a linked user. Tasks will be created without assignment.")

        total_days = self.total_days or 1
        project_title = self.project_title or frappe.db.get_value("Smart Project", self.project, "title")

        # Create default tasks based on project duration
        tasks_to_create = []

        if total_days <= 7:
            # Short project - create 2-3 tasks
            tasks_to_create = [
                {"title": f"{project_title} - Planning & Setup", "days_offset": 0, "days_duration": max(1, total_days // 3)},
                {"title": f"{project_title} - Implementation", "days_offset": max(1, total_days // 3), "days_duration": max(1, total_days // 2)},
                {"title": f"{project_title} - Review & Completion", "days_offset": max(2, total_days - 2), "days_duration": min(2, total_days)}
            ]
        elif total_days <= 30:
            # Medium project - create 4-5 tasks
            week_duration = 7
            tasks_to_create = [
                {"title": f"{project_title} - Week 1: Planning", "days_offset": 0, "days_duration": week_duration},
                {"title": f"{project_title} - Week 2: Development", "days_offset": 7, "days_duration": week_duration},
                {"title": f"{project_title} - Week 3: Testing", "days_offset": 14, "days_duration": week_duration},
                {"title": f"{project_title} - Week 4: Deployment", "days_offset": 21, "days_duration": min(week_duration, total_days - 21)}
            ]
        else:
            # Long project - create monthly tasks
            months = (total_days // 30) + 1
            for i in range(min(months, 6)):  # Max 6 tasks
                tasks_to_create.append({
                    "title": f"{project_title} - Phase {i + 1}",
                    "days_offset": i * 30,
                    "days_duration": min(30, total_days - (i * 30))
                })

        # Create the tasks
        for task_data in tasks_to_create:
            start_date = add_days(self.from_date, task_data["days_offset"])
            due_date = add_days(start_date, task_data["days_duration"] - 1)

            # Don't create task if start date is beyond project end
            if getdate(start_date) > getdate(self.to_date):
                continue

            # Ensure due date doesn't exceed project end date
            if getdate(due_date) > getdate(self.to_date):
                due_date = self.to_date

            # Check if similar task already exists
            existing_task = frappe.db.exists("Smart Task", {
                "project": self.project,
                "title": task_data["title"]
            })

            if not existing_task:
                task = frappe.get_doc({
                    "doctype": "Smart Task",
                    "title": task_data["title"],
                    "project": self.project,
                    "assigned_to": user_id,
                    "status": "Open",
                    "priority": "Medium",
                    "start_date": start_date,
                    "due_date": due_date,
                    "progress": 0,
                    "description": f"Auto-created task for {project_title}",
                    "project_scope": self.project_scope  # Forward project scope to task
                })
                task.insert(ignore_permissions=True)
                frappe.msgprint(f"Created task: {task.title}")
