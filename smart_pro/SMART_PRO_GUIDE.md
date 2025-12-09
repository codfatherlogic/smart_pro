# Smart Pro - Project Management with Employee Assignment

A simplified Frappe-based project management solution with FrappeUI support, designed for managing projects, tasks, project plans, employee assignments, and employee date requests.

## Features

### 1. **Smart Project**
- Create and manage projects with detailed information
- Track project status (Planning, Active, On Hold, Completed, Cancelled)
- Assign project managers and departments
- Set budgets and track financial information
- Define project timelines with start and end dates

### 2. **Smart Task**
- Create tasks within projects
- Assign tasks to employees
- Track task progress with percentage completion
- Set priority levels (Low, Medium, High, Critical)
- Monitor task status (Open, Working, Pending Review, Completed, Cancelled)

### 3. **Project Plan**
- Break down projects into phases
- Create milestones within each phase
- Track phase completion status
- Manage project timelines at the phase level

### 4. **Employee Project Assignment**
- Assign employees to projects with specific roles
- Set allocation percentages (how much time an employee dedicates to a project)
- Track assignment dates and duration
- Manage assignment status (Active, On Hold, Completed, Cancelled)

### 5. **Employee Date Request**
- Employees can request time off (Leave, Time Off, Work From Home, etc.)
- Submit requests for approval
- Managers can approve or reject requests
- Track request status throughout the workflow

## Doctypes

### Smart Project
**Fields:**
- Project Title (required)
- Description
- Status (Planning, Active, On Hold, Completed, Cancelled)
- Project Manager
- Department
- Start Date
- End Date
- Budget Amount
- Currency

**Permissions:**
- System Manager: Full access
- Employee: Read-only access
- Project Manager: Create, read, write, submit

---

### Smart Task
**Fields:**
- Task Title (required)
- Description
- Project (Link to Smart Project)
- Assigned To (User)
- Status (Open, Working, Pending Review, Completed, Cancelled)
- Priority (Low, Medium, High, Critical)
- Start Date
- Due Date
- Progress (0-100%)

**Permissions:**
- System Manager: Full access
- Employee: Create, read, write (for assigned tasks)
- Project Manager: Create, read, write, submit

---

### Project Plan
**Fields:**
- Phase Name (required)
- Project (required, Link to Smart Project)
- Description
- Status (Planning, In Progress, Completed, On Hold)
- Start Date
- End Date
- Milestone Tasks (Child table - Project Plan Task)

**Child Table: Project Plan Task**
- Task Name (required)
- Description
- Status (Pending, In Progress, Completed, Cancelled)
- Assigned To (User)

---

### Employee Project Assignment
**Fields:**
- Employee (required, Link to Employee)
- Employee Name (read-only, auto-fetched)
- Project (required, Link to Smart Project)
- Role (required)
- Allocation Percentage (0-100%, default 100)
- Status (Active, On Hold, Completed, Cancelled)
- Start Date (required)
- End Date

**Permissions:**
- System Manager: Full access
- Employee: Read-only access
- HR Manager: Create, read, write, submit

---

### Employee Date Request
**Fields:**
- Employee (required, Link to Employee)
- Employee Name (read-only, auto-fetched)
- Request Type (Leave, Time Off, Work From Home, Overtime, Other)
- From Date (required)
- To Date (required)
- Reason (required, Text Editor)
- Approver (User)
- Status (Draft, Pending Approval, Approved, Rejected, Cancelled)
- Comments (Text Editor)

**Workflow States:**
1. Draft → Pending Approval (on submit)
2. Pending Approval → Approved (on approval)
3. Pending Approval → Rejected (on rejection)

---

## API Endpoints

The app provides several whitelisted API endpoints for frontend integration:

### Projects API

#### `get_user_projects()`
Returns all projects managed by the current user.

**Response:**
```json
[
  {
    "name": "PRJ-001",
    "title": "Website Redesign",
    "status": "Active",
    "start_date": "2025-01-01",
    "end_date": "2025-03-31",
    "budget_amount": 50000
  }
]
```

#### `get_user_tasks()`
Returns all tasks assigned to the current user.

