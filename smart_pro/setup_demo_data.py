"""
Smart Pro Demo Data Setup Script
================================
Creates comprehensive demo data for testing Smart Pro application.

Usage:
    cd /path/to/frappe-bench
    bench --site your-site execute smart_pro.setup_demo_data.setup_all_demo_data
"""

import frappe
from frappe.utils import nowdate, add_days, add_months
from datetime import datetime


def setup_all_demo_data():
    """Main function to setup all demo data"""
    print("=" * 60)
    print("Setting up Smart Pro Demo Data")
    print("=" * 60)

    # Create data in order of dependencies
    create_designations()
    create_departments()
    create_users_and_employees()
    create_smart_projects()
    create_smart_tasks()
    create_employee_project_assignments()
    create_employee_date_requests()
    setup_smart_pro_settings()

    frappe.db.commit()
    print("=" * 60)
    print("Demo data setup completed successfully!")
    print("=" * 60)


def create_designations():
    """Create demo designations"""
    print("\n[0/7] Creating Designations...")

    designations = [
        "Senior Developer",
        "Project Manager",
        "HR Manager",
        "Software Engineer",
        "Frontend Developer",
        "UI/UX Designer",
        "QA Engineer",
        "Marketing Manager",
        "Sales Executive",
        "Support Lead",
        "Backend Developer",
        "Security Analyst",
        "Training Coordinator"
    ]

    created = 0
    for designation in designations:
        if not frappe.db.exists("Designation", designation):
            doc = frappe.get_doc({
                "doctype": "Designation",
                "designation_name": designation
            })
            doc.insert(ignore_permissions=True)
            created += 1
            print(f"  Created: {designation}")
        else:
            print(f"  Exists: {designation}")

    print(f"  Total created: {created}")


def create_departments():
    """Create demo departments"""
    print("\n[1/7] Creating Departments...")

    departments = [
        {"department_name": "Engineering", "company": get_default_company()},
        {"department_name": "Human Resources", "company": get_default_company()},
        {"department_name": "Marketing", "company": get_default_company()},
        {"department_name": "Sales", "company": get_default_company()},
        {"department_name": "Finance", "company": get_default_company()},
        {"department_name": "Operations", "company": get_default_company()},
        {"department_name": "Product", "company": get_default_company()},
        {"department_name": "Design", "company": get_default_company()},
        {"department_name": "Quality Assurance", "company": get_default_company()},
        {"department_name": "Customer Support", "company": get_default_company()},
    ]

    created = 0
    for dept in departments:
        dept_name = f"{dept['department_name']} - {dept['company']}"
        if not frappe.db.exists("Department", dept_name):
            doc = frappe.get_doc({
                "doctype": "Department",
                "department_name": dept["department_name"],
                "company": dept["company"],
                "is_group": 0
            })
            doc.insert(ignore_permissions=True)
            created += 1
            print(f"  Created: {dept['department_name']}")
        else:
            print(f"  Exists: {dept['department_name']}")

    print(f"  Total created: {created}")


