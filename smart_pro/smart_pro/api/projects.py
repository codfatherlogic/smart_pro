import frappe
from frappe.utils import now_datetime
from smart_pro.smart_pro.doctype.smart_pro_settings.smart_pro_settings import user_has_full_access, user_can_view_all_tasks

@frappe.whitelist()
def get_user_projects(include_completed=False):
    """Get only projects assigned to the current user via Employee Project Assignment

    Args:
        include_completed: If False (default), exclude completed projects for better performance
    """
    user = frappe.session.user
    # Convert string "true"/"false" to boolean
    if isinstance(include_completed, str):
        include_completed = include_completed.lower() == "true"

    try:
        # Base filter to exclude completed projects (unless explicitly requested)
        base_filters = {}
        if not include_completed:
            base_filters["status"] = ["!=", "Completed"]

        # Check if user has full access via Smart Pro Settings
        if user_has_full_access(user):
            # Return all non-completed projects
            projects = frappe.get_list(
                "Smart Project",
                filters=base_filters,
                fields=["name", "title", "status", "start_date", "end_date", "budget_amount", "project_manager"],
                order_by="modified desc"
            )
            frappe.logger().info(f"get_user_projects: User {user} has full access, returning {len(projects)} projects (completed excluded: {not include_completed})")
        else:
            # Get employee record for current user
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

            if not employee:
                frappe.logger().info(f"get_user_projects: User {user} has no employee record")
                return []

            # ONLY get projects where employee is assigned via Employee Project Assignment
            assignments = frappe.get_list(
                "Employee Project Assignment",
                filters={
                    "employee": employee,
                    "status": "Active"
                },
                pluck="project"
            )

            if not assignments:
                frappe.logger().info(f"get_user_projects: Employee {employee} has no active assignments")
                return []

            # Combine filters
            project_filters = {"name": ["in", assignments]}
            if not include_completed:
                project_filters["status"] = ["!=", "Completed"]

            projects = frappe.get_list(
                "Smart Project",
                filters=project_filters,
                fields=["name", "title", "status", "start_date", "end_date", "budget_amount", "project_manager"],
                order_by="modified desc"
            )

            frappe.logger().info(f"get_user_projects: Found {len(projects)} assigned projects for employee {employee} (completed excluded: {not include_completed})")
        return projects
    except Exception as e:
        frappe.logger().error(f"Error getting user projects: {str(e)}")
        frappe.throw(f"Error loading projects: {str(e)}")

@frappe.whitelist()
def get_user_tasks(include_from_completed_projects=False):
    """Get only tasks from projects assigned to the current user via Employee Project Assignment

    Args:
        include_from_completed_projects: If False (default), exclude tasks from completed projects for better performance
    """
    user = frappe.session.user
    # Convert string "true"/"false" to boolean
    if isinstance(include_from_completed_projects, str):
        include_from_completed_projects = include_from_completed_projects.lower() == "true"

    try:
        # Get list of completed projects to exclude their tasks
        completed_projects = []
        if not include_from_completed_projects:
            completed_projects = frappe.get_list(
                "Smart Project",
                filters={"status": "Completed"},
                pluck="name"
            )

        # Check if user has full access via Smart Pro Settings
        if user_can_view_all_tasks(user):
            # Build filters
            task_filters = {}
            if completed_projects:
                task_filters["project"] = ["not in", completed_projects]

            # Return all tasks (excluding from completed projects)
            tasks = frappe.get_list(
                "Smart Task",
                filters=task_filters if task_filters else None,
                fields=["name", "title", "project", "status", "priority", "due_date", "progress", "assigned_to", "project_scope"],
                order_by="due_date asc"
            )
            frappe.logger().info(f"get_user_tasks: User {user} has full access, returning {len(tasks)} tasks (from completed projects excluded: {not include_from_completed_projects})")
        else:
            # Get employee record for current user
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

            if not employee:
                frappe.logger().info(f"get_user_tasks: User {user} has no employee record")
                return []

            # ONLY get tasks from projects where employee is assigned via Employee Project Assignment
            assignments = frappe.get_list(
                "Employee Project Assignment",
                filters={
                    "employee": employee,
                    "status": "Active"
                },
                pluck="project"
            )

            if not assignments:
                frappe.logger().info(f"get_user_tasks: Employee {employee} has no active assignments")
                return []

            # Filter out completed projects from assignments
            if completed_projects:
                assignments = [p for p in assignments if p not in completed_projects]

            if not assignments:
                frappe.logger().info(f"get_user_tasks: All assigned projects are completed for employee {employee}")
                return []

            # Get tasks ONLY from assigned non-completed projects
            tasks = frappe.get_list(
                "Smart Task",
                filters={
                    "project": ["in", assignments]
                },
                fields=["name", "title", "project", "status", "priority", "due_date", "progress", "assigned_to", "project_scope"],
                order_by="due_date asc"
            )

            frappe.logger().info(f"get_user_tasks: Found {len(tasks)} tasks from {len(assignments)} assigned non-completed projects for employee {employee}")
        return tasks
    except Exception as e:
        frappe.logger().error(f"Error getting user tasks: {str(e)}")
        frappe.throw(f"Error loading tasks: {str(e)}")

