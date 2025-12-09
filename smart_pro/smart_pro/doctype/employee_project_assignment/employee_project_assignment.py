import frappe
from frappe.model.document import Document

class EmployeeProjectAssignment(Document):
    def before_insert(self):
        # Set default status if not provided
        if not self.status:
            self.status = "Active"

    def validate(self):
        self.validate_dates()
        self.fetch_employee_name()
        self.validate_allocation()

    def after_insert(self):
        """Auto-create Employee Date Request after assignment is created"""
        self.create_date_request()

    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("Start Date cannot be after End Date")

    def fetch_employee_name(self):
        if self.employee:
            employee_doc = frappe.get_doc("Employee", self.employee)
            self.employee_name = employee_doc.employee_name

    def validate_allocation(self):
        if self.allocation_percentage:
            try:
                allocation = float(self.allocation_percentage)
                if allocation < 0 or allocation > 100:
                    frappe.throw("Allocation Percentage must be between 0 and 100")
            except (ValueError, TypeError):
                frappe.throw("Allocation Percentage must be a valid number")

    def create_date_request(self):
        """Auto-create Employee Date Request for project assignment"""
        if not self.employee or not self.project or not self.start_date:
            return

        # Get project title
        project_title = frappe.db.get_value("Smart Project", self.project, "title") or self.project

        # Create the date request
        date_request = frappe.get_doc({
            "doctype": "Employee Date Request",
            "employee": self.employee,
            "request_type": "Project Date Update",
            "project": self.project,
            "assignment": self.name,
            "from_date": self.start_date,
            "to_date": self.end_date or self.start_date,
            "reason": f"Assigned to project: {project_title}\nRole: {self.role or 'Team Member'}\nAllocation: {self.allocation_percentage or 100}%",
            "status": "Pending Approval",
            "auto_create_tasks": 1
        })

        try:
            date_request.insert(ignore_permissions=True)
            frappe.msgprint(
                f"Date Request created for approval: {date_request.name}",
                indicator="blue",
                alert=True
            )
        except Exception as e:
            frappe.log_error(f"Failed to create date request: {str(e)}", "Employee Project Assignment")
            frappe.msgprint(
                f"Note: Date request could not be auto-created. Please create manually.",
                indicator="orange"
            )