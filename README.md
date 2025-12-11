# Smart Pro

A comprehensive project management and employee assignment system built on Frappe Framework with a PWA mobile app.

## Features

- **Project Management**: Create and manage projects with AI-powered descriptions
- **Employee Assignment**: Assign employees to projects with roles and scopes
- **Date Request Workflow**: Request and approve project date changes
- **Task Management**: Track tasks with status, priority, and progress
- **Timesheet Tracking**: Log work hours against projects and tasks
- **Mobile PWA App**: Full-featured mobile app with offline support
- **AI Integration**: DeepSeek/OpenAI powered description and scope generation
- **Social Login**: Google, GitHub, Facebook, Microsoft OAuth support
- **Push Notifications**: Real-time notifications for approvals and updates
- **Dark Mode**: Full dark mode support in mobile app

---

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/codfatherlogic/smart_pro.git
bench --site your-site install-app smart_pro
bench build --app smart_pro
bench migrate
```

### Access Mobile App

After installation, access the PWA at:
```
https://your-site.com/smart-pro
```

---

## DocTypes & Workflow

### 1. Smart Project

Main project entity that holds all project information.

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Project title (required) |
| description | Text Editor | AI-generated or manual description |
| status | Select | Planning / Active / On Hold / Completed / Cancelled |
| project_manager | Link (User) | User responsible for the project |
| department | Link | Department association |
| start_date | Date | Project start date |
| end_date | Date | Project end date |
| budget_amount | Currency | Project budget |

**Workflow:**
```
1. Create Project (Status: Planning)
2. Add description manually or use AI > Generate Description
3. Assign employees via Employee Project Assignment
4. Change status to Active when work begins
5. Track progress via Tasks and Timesheets
6. Mark as Completed when done
```

**AI Feature:** Click `AI > Generate Description` to auto-generate project description using DeepSeek/OpenAI.

---

### 2. Employee Project Assignment (EPA)

Links employees to projects with specific roles and scopes.

| Field | Type | Description |
|-------|------|-------------|
| employee | Link (Employee) | Assigned employee (required) |
| project | Link (Smart Project) | Target project (required) |
| role | Link (Smart Role) | Employee's role on project |
| status | Select | Active / On Hold / Completed / Cancelled |
| approver | Link (User) | User who approves date requests |
| start_date | Date | Assignment start date |
| end_date | Date | Assignment end date |
| project_scope | Text Editor | AI-generated or manual scope details |
| allocation_percentage | Percent | % of employee's time allocated |

**Workflow:**
```
1. Create Assignment for employee on a project
2. Set role and allocation percentage
3. Define approver for date requests (defaults to project manager if empty)
4. Use AI > Generate Scope to create scope details
5. Employee can now view project in mobile app
```

**AI Feature:** Click `AI > Generate Scope` to auto-generate project scope based on project title, employee name, and role.

---

### 3. Employee Date Request

Workflow for employees to request project date changes.

| Field | Type | Description |
|-------|------|-------------|
| employee | Link (Employee) | Requesting employee |
| project | Link (Smart Project) | Target project |
| request_type | Select | Project Date Update / Leave Request |
| from_date | Date | Requested start date |
| to_date | Date | Requested end date |
| status | Select | Draft / Pending Approval / Approved / Rejected |
| approver | Link (User) | Auto-set from EPA or project manager |
| auto_create_tasks | Check | Create task on approval |
| project_scope | Text Editor | Inherited from EPA |

**Workflow:**
```
1. Employee creates date request from mobile app
2. System auto-sets approver from EPA (or project manager as fallback)
3. Approver receives notification
4. Approver reviews and Approves/Rejects
5. If approved:
   - Project dates are updated
   - Assignment dates are updated
   - Task is created (if auto_create_tasks enabled)
6. Employee receives notification of decision
```

**Approval Logic:**
- Checks EPA's `approver` field first
- Falls back to `project_manager` if EPA approver is not set
- Project managers can self-approve their own requests

---

### 4. Smart Task

Task management linked to projects.

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Task title |
| project | Link (Smart Project) | Parent project |
| assigned_to | Link (User) | Assigned user |
| status | Select | Open / Working / Pending Review / Completed / Cancelled |
| priority | Select | Low / Medium / High / Critical |
| start_date | Date | Task start date |
| due_date | Date | Task due date |
| progress | Percent | Completion percentage |
| description | Text Editor | Task details |
| project_scope | Text Editor | Inherited scope |

**Workflow:**
```
1. Tasks are auto-created when date requests are approved (if enabled)
2. Or manually create tasks from project
3. Assign to users
4. Track progress (0-100%)
5. Update status as work progresses
6. Mark as Completed when done
```

---

### 5. Smart Timesheet

Time tracking against projects and tasks.

| Field | Type | Description |
|-------|------|-------------|
| employee | Link (Employee) | Employee logging time |
| project | Link (Smart Project) | Target project |
| task | Link (Smart Task) | Optional task reference |
| date | Date | Work date |
| hours | Float | Hours worked |
| description | Text | Work description |
| status | Select | Draft / Submitted / Approved |

**Workflow:**
```
1. Employee logs time from mobile app
2. Select project and optionally task
3. Enter hours and description
4. Submit for approval
5. Manager approves timesheet
```

---

### 6. Smart Pro Settings

Global configuration for the app.

| Section | Fields | Description |
|---------|--------|-------------|
| Branding | app_name, app_logo | Mobile app branding |
| General | enable_notifications, enable_email_notifications, enable_offline_mode | Feature toggles |
| Defaults | default_project_status, default_task_priority | Default values |
| AI Settings | enable_ai_features, ai_provider, deepseek_api_key, ai_prompt_template | AI configuration |
| Permissions | users_with_full_access, roles_with_full_access | Access control |

**AI Setup:**
1. Enable AI Features
2. Select Provider (DeepSeek or OpenAI)
3. Enter API Key
4. Customize prompt template (optional)

---

### 7. Smart Role

Simple role definitions for project assignments.

| Field | Type | Description |
|-------|------|-------------|
| smart_role | Data | Role name (e.g., Developer, Designer, Manager) |

---

## Mobile App Features

### Pages
- **Home**: Dashboard with project count and recent activity
- **Projects**: List all assigned projects with status filters
- **Tasks**: View and manage tasks with status tabs
- **Date Requests**: Create and track date requests
- **Timesheets**: Log and view time entries
- **Approvals**: Approve/reject pending requests (for managers)
- **Notifications**: View all notifications
- **Profile**: User profile and settings

### Features
- Pull-to-refresh on all pages
- Dark mode with system preference detection
- Offline caching
- PWA install prompt
- Social login (Google, GitHub, etc.)
- Push notifications

---

## API Endpoints

### Projects
```python
smart_pro.smart_pro.api.projects.get_user_projects(include_completed=False)
smart_pro.smart_pro.api.projects.get_user_tasks(include_from_completed_projects=False)
smart_pro.smart_pro.api.projects.get_my_date_requests(include_from_completed_projects=False)
smart_pro.smart_pro.api.projects.get_my_timesheets(from_date, to_date, include_from_completed_projects=False)
```

### AI Generation
```python
smart_pro.smart_pro.api.projects.generate_project_description(title)
smart_pro.smart_pro.api.projects.generate_project_scope(project_title, employee_name, role)
```

### Social Login
```python
smart_pro.smart_pro.api.projects.get_social_login_providers(redirect_to)
```

---

## CI/CD

### GitHub Actions Workflows

**CI (ci.yml)** - Runs on push to `develop` branch:
- Sets up Python 3.10, Node 18, MariaDB
- Installs Frappe and Smart Pro
- Runs unit tests

**Linters (linter.yml)** - Runs on pull requests:
- Pre-commit hooks (ruff, eslint, prettier)
- Semgrep security rules
- pip-audit vulnerability check

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release with full feature set |
| 0.0.1 | Development version |

---

## Contributing

1. Install pre-commit hooks:
```bash
cd apps/smart_pro
pre-commit install
```

2. Code formatting tools:
- **Python**: ruff
- **JavaScript**: eslint, prettier

3. Run tests:
```bash
bench --site your-site run-tests --app smart_pro
```

---

## License

MIT License - See [license.txt](license.txt)

---

## Support

Report issues at: https://github.com/codfatherlogic/smart_pro/issues