@frappe.whitelist()
def get_project_details(project_name):
    """Get detailed information about a specific project"""
    try:
        project = frappe.get_doc("Smart Project", project_name)
        return {
            "name": project.name,
            "title": project.title,
            "description": project.description,
            "status": project.status,
            "project_manager": project.project_manager,
            "department": project.department,
            "start_date": str(project.start_date),
            "end_date": str(project.end_date),
            "budget_amount": project.budget_amount,
            "currency": project.currency,
        }
    except frappe.DoesNotExistError:
        frappe.throw(f"Project {project_name} not found")

@frappe.whitelist()
def get_project_tasks(project_name):
    """Get all tasks for a specific project"""
    tasks = frappe.get_list(
        "Smart Task",
        filters={
            "project": project_name
        },
        fields=["name", "title", "assigned_to", "status", "priority", "due_date", "progress", "project_scope"],
        order_by="due_date asc"
    )
    return tasks


@frappe.whitelist()
def get_task_details(task_name):
    """Get detailed information about a specific task including project scope"""
    try:
        task = frappe.get_doc("Smart Task", task_name)
        return {
            "name": task.name,
            "title": task.title,
            "description": task.description,
            "project": task.project,
            "assigned_to": task.assigned_to,
            "status": task.status,
            "priority": task.priority,
            "start_date": str(task.start_date) if task.start_date else None,
            "due_date": str(task.due_date) if task.due_date else None,
            "progress": task.progress,
            "project_scope": task.project_scope,
        }
    except frappe.DoesNotExistError:
        frappe.throw(f"Task {task_name} not found")

@frappe.whitelist()
def get_employee_assignments(project_name):
    """Get all employee assignments for a project"""
    assignments = frappe.get_list(
        "Employee Project Assignment",
        filters={
            "project": project_name,
            "status": "Active"
        },
        fields=["name", "employee", "employee_name", "role", "allocation_percentage", "start_date", "end_date"],
        order_by="employee_name asc"
    )
    return assignments

@frappe.whitelist()
def get_pending_date_requests():
    """Get all pending date requests for the current user"""
    user = frappe.session.user
    
    try:
        requests = frappe.get_list(
            "Employee Date Request",
            filters={
                "approver": user,
                "status": "Pending Approval"
            },
            fields=["name", "employee", "employee_name", "request_type", "from_date", "to_date", "reason"],
            order_by="modified desc"
        )
        frappe.logger().info(f"get_pending_date_requests: Found {len(requests)} requests for user {user}")
        return requests
    except Exception as e:
        frappe.logger().error(f"Error getting pending date requests: {str(e)}")
        frappe.throw(f"Error loading pending requests: {str(e)}")

