#!/usr/bin/env python
"""Script to check and populate sample data for testing"""

import frappe
import sys

def check_data():
    """Check if there's data in the database"""
    
    # Count records
    project_count = frappe.db.count("Smart Project")
    task_count = frappe.db.count("Smart Task")
    request_count = frappe.db.count("Employee Date Request")
    
    print(f"\n=== Database Status ===")
    print(f"Smart Projects: {project_count}")
    print(f"Smart Tasks: {task_count}")
    print(f"Employee Date Requests: {request_count}")
    
    if project_count == 0 and task_count == 0 and request_count == 0:
        print("\n⚠️  No data found in database!")
        print("The dashboard will be empty because there are no projects, tasks, or requests.")
        return False
    
    return True

def get_user_data():
    """Get data for the current user"""
    user = frappe.session.user
    print(f"\n=== Data for User: {user} ===")
    
    user_projects = frappe.db.count("Smart Project", {"project_manager": user})
    user_tasks = frappe.db.count("Smart Task", {"assigned_to": user})
    user_requests = frappe.db.count("Employee Date Request", {"approver": user, "status": "Pending Approval"})
    
    print(f"Projects managed: {user_projects}")
    print(f"Tasks assigned: {user_tasks}")
    print(f"Pending approval requests: {user_requests}")
    
    if user_projects == 0 and user_tasks == 0 and user_requests == 0:
        print(f"\n⚠️  No data assigned to user {user}")
        print("The dashboard will be empty for this user.")
        return False
    
    return True

if __name__ == "__main__":
    try:
        frappe.init(user="Administrator")
        frappe.connect()
        
        check_data()
        get_user_data()
        
        frappe.close()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)