**Response:**
```json
[
  {
    "name": "TSK-001",
    "title": "Design Homepage",
    "project": "PRJ-001",
    "status": "Working",
    "priority": "High",
    "due_date": "2025-02-15",
    "progress": 60
  }
]
```

#### `get_project_details(project_name)`
Returns detailed information about a specific project.

**Parameters:**
- `project_name` (string): Name of the project

**Response:**
```json
{
  "name": "PRJ-001",
  "title": "Website Redesign",
  "description": "Complete redesign of company website",
  "status": "Active",
  "project_manager": "john@example.com",
  "department": "IT",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "budget_amount": 50000,
  "currency": "INR"
}
```

#### `get_project_tasks(project_name)`
Returns all tasks for a specific project.

#### `get_employee_assignments(project_name)`
Returns all active employee assignments for a project.

#### `get_pending_date_requests()`
Returns all pending date requests for the current user (as approver).

---

## Workflows

### Smart Project Workflow
- **Draft** → **Active**: Project is activated
- **Active** → **Completed**: Project is completed
- **Active** → **Cancelled**: Project is cancelled

### Employee Date Request Workflow
- **Draft** → **Pending Approval**: Request is submitted
- **Pending Approval** → **Approved**: Request is approved by manager
- **Pending Approval** → **Rejected**: Request is rejected

---

## Frontend Components

### Projects Dashboard
Located at `/app/projects_dashboard`

Features:
- View all user projects
- View assigned tasks with progress tracking
- View pending date requests for approval
- Click on projects to see detailed information
- View employee assignments for selected project

**Technologies:**
- Vue.js 3
- Bootstrap 5
- Frappe Framework

---

## Installation

1. Clone the repository:
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app smart_pro
```

2. Install the app:
```bash
bench install-app smart_pro
```

3. Migrate database:
```bash
bench migrate
```

4. Create initial data (optional):
```bash
bench console
# Create test projects, tasks, etc.
```

---

## Permissions & Roles

### System Manager
- Full access to all doctypes
- Can create, read, write, delete, submit, and cancel all documents

### HR Manager
- Full access to Smart Project, Project Plan, Employee Project Assignment
- Can read and write Employee Date Requests
- Read-only access to Smart Task

### Project Manager
- Can create and manage Smart Projects
- Can create and manage Smart Tasks
- Can create and manage Project Plans
- Read-only access to Employee Project Assignment and Employee Date Request

### Employee
- Read-only access to Smart Projects
- Can read and write assigned Smart Tasks
- Read-only access to Project Plans
- Can create, read, and submit Employee Date Requests

---

## Validation Rules

### Smart Project
- Start Date cannot be after End Date
- Status automatically updates to "Active" when start date is reached

### Smart Task
- Start Date cannot be after Due Date
- Progress must be between 0 and 100
- Status automatically updates to "Working" when progress > 0
- Status automatically updates to "Completed" when progress = 100

### Employee Project Assignment
- Start Date cannot be after End Date
- Allocation Percentage must be between 0 and 100
- Employee Name is auto-fetched from Employee record

### Employee Date Request
- From Date cannot be after To Date
- Employee Name is auto-fetched from Employee record
- Status automatically updates to "Pending Approval" on submit

---

## Development

### Adding New Features

1. **Create a new Doctype:**
   - Create directory: `smart_pro/smart_pro/doctype/your_doctype/`
   - Add `__init__.py`, `.json` (schema), and `.py` (controller) files

2. **Add API Endpoints:**
   - Add whitelisted methods to `smart_pro/smart_pro/api/projects.py`
   - Use `@frappe.whitelist()` decorator

3. **Update Permissions:**
   - Modify `smart_pro/smart_pro/permissions.py`
   - Add role-based access control

4. **Create Frontend Components:**
   - Add Vue components to `smart_pro/public/js/`
   - Add styles to `smart_pro/public/css/`

---

## Troubleshooting

### Projects not appearing in dashboard
- Check user permissions
- Verify user is assigned as project manager
- Check project status

### Tasks not updating progress
- Ensure task status is not "Completed"
- Check user permissions for task write access

### Date requests not appearing for approval
- Verify user is set as approver
- Check request status is "Pending Approval"

---

## Support & Contribution

For issues, feature requests, or contributions, please refer to the main project repository.

---

## License

MIT License - See LICENSE file for details