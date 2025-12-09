#!/usr/bin/env python
"""Create sample data for testing the dashboard"""

import frappe
import random
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample projects, tasks, and requests"""
    
    # Set sample user for testing
    user = "test@example.com"  # Change to an existing user email or relevant test user
    
    print(f"Creating sample data for user: {user}")
    
    # Create sample projects
    projects = []
    for i in range(3):
        project = frappe.get_doc({
            "doctype": "Smart Project",
            "title": f"Sample Project {i+1}",
            "project_manager": user,
            "status": random.choice(["Active", "Planning", "On Hold"]),
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=30)).date(),
            "budget_amount": random.randint(10000, 50000),
            "currency": "USD"
        })
        project.insert()
        projects.append(project)
        print(f"Created project: {project.title}")
    
    # Create sample tasks
    for i in range(5):
        task = frappe.get_doc({
            "doctype": "Smart Task",
            "title": f"Sample Task {i+1}",
            "project": random.choice(projects).name,
            "assigned_to": user,
            "status": random.choice(["Open", "Working", "Pending Review"]),
            "priority": random.choice(["High", "Medium", "Low"]),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).date(),
            "progress": random.randint(0, 100)
        })
        task.insert()
        print(f"Created task: {task.title}")
    
    # Create sample employee date requests
    for i in range(2):
        request = frappe.get_doc({
            "doctype": "Employee Date Request",
            "employee": "HR-EMP-00001",  # Sample employee
            "employee_name": "John Doe",
            "approver": user,
            "request_type": random.choice(["Leave", "Work From Home", "Training"]),
            "from_date": datetime.now().date(),
            "to_date": (datetime.now() + timedelta(days=random.randint(1, 5))).date(),
            "reason": f"Sample reason {i+1}",
            "status": "Pending Approval"
        })
        request.insert()
        print(f"Created request: {request.request_type}")
    
    print("\n✅ Sample data created successfully!")
    print(f"Projects: {len(projects)}")
    print(f"Tasks: 5")
    print(f"Requests: 2")

if __name__ == "__main__":
    try:
        frappe.init(user="Administrator")
        frappe.connect()
        
        create_sample_data()
        
        frappe.close()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()