def create_users_and_employees():
    """Create demo users and employees"""
    print("\n[2/7] Creating Users and Employees...")

    users_data = [
        {
            "email": "john.smith@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "roles": ["System Manager", "Employee"],
            "department": "Engineering",
            "designation": "Senior Developer"
        },
        {
            "email": "sarah.johnson@example.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "roles": ["Projects Manager", "Employee"],
            "department": "Product",
            "designation": "Project Manager"
        },
        {
            "email": "mike.williams@example.com",
            "first_name": "Mike",
            "last_name": "Williams",
            "roles": ["HR Manager", "Employee"],
            "department": "Human Resources",
            "designation": "HR Manager"
        },
        {
            "email": "emily.brown@example.com",
            "first_name": "Emily",
            "last_name": "Brown",
            "roles": ["Employee"],
            "department": "Engineering",
            "designation": "Software Engineer"
        },
        {
            "email": "david.jones@example.com",
            "first_name": "David",
            "last_name": "Jones",
            "roles": ["Employee"],
            "department": "Engineering",
            "designation": "Frontend Developer"
        },
        {
            "email": "lisa.davis@example.com",
            "first_name": "Lisa",
            "last_name": "Davis",
            "roles": ["Employee"],
            "department": "Design",
            "designation": "UI/UX Designer"
        },
        {
            "email": "james.wilson@example.com",
            "first_name": "James",
            "last_name": "Wilson",
            "roles": ["Employee"],
            "department": "Quality Assurance",
            "designation": "QA Engineer"
        },
        {
            "email": "anna.martinez@example.com",
            "first_name": "Anna",
            "last_name": "Martinez",
            "roles": ["Projects Manager", "Employee"],
            "department": "Marketing",
            "designation": "Marketing Manager"
        },
        {
            "email": "robert.taylor@example.com",
            "first_name": "Robert",
            "last_name": "Taylor",
            "roles": ["Employee"],
            "department": "Sales",
            "designation": "Sales Executive"
        },
        {
            "email": "jennifer.anderson@example.com",
            "first_name": "Jennifer",
            "last_name": "Anderson",
            "roles": ["Employee"],
            "department": "Customer Support",
            "designation": "Support Lead"
        },
    ]

    company = get_default_company()

    for user_data in users_data:
        # Create User
        if not frappe.db.exists("User", user_data["email"]):
            user = frappe.get_doc({
                "doctype": "User",
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "enabled": 1,
                "send_welcome_email": 0,
                "new_password": "Demo@123"
            })
            user.insert(ignore_permissions=True)

            # Add roles
            for role in user_data["roles"]:
                user.add_roles(role)

            print(f"  Created User: {user_data['email']}")
        else:
            print(f"  User Exists: {user_data['email']}")

        # Create Employee
        employee_name = f"{user_data['first_name']} {user_data['last_name']}"
        if not frappe.db.exists("Employee", {"user_id": user_data["email"]}):
            dept_name = f"{user_data['department']} - {company}"
            employee = frappe.get_doc({
                "doctype": "Employee",
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "employee_name": employee_name,
                "user_id": user_data["email"],
                "company": company,
                "department": dept_name if frappe.db.exists("Department", dept_name) else None,
                "designation": user_data["designation"],
                "gender": "Male" if user_data["first_name"] in ["John", "Mike", "David", "James", "Robert"] else "Female",
                "date_of_birth": "1990-01-15",
                "date_of_joining": "2023-01-01",
                "status": "Active"
            })
            employee.insert(ignore_permissions=True)
            print(f"  Created Employee: {employee_name}")
        else:
            print(f"  Employee Exists: {employee_name}")


def create_smart_projects():
    """Create 10 demo Smart Projects"""
    print("\n[3/7] Creating Smart Projects...")

    today = nowdate()

    # Use existing departments if available
    departments = frappe.get_all("Department", filters={"is_group": 0}, pluck="name", limit=10)
    dept_map = {
        "engineering": departments[0] if len(departments) > 0 else None,
        "hr": departments[1] if len(departments) > 1 else None,
        "marketing": departments[2] if len(departments) > 2 else None,
        "sales": departments[3] if len(departments) > 3 else None,
        "operations": departments[4] if len(departments) > 4 else None,
    }

    projects = [
        {
            "title": "E-Commerce Platform Redesign",
            "description": "Complete redesign of the e-commerce platform with modern UI/UX",
            "status": "Active",
            "project_manager": "sarah.johnson@example.com",
            "department": dept_map.get("engineering"),
            "start_date": today,
            "end_date": add_months(today, 3),
            "budget_amount": 50000
        },
        {
            "title": "Mobile App Development",
            "description": "Develop iOS and Android mobile applications for customers",
            "status": "Active",
            "project_manager": "sarah.johnson@example.com",
            "department": dept_map.get("engineering"),
            "start_date": today,
            "end_date": add_months(today, 6),
            "budget_amount": 80000
        },
        {
            "title": "HR Portal Implementation",
            "description": "Implement new HR portal for employee self-service",
            "status": "Planning",
            "project_manager": "mike.williams@example.com",
            "department": dept_map.get("hr"),
            "start_date": add_days(today, 30),
            "end_date": add_months(today, 4),
            "budget_amount": 30000
        },
        {
            "title": "Marketing Campaign Q1",
            "description": "Digital marketing campaign for Q1 product launch",
            "status": "Active",
            "project_manager": "anna.martinez@example.com",
            "department": dept_map.get("marketing"),
            "start_date": today,
            "end_date": add_months(today, 2),
            "budget_amount": 25000
        },
        {
            "title": "Customer Support Automation",
            "description": "Implement AI chatbot and automation for customer support",
            "status": "Planning",
            "project_manager": "sarah.johnson@example.com",
            "department": dept_map.get("operations"),
            "start_date": add_days(today, 15),
            "end_date": add_months(today, 3),
            "budget_amount": 40000
        },
        {
            "title": "Data Analytics Dashboard",
            "description": "Build comprehensive analytics dashboard for business insights",
            "status": "Active",
            "project_manager": "john.smith@example.com",
            "department": dept_map.get("engineering"),
            "start_date": add_days(today, -30),
            "end_date": add_months(today, 2),
            "budget_amount": 35000
        },
        {
            "title": "Security Audit & Compliance",
            "description": "Annual security audit and compliance certification",
            "status": "Active",
            "project_manager": "john.smith@example.com",
            "department": dept_map.get("engineering"),
            "start_date": today,
            "end_date": add_months(today, 1),
            "budget_amount": 20000
        },
        {
            "title": "Brand Identity Refresh",
            "description": "Update brand guidelines, logo, and marketing materials",
            "status": "Planning",
            "project_manager": "anna.martinez@example.com",
            "department": dept_map.get("marketing"),
            "start_date": add_days(today, 45),
            "end_date": add_months(today, 3),
            "budget_amount": 15000
        },
        {
            "title": "Sales CRM Integration",
            "description": "Integrate new CRM system with existing sales tools",
            "status": "On Hold",
            "project_manager": "sarah.johnson@example.com",
            "department": dept_map.get("sales"),
            "start_date": add_days(today, -15),
            "end_date": add_months(today, 2),
            "budget_amount": 45000
        },
        {
            "title": "Employee Training Program",
            "description": "Develop and implement comprehensive employee training program",
            "status": "Active",
            "project_manager": "mike.williams@example.com",
            "department": dept_map.get("hr"),
            "start_date": today,
            "end_date": add_months(today, 4),
            "budget_amount": 18000
        },
    ]

    created = 0
    for project in projects:
        if not frappe.db.exists("Smart Project", {"title": project["title"]}):
            doc = frappe.get_doc({
                "doctype": "Smart Project",
                **project
            })
            doc.insert(ignore_permissions=True)
            created += 1
            print(f"  Created: {project['title']}")
        else:
            print(f"  Exists: {project['title']}")

    print(f"  Total created: {created}")


