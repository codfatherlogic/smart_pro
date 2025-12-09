"""
Permission configurations for Smart Pro doctypes
"""

import frappe

def get_permission_query_conditions(user):
    """
    Get permission query conditions based on user role
    """
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    
    conditions = {}
    
    # System Manager has full access
    if "System Manager" in user_roles:
        return conditions
    
    # HR Manager can see all projects and assignments
    if "HR Manager" in user_roles or "HR-Manager" in user_roles:
        return conditions
    
    # Project Manager can see their own projects
    if "Project Manager" in user_roles:
        conditions["Smart Project"] = f"`tabSmart Project`.`project_manager` = %s"
        conditions["Project Plan"] = f"`tabProject Plan`.`project` IN (SELECT `name` FROM `tabSmart Project` WHERE `project_manager` = %s)"
    
    # Employee can see assigned tasks and their own requests
    if "Employee" in user_roles:
        conditions["Smart Task"] = f"`tabSmart Task`.`assigned_to` = %s"
        conditions["Employee Date Request"] = f"`tabEmployee Date Request`.`employee` IN (SELECT `name` FROM `tabEmployee` WHERE `user_id` = %s)"
    
    return conditions

def has_permission(doc, perm_type, user=None):
    """
    Custom permission check for Smart Pro doctypes
    """
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    
    # System Manager always has access
    if "System Manager" in user_roles:
        return True
    
    # HR Manager always has access
    if "HR Manager" in user_roles or "HR-Manager" in user_roles:
        return True
    
    # Check doctype-specific permissions
    doctype = doc.doctype
    
    if doctype == "Smart Project":
        if perm_type == "read":
            return doc.project_manager == user or "Project Manager" in user_roles
        if perm_type == "write":
            return doc.project_manager == user
    
    elif doctype == "Smart Task":
        if perm_type == "read":
            return doc.assigned_to == user
        if perm_type == "write":
            return doc.assigned_to == user
    
    elif doctype == "Employee Project Assignment":
        if perm_type == "read":
            return "HR Manager" in user_roles or "HR-Manager" in user_roles
    
    elif doctype == "Employee Date Request":
        if perm_type == "read":
            # Employee can see their own requests
            employee = frappe.get_value("Employee", {"user_id": user}, "name")
            if employee and doc.employee == employee:
                return True
            # Approver can see requests assigned to them
            if doc.approver == user:
                return True
        if perm_type == "write":
            employee = frappe.get_value("Employee", {"user_id": user}, "name")
            if employee and doc.employee == employee and doc.status == "Draft":
                return True
    
    return False

# Role-based permissions configuration
ROLE_PERMISSIONS = {
    "System Manager": {
        "Smart Project": ["create", "read", "write", "delete", "submit", "cancel"],
        "Smart Task": ["create", "read", "write", "delete", "submit", "cancel"],
        "Project Plan": ["create", "read", "write", "delete", "submit", "cancel"],
        "Employee Project Assignment": ["create", "read", "write", "delete", "submit", "cancel"],
        "Employee Date Request": ["create", "read", "write", "delete", "submit", "cancel"],
    },
    "HR Manager": {
        "Smart Project": ["create", "read", "write", "delete", "submit", "cancel"],
        "Smart Task": ["read"],
        "Project Plan": ["create", "read", "write", "delete"],
        "Employee Project Assignment": ["create", "read", "write", "delete", "submit"],
        "Employee Date Request": ["read", "write"],
    },
    "Project Manager": {
        "Smart Project": ["create", "read", "write", "submit"],
        "Smart Task": ["create", "read", "write", "submit"],
        "Project Plan": ["create", "read", "write", "submit"],
        "Employee Project Assignment": ["read"],
        "Employee Date Request": ["read"],
    },
    "Employee": {
        "Smart Project": ["read"],
        "Smart Task": ["read", "write"],
        "Project Plan": ["read"],
        "Employee Project Assignment": ["read"],
        "Employee Date Request": ["create", "read", "write", "submit"],
    }
}