@frappe.whitelist()
def get_debug_info():
    """Get debug information for troubleshooting"""
    user = frappe.session.user
    
    try:
        # Count records in each doctype
        project_count = frappe.db.count("Smart Project")
        task_count = frappe.db.count("Smart Task")
        request_count = frappe.db.count("Employee Date Request")
        assignment_count = frappe.db.count("Employee Project Assignment")
        
        # Get user-specific counts
        user_projects = frappe.db.count("Smart Project", {"project_manager": user})
        user_tasks = frappe.db.count("Smart Task", {"assigned_to": user})
        user_requests = frappe.db.count("Employee Date Request", {"approver": user, "status": "Pending Approval"})
        
        debug_info = {
            "current_user": user,
            "total_projects": project_count,
            "total_tasks": task_count,
            "total_requests": request_count,
            "total_assignments": assignment_count,
            "user_projects": user_projects,
            "user_tasks": user_tasks,
            "user_pending_requests": user_requests
        }
        
        frappe.logger().info(f"Debug info: {debug_info}")
        return debug_info
    except Exception as e:
        frappe.logger().error(f"Error getting debug info: {str(e)}")
        frappe.throw(f"Error getting debug info: {str(e)}")

@frappe.whitelist()
def get_team_members():
    """Get all team members managed by the current user (team lead)"""
    user = frappe.session.user
    
    try:
        # Get all employees assigned to projects managed by current user
        assignments = frappe.get_list(
            "Employee Project Assignment",
            filters={
                "project": ["in", frappe.get_list("Smart Project", filters={"project_manager": user}, pluck="name")]
            },
            fields=["name", "employee", "employee_name", "project", "role", "allocation_percentage", "status"],
            order_by="employee_name asc"
        )
        frappe.logger().info(f"get_team_members: Found {len(assignments)} team members for user {user}")
        return assignments
    except Exception as e:
        frappe.logger().error(f"Error getting team members: {str(e)}")
        frappe.throw(f"Error loading team members: {str(e)}")

@frappe.whitelist()
def get_team_tasks():
    """Get all tasks for projects managed by the current user"""
    user = frappe.session.user
    
    try:
        # Get all tasks for projects managed by current user
        tasks = frappe.get_list(
            "Smart Task",
            filters={
                "project": ["in", frappe.get_list("Smart Project", filters={"project_manager": user}, pluck="name")]
            },
            fields=["name", "title", "project", "assigned_to", "status", "priority", "due_date", "progress"],
            order_by="due_date asc"
        )
        frappe.logger().info(f"get_team_tasks: Found {len(tasks)} tasks for user {user}")
        return tasks
    except Exception as e:
        frappe.logger().error(f"Error getting team tasks: {str(e)}")
        frappe.throw(f"Error loading team tasks: {str(e)}")

@frappe.whitelist()
def get_pending_approvals():
    """Get all pending approvals (date requests and timesheets) for the current user"""
    user = frappe.session.user
    
    try:
        # Get pending date requests
        date_requests = frappe.get_list(
            "Employee Date Request",
            filters={
                "approver": user,
                "status": "Pending Approval"
            },
            fields=["name", "employee", "employee_name", "request_type", "from_date", "to_date", "reason"],
            order_by="modified desc"
        )
        
        frappe.logger().info(f"get_pending_approvals: Found {len(date_requests)} pending approvals for user {user}")
        return {
            "date_requests": date_requests
        }
    except Exception as e:
        frappe.logger().error(f"Error getting pending approvals: {str(e)}")
        frappe.throw(f"Error loading pending approvals: {str(e)}")

@frappe.whitelist()
def approve_date_request(request_id, status, comments=None):
    """Approve or reject a date request"""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)

    try:
        request_doc = frappe.get_doc("Employee Date Request", request_id)

        # Check if user is authorized to approve:
        # 1. User is the designated approver
        # 2. User has full access via Smart Pro Settings
        # 3. User is the project manager of the related project
        # 4. User is System Manager or Administrator
        # 5. No approver is set (self-approval allowed for project managers)
        is_approver = request_doc.approver == user
        has_full_access = user_has_full_access(user)
        is_system_manager = "System Manager" in user_roles or user == "Administrator"
        is_project_manager = False
        no_approver_set = not request_doc.approver  # Allow self-approval when no approver

        if request_doc.project:
            project_manager = frappe.db.get_value("Smart Project", request_doc.project, "project_manager")
            is_project_manager = project_manager == user

        # Log authorization check for debugging
        frappe.logger().info(f"Approval check - User: {user}, Approver: {request_doc.approver}, "
                            f"is_approver: {is_approver}, has_full_access: {has_full_access}, "
                            f"is_system_manager: {is_system_manager}, is_project_manager: {is_project_manager}, "
                            f"no_approver_set: {no_approver_set}, roles: {user_roles}")

        if not (is_approver or has_full_access or is_system_manager or is_project_manager or no_approver_set):
            frappe.throw(f"You are not authorized to approve this request. User: {user}, Approver: {request_doc.approver}")

        # Store old status to detect change
        old_status = request_doc.status

        # Update status
        request_doc.status = status  # "Approved" or "Rejected"
        if comments:
            request_doc.comments = comments
        request_doc.save()

        # Manually trigger approval/rejection actions if status changed
        message = f"Request {status.lower()} successfully"
        if old_status != status:
            if status == "Approved":
                # Call the on_approval method explicitly to create tasks and update dates
                request_doc.on_approval()
                frappe.db.commit()
                message = "Request approved! Project dates updated and tasks created."
                frappe.logger().info(f"Date request {request_id} approved - tasks created and dates updated")
            elif status == "Rejected":
                request_doc.on_rejection()
                message = "Request rejected."

        frappe.logger().info(f"Date request {request_id} {status} by {user}")
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        frappe.logger().error(f"Error approving date request: {str(e)}")
        frappe.throw(f"Error approving request: {str(e)}")