def create_smart_tasks():
    """Create 10 demo Smart Tasks"""
    print("\n[4/7] Creating Smart Tasks...")

    today = nowdate()

    # Get project names
    projects = frappe.get_all("Smart Project", pluck="name", limit=10)

    tasks = [
        {
            "title": "Design Homepage Mockups",
            "description": "Create wireframes and high-fidelity mockups for the new homepage",
            "project": projects[0] if len(projects) > 0 else None,
            "assigned_to": "lisa.davis@example.com",
            "status": "Working",
            "priority": "High",
            "start_date": today,
            "due_date": add_days(today, 7),
            "progress": 60
        },
        {
            "title": "Implement User Authentication",
            "description": "Build secure login/signup system with OAuth support",
            "project": projects[0] if len(projects) > 0 else None,
            "assigned_to": "emily.brown@example.com",
            "status": "Open",
            "priority": "Critical",
            "start_date": today,
            "due_date": add_days(today, 14),
            "progress": 0
        },
        {
            "title": "Setup CI/CD Pipeline",
            "description": "Configure automated testing and deployment pipeline",
            "project": projects[1] if len(projects) > 1 else None,
            "assigned_to": "john.smith@example.com",
            "status": "Completed",
            "priority": "High",
            "start_date": add_days(today, -10),
            "due_date": add_days(today, -3),
            "progress": 100
        },
        {
            "title": "Write API Documentation",
            "description": "Document all REST API endpoints with examples",
            "project": projects[1] if len(projects) > 1 else None,
            "assigned_to": "david.jones@example.com",
            "status": "Working",
            "priority": "Medium",
            "start_date": today,
            "due_date": add_days(today, 10),
            "progress": 30
        },
        {
            "title": "Create Test Cases",
            "description": "Write comprehensive unit and integration test cases",
            "project": projects[0] if len(projects) > 0 else None,
            "assigned_to": "james.wilson@example.com",
            "status": "Open",
            "priority": "Medium",
            "start_date": add_days(today, 5),
            "due_date": add_days(today, 15),
            "progress": 0
        },
        {
            "title": "Social Media Content Calendar",
            "description": "Plan and create content calendar for Q1",
            "project": projects[3] if len(projects) > 3 else None,
            "assigned_to": "anna.martinez@example.com",
            "status": "Working",
            "priority": "High",
            "start_date": today,
            "due_date": add_days(today, 5),
            "progress": 80
        },
        {
            "title": "Database Optimization",
            "description": "Optimize database queries and indexes for performance",
            "project": projects[5] if len(projects) > 5 else None,
            "assigned_to": "emily.brown@example.com",
            "status": "Open",
            "priority": "High",
            "start_date": add_days(today, 2),
            "due_date": add_days(today, 12),
            "progress": 0
        },
        {
            "title": "Security Vulnerability Assessment",
            "description": "Conduct penetration testing and vulnerability scan",
            "project": projects[6] if len(projects) > 6 else None,
            "assigned_to": "john.smith@example.com",
            "status": "Working",
            "priority": "Critical",
            "start_date": today,
            "due_date": add_days(today, 7),
            "progress": 45
        },
        {
            "title": "Employee Onboarding Guide",
            "description": "Create comprehensive onboarding documentation",
            "project": projects[9] if len(projects) > 9 else None,
            "assigned_to": "mike.williams@example.com",
            "status": "Open",
            "priority": "Medium",
            "start_date": add_days(today, 3),
            "due_date": add_days(today, 20),
            "progress": 0
        },
        {
            "title": "Customer Feedback Analysis",
            "description": "Analyze customer feedback and create improvement report",
            "project": projects[4] if len(projects) > 4 else None,
            "assigned_to": "jennifer.anderson@example.com",
            "status": "Working",
            "priority": "Medium",
            "start_date": add_days(today, -5),
            "due_date": add_days(today, 5),
            "progress": 50
        },
    ]

    created = 0
    for task in tasks:
        if task["project"] and not frappe.db.exists("Smart Task", {"title": task["title"]}):
            doc = frappe.get_doc({
                "doctype": "Smart Task",
                **task
            })
            doc.insert(ignore_permissions=True)
            created += 1
            print(f"  Created: {task['title']}")
        elif not task["project"]:
            print(f"  Skipped (no project): {task['title']}")
        else:
            print(f"  Exists: {task['title']}")

    print(f"  Total created: {created}")


def create_employee_project_assignments():
    """Create demo Employee Project Assignments"""
    print("\n[5/7] Creating Employee Project Assignments...")

    today = nowdate()
    projects = frappe.get_all("Smart Project", pluck="name", limit=10)

    # Get employees
    employees = frappe.get_all("Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name"],
        limit=10
    )

    assignments = [
        {"employee_idx": 0, "project_idx": 0, "role": "Lead Developer", "allocation": 80},
        {"employee_idx": 1, "project_idx": 0, "role": "Project Lead", "allocation": 100},
        {"employee_idx": 2, "project_idx": 1, "role": "UI/UX Designer", "allocation": 60},
        {"employee_idx": 3, "project_idx": 1, "role": "Frontend Developer", "allocation": 100},
        {"employee_idx": 4, "project_idx": 2, "role": "QA Engineer", "allocation": 50},
        {"employee_idx": 5, "project_idx": 3, "role": "Marketing Lead", "allocation": 100},
        {"employee_idx": 6, "project_idx": 4, "role": "Support Lead", "allocation": 80},
        {"employee_idx": 7, "project_idx": 5, "role": "Backend Developer", "allocation": 70},
        {"employee_idx": 8, "project_idx": 6, "role": "Security Analyst", "allocation": 100},
        {"employee_idx": 9, "project_idx": 9, "role": "Training Coordinator", "allocation": 60},
    ]

    created = 0
    for assignment in assignments:
        if (len(employees) > assignment["employee_idx"] and
            len(projects) > assignment["project_idx"]):

            employee = employees[assignment["employee_idx"]]
            project = projects[assignment["project_idx"]]

            if not frappe.db.exists("Employee Project Assignment",
                {"employee": employee["name"], "project": project}):

                doc = frappe.get_doc({
                    "doctype": "Employee Project Assignment",
                    "employee": employee["name"],
                    "project": project,
                    "role": assignment["role"],
                    "allocation_percentage": assignment["allocation"],
                    "status": "Active",
                    "start_date": today
                })
                doc.insert(ignore_permissions=True)
                created += 1
                print(f"  Created: {employee['employee_name']} -> {project}")
            else:
                print(f"  Exists: {employee['employee_name']} -> {project}")

    print(f"  Total created: {created}")


def create_employee_date_requests():
    """Create demo Employee Date Requests"""
    print("\n[6/7] Creating Employee Date Requests...")

    today = nowdate()

    # Get employees and their approvers
    employees = frappe.get_all("Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "user_id"],
        limit=10
    )

    # Mike Williams (HR Manager) will be the approver
    approver = "mike.williams@example.com"

    requests = [
        {
            "employee_idx": 3,
            "request_type": "Leave",
            "from_date": add_days(today, 10),
            "to_date": add_days(today, 12),
            "reason": "Family vacation - planned trip",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 4,
            "request_type": "Work From Home",
            "from_date": add_days(today, 5),
            "to_date": add_days(today, 5),
            "reason": "Home repair work scheduled",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 5,
            "request_type": "Leave",
            "from_date": add_days(today, 20),
            "to_date": add_days(today, 25),
            "reason": "Personal travel",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 6,
            "request_type": "Time Off",
            "from_date": add_days(today, 3),
            "to_date": add_days(today, 3),
            "reason": "Doctor appointment",
            "status": "Approved"
        },
        {
            "employee_idx": 7,
            "request_type": "Overtime",
            "from_date": add_days(today, -2),
            "to_date": add_days(today, -2),
            "reason": "Project deadline - extra hours needed",
            "status": "Approved"
        },
        {
            "employee_idx": 8,
            "request_type": "Leave",
            "from_date": add_days(today, 15),
            "to_date": add_days(today, 16),
            "reason": "Wedding anniversary celebration",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 9,
            "request_type": "Work From Home",
            "from_date": add_days(today, 7),
            "to_date": add_days(today, 8),
            "reason": "Child care - school closure",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 0,
            "request_type": "Leave",
            "from_date": add_days(today, -10),
            "to_date": add_days(today, -8),
            "reason": "Sick leave - flu",
            "status": "Approved"
        },
        {
            "employee_idx": 1,
            "request_type": "Time Off",
            "from_date": add_days(today, 30),
            "to_date": add_days(today, 30),
            "reason": "Personal errand",
            "status": "Pending Approval"
        },
        {
            "employee_idx": 3,
            "request_type": "Work From Home",
            "from_date": add_days(today, 1),
            "to_date": add_days(today, 2),
            "reason": "Internet installation at home",
            "status": "Rejected"
        },
    ]

    created = 0
    for req in requests:
        if len(employees) > req["employee_idx"]:
            employee = employees[req["employee_idx"]]

            # Check if similar request exists
            existing = frappe.db.exists("Employee Date Request", {
                "employee": employee["name"],
                "from_date": req["from_date"],
                "request_type": req["request_type"]
            })

            if not existing:
                doc = frappe.get_doc({
                    "doctype": "Employee Date Request",
                    "employee": employee["name"],
                    "request_type": req["request_type"],
                    "from_date": req["from_date"],
                    "to_date": req["to_date"],
                    "reason": req["reason"],
                    "approver": approver,
                    "status": req["status"]
                })
                doc.insert(ignore_permissions=True)
                created += 1
                print(f"  Created: {employee['employee_name']} - {req['request_type']} ({req['status']})")
            else:
                print(f"  Exists: {employee['employee_name']} - {req['request_type']}")

    print(f"  Total created: {created}")


def setup_smart_pro_settings():
    """Configure Smart Pro Settings"""
    print("\n[7/7] Configuring Smart Pro Settings...")

    try:
        settings = frappe.get_single("Smart Pro Settings")

        # Set default values
        settings.enable_notifications = 1
        settings.enable_offline_mode = 1
        settings.default_project_status = "Planning"
        settings.default_task_priority = "Medium"
        settings.roles_with_full_access = "System Manager\nHR Manager"

        # Add Administrator to full access users
        if not any(row.user == "Administrator" for row in settings.users_with_full_access):
            settings.append("users_with_full_access", {
                "user": "Administrator",
                "can_view_all_projects": 1,
                "can_view_all_tasks": 1
            })

        # Add john.smith (System Manager) to full access
        if frappe.db.exists("User", "john.smith@example.com"):
            if not any(row.user == "john.smith@example.com" for row in settings.users_with_full_access):
                settings.append("users_with_full_access", {
                    "user": "john.smith@example.com",
                    "can_view_all_projects": 1,
                    "can_view_all_tasks": 1
                })

        settings.save(ignore_permissions=True)
        print("  Smart Pro Settings configured successfully")
        print("  - Notifications: Enabled")
        print("  - Offline Mode: Enabled")
        print("  - Full Access Roles: System Manager, HR Manager")
        print("  - Full Access Users: Administrator, john.smith@example.com")

    except Exception as e:
        print(f"  Error configuring settings: {str(e)}")


def get_default_company():
    """Get the default company"""
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        company = frappe.get_all("Company", limit=1, pluck="name")
        company = company[0] if company else None
    return company


# Allow running directly
if __name__ == "__main__":
    setup_all_demo_data()