@frappe.whitelist()
def update_date_request(request_id, from_date, to_date, reason=None):
    """Update dates on a pending date request"""
    user = frappe.session.user

    try:
        request_doc = frappe.get_doc("Employee Date Request", request_id)

        # Only allow updates on pending requests
        if request_doc.status != "Pending Approval":
            frappe.throw("Only pending requests can be modified")

        # Verify user is the employee who created it, the approver, or has full access
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if request_doc.employee != employee and request_doc.approver != user and not user_has_full_access(user):
            frappe.throw("You are not authorized to modify this request")

        # Update dates
        request_doc.from_date = from_date
        request_doc.to_date = to_date
        if reason:
            request_doc.reason = reason
        request_doc.save()

        frappe.logger().info(f"Date request {request_id} updated by {user}")
        return {
            "success": True,
            "message": "Request updated successfully"
        }
    except Exception as e:
        frappe.logger().error(f"Error updating date request: {str(e)}")
        frappe.throw(f"Error updating request: {str(e)}")

@frappe.whitelist()
def get_user_time_sheets():
    """Get all time sheets for the current user"""
    user = frappe.session.user
    
    try:
        # Get employee record for current user
        employee = frappe.get_list(
            "Employee",
            filters={"user_id": user},
            pluck="name"
        )
        
        if not employee:
            return []
        
        timesheets = frappe.get_list(
            "Smart Time Sheet",
            filters={
                "employee": employee[0]
            },
            fields=["name", "date", "task", "hours_worked", "project", "status"],
            order_by="date desc"
        )
        frappe.logger().info(f"get_user_time_sheets: Found {len(timesheets)} time sheets for user {user}")
        return timesheets
    except Exception as e:
        frappe.logger().error(f"Error getting time sheets: {str(e)}")
        frappe.throw(f"Error loading time sheets: {str(e)}")

@frappe.whitelist()
def get_team_time_sheets():
    """Get all time sheets for team members managed by current user"""
    user = frappe.session.user
    
    try:
        # Get all team members
        team_members = frappe.get_list(
            "Employee Project Assignment",
            filters={
                "project": ["in", frappe.get_list("Smart Project", filters={"project_manager": user}, pluck="name")]
            },
            pluck="employee"
        )
        
        if not team_members:
            return []
        
        # Get time sheets for all team members
        timesheets = frappe.get_list(
            "Smart Time Sheet",
            filters={
                "employee": ["in", team_members]
            },
            fields=["name", "employee", "date", "task", "hours_worked", "project", "status"],
            order_by="date desc"
        )
        frappe.logger().info(f"get_team_time_sheets: Found {len(timesheets)} time sheets for user {user}")
        return timesheets
    except Exception as e:
        frappe.logger().error(f"Error getting team time sheets: {str(e)}")
        frappe.throw(f"Error loading team time sheets: {str(e)}")

@frappe.whitelist()
def get_user_roles():
    """Get roles of the current user"""
    user = frappe.session.user

    try:
        roles = frappe.get_roles(user)
        frappe.logger().info(f"get_user_roles: User {user} has roles {roles}")
        return {
            "roles": roles,
            "is_team_lead": "Projects Manager" in roles or "HR Manager" in roles or "HR-Manager" in roles,
            "is_employee": "Employee" in roles
        }
    except Exception as e:
        frappe.logger().error(f"Error getting user roles: {str(e)}")
        frappe.throw(f"Error loading user roles: {str(e)}")


# ==================== EMPLOYEE ASSIGNED PROJECTS ====================

@frappe.whitelist()
def get_employee_assigned_projects():
    """Get all projects assigned to the current employee"""
    user = frappe.session.user

    try:
        # Get employee record for current user
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            return []

        # Get all active assignments for this employee
        assignments = frappe.get_list(
            "Employee Project Assignment",
            filters={
                "employee": employee,
                "status": "Active"
            },
            fields=["name", "project", "role", "allocation_percentage", "start_date", "end_date"]
        )

        # Get project details for each assignment
        projects = []
        for assignment in assignments:
            project = frappe.get_doc("Smart Project", assignment.project)
            projects.append({
                "assignment": assignment.name,
                "project": project.name,
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "project_manager": project.project_manager,
                "start_date": str(project.start_date) if project.start_date else None,
                "end_date": str(project.end_date) if project.end_date else None,
                "role": assignment.role,
                "allocation_percentage": assignment.allocation_percentage
            })

        return projects
    except Exception as e:
        frappe.logger().error(f"Error getting employee assigned projects: {str(e)}")
        frappe.throw(f"Error loading assigned projects: {str(e)}")


# ==================== EMPLOYEE DATE REQUEST APIs ====================

@frappe.whitelist()
def get_my_date_requests():
    """Get all date requests submitted by current employee"""
    user = frappe.session.user

    try:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            return []

        requests = frappe.get_list(
            "Employee Date Request",
            filters={"employee": employee},
            fields=["name", "request_type", "project", "project_title", "from_date", "to_date",
                    "total_days", "status", "reason", "approver", "comments", "auto_create_tasks",
                    "project_scope", "assignment"],
            order_by="modified desc"
        )

        return requests
    except Exception as e:
        frappe.logger().error(f"Error getting date requests: {str(e)}")
        frappe.throw(f"Error loading date requests: {str(e)}")


@frappe.whitelist()
def create_date_request(project, from_date, to_date, reason, request_type="Project Date Update", auto_create_tasks=1):
    """Create a new Employee Date Request"""
    user = frappe.session.user

    try:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            frappe.throw("You are not linked to an employee record")

        # Create the request
        doc = frappe.get_doc({
            "doctype": "Employee Date Request",
            "employee": employee,
            "request_type": request_type,
            "project": project,
            "from_date": from_date,
            "to_date": to_date,
            "reason": reason,
            "auto_create_tasks": auto_create_tasks,
            "status": "Pending Approval"
        })
        doc.insert()

        return {
            "success": True,
            "name": doc.name,
            "message": "Date request created successfully"
        }
    except Exception as e:
        frappe.logger().error(f"Error creating date request: {str(e)}")
        frappe.throw(f"Error creating date request: {str(e)}")


# ==================== TIMESHEET APIs ====================

@frappe.whitelist()
def get_my_timesheets(from_date=None, to_date=None):
    """Get all timesheets for current employee"""
    user = frappe.session.user

    try:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            return []

        filters = {"employee": employee}

        if from_date:
            filters["date"] = [">=", from_date]
        if to_date:
            if "date" in filters:
                filters["date"] = ["between", [from_date, to_date]]
            else:
                filters["date"] = ["<=", to_date]

        timesheets = frappe.get_list(
            "Smart Timesheet",
            filters=filters,
            fields=["name", "date", "project", "task", "task_title", "activity_type",
                    "hours_worked", "description", "status"],
            order_by="date desc"
        )

        return timesheets
    except Exception as e:
        frappe.logger().error(f"Error getting timesheets: {str(e)}")
        frappe.throw(f"Error loading timesheets: {str(e)}")


@frappe.whitelist()
def create_timesheet(task, date, hours_worked, description, activity_type="Development", notes=None):
    """Create a new timesheet entry from a task"""
    user = frappe.session.user

    try:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            frappe.throw("You are not linked to an employee record")

        # Get task details
        task_doc = frappe.get_doc("Smart Task", task)

        # Check if timesheet already exists for this task and date
        existing = frappe.db.exists("Smart Timesheet", {
            "employee": employee,
            "task": task,
            "date": date
        })

        if existing:
            frappe.throw(f"Timesheet already exists for this task on {date}")

        # Create timesheet
        doc = frappe.get_doc({
            "doctype": "Smart Timesheet",
            "employee": employee,
            "date": date,
            "project": task_doc.project,
            "task": task,
            "activity_type": activity_type,
            "hours_worked": hours_worked,
            "description": description,
            "notes": notes,
            "status": "Draft"
        })
        doc.insert()

        return {
            "success": True,
            "name": doc.name,
            "message": "Timesheet created successfully"
        }
    except Exception as e:
        frappe.logger().error(f"Error creating timesheet: {str(e)}")
        frappe.throw(f"Error creating timesheet: {str(e)}")


@frappe.whitelist()
def submit_timesheet(timesheet_name):
    """Submit a timesheet for approval"""
    try:
        doc = frappe.get_doc("Smart Timesheet", timesheet_name)
        doc.status = "Submitted"
        doc.save()

        return {
            "success": True,
            "message": "Timesheet submitted successfully"
        }
    except Exception as e:
        frappe.logger().error(f"Error submitting timesheet: {str(e)}")
        frappe.throw(f"Error submitting timesheet: {str(e)}")


@frappe.whitelist()
def get_task_timesheets(task_name):
    """Get all timesheets for a specific task"""
    try:
        timesheets = frappe.get_list(
            "Smart Timesheet",
            filters={"task": task_name},
            fields=["name", "employee", "employee_name", "date", "hours_worked",
                    "activity_type", "description", "status"],
            order_by="date desc"
        )

        # Calculate total hours
        total_hours = sum(ts.get("hours_worked", 0) for ts in timesheets)

        return {
            "timesheets": timesheets,
            "total_hours": total_hours
        }
    except Exception as e:
        frappe.logger().error(f"Error getting task timesheets: {str(e)}")
        frappe.throw(f"Error loading task timesheets: {str(e)}")


@frappe.whitelist()
def get_today_summary():
    """Get today's work summary for current employee"""
    user = frappe.session.user
    from frappe.utils import today

    try:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            return {"timesheets": [], "total_hours": 0, "tasks_worked": 0}

        timesheets = frappe.get_list(
            "Smart Timesheet",
            filters={
                "employee": employee,
                "date": today()
            },
            fields=["name", "task", "task_title", "project", "hours_worked", "activity_type", "status"]
        )

        total_hours = sum(ts.get("hours_worked", 0) for ts in timesheets)

        return {
            "timesheets": timesheets,
            "total_hours": total_hours,
            "tasks_worked": len(timesheets)
        }
    except Exception as e:
        frappe.logger().error(f"Error getting today summary: {str(e)}")
        frappe.throw(f"Error loading today summary: {str(e)}")


# ==================== APP SETTINGS API ====================

@frappe.whitelist(allow_guest=True)
def get_app_settings():
    """Get app settings for mobile app branding"""
    try:
        settings = frappe.get_single("Smart Pro Settings")
        return {
            "app_name": settings.app_name or "Smart Pro",
            "app_logo": settings.app_logo or None,
            "enable_notifications": settings.enable_notifications,
            "enable_offline_mode": settings.enable_offline_mode,
        }
    except Exception as e:
        frappe.logger().error(f"Error getting app settings: {str(e)}")
        return {
            "app_name": "Smart Pro",
            "app_logo": None,
            "enable_notifications": 1,
            "enable_offline_mode": 1,
        }


# ==================== CONNECTIONS DASHBOARD API ====================

@frappe.whitelist()
def get_connections_dashboard():
    """Get counts and statistics for all Smart Pro doctypes"""
    try:
        # Smart Projects counts
        all_projects = frappe.db.count("Smart Project")
        active_projects = frappe.db.count("Smart Project", {"status": "Active"})
        planning_projects = frappe.db.count("Smart Project", {"status": "Planning"})
        completed_projects = frappe.db.count("Smart Project", {"status": "Completed"})

        # Employee Project Assignments count
        assignments = frappe.db.count("Employee Project Assignment")

        # Employee Date Requests counts
        all_requests = frappe.db.count("Employee Date Request")
        pending_requests = frappe.db.count("Employee Date Request", {"status": "Pending Approval"})
        approved_requests = frappe.db.count("Employee Date Request", {"status": "Approved"})
        rejected_requests = frappe.db.count("Employee Date Request", {"status": "Rejected"})

        # Smart Tasks counts
        all_tasks = frappe.db.count("Smart Task")
        open_tasks = frappe.db.count("Smart Task", {"status": "Open"})
        working_tasks = frappe.db.count("Smart Task", {"status": "Working"})
        completed_tasks = frappe.db.count("Smart Task", {"status": "Completed"})

        # Smart Timesheets counts
        all_timesheets = frappe.db.count("Smart Timesheet")
        draft_timesheets = frappe.db.count("Smart Timesheet", {"status": "Draft"})
        submitted_timesheets = frappe.db.count("Smart Timesheet", {"status": "Submitted"})
        approved_timesheets = frappe.db.count("Smart Timesheet", {"status": "Approved"})

        # Notifications count
        notifications = frappe.db.count("Smart Pro Notification") if frappe.db.exists("DocType", "Smart Pro Notification") else 0

        return {
            "projects": all_projects,
            "activeProjects": active_projects,
            "planningProjects": planning_projects,
            "completedProjects": completed_projects,
            "assignments": assignments,
            "dateRequests": all_requests,
            "pendingRequests": pending_requests,
            "approvedRequests": approved_requests,
            "rejectedRequests": rejected_requests,
            "tasks": all_tasks,
            "openTasks": open_tasks,
            "workingTasks": working_tasks,
            "completedTasks": completed_tasks,
            "timesheets": all_timesheets,
            "draftTimesheets": draft_timesheets,
            "submittedTimesheets": submitted_timesheets,
            "approvedTimesheets": approved_timesheets,
            "notifications": notifications,
        }
    except Exception as e:
        frappe.logger().error(f"Error getting connections dashboard: {str(e)}")
        return {
            "projects": 0,
            "activeProjects": 0,
            "planningProjects": 0,
            "completedProjects": 0,
            "assignments": 0,
            "dateRequests": 0,
            "pendingRequests": 0,
            "approvedRequests": 0,
            "rejectedRequests": 0,
            "tasks": 0,
            "openTasks": 0,
            "workingTasks": 0,
            "completedTasks": 0,
            "timesheets": 0,
            "draftTimesheets": 0,
            "submittedTimesheets": 0,
            "approvedTimesheets": 0,
            "notifications": 0,
        }


# ==================== NOTIFICATIONS ====================

@frappe.whitelist()
def mark_notification_as_read(notification_name, source="smart_pro"):
    """Mark a notification as read"""
    try:
        if source == "smart_pro":
            if frappe.db.exists("Smart Pro Notification", notification_name):
                frappe.db.set_value("Smart Pro Notification", notification_name, "status", "read")
                frappe.db.commit()
                return {"success": True}
        else:
            if frappe.db.exists("Notification Log", notification_name):
                frappe.db.set_value("Notification Log", notification_name, "read", 1)
                frappe.db.commit()
                return {"success": True}
        return {"success": False, "message": "Notification not found"}
    except Exception as e:
        frappe.logger().error(f"Error marking notification as read: {str(e)}")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def mark_all_notifications_as_read():
    """Mark all notifications as read for current user"""
    user = frappe.session.user

    try:
        # Mark Smart Pro Notifications as read
        frappe.db.sql("""
            UPDATE `tabSmart Pro Notification`
            SET status = 'read'
            WHERE user = %s AND status != 'read'
        """, (user,))

        # Mark Frappe Notification Log as read
        frappe.db.sql("""
            UPDATE `tabNotification Log`
            SET `read` = 1
            WHERE for_user = %s AND `read` = 0
        """, (user,))

        frappe.db.commit()
        return {"success": True}
    except Exception as e:
        frappe.logger().error(f"Error marking all notifications as read: {str(e)}")
        return {"success": False, "message": str(e)}