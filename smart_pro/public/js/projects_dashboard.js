frappe.pages['projects_dashboard'].onload = function(wrapper) {
    const { __, frappe } = window;
    
    // Create a new Vue app
    const app = new Vue({
        el: wrapper,
        data() {
            return {
                projects: [],
                tasks: [],
                pendingRequests: [],
                loading: true,
                selectedProject: null,
                projectDetails: null,
                projectTasks: [],
                projectAssignments: []
            };
        },
        mounted() {
            this.loadData();
        },
        methods: {
            async loadData() {
                this.loading = true;
                try {
                    const [projects, tasks, requests] = await Promise.all([
                        frappe.call('smart_pro.api.projects.get_user_projects'),
                        frappe.call('smart_pro.api.projects.get_user_tasks'),
                        frappe.call('smart_pro.api.projects.get_pending_date_requests')
                    ]);
                    
                    this.projects = projects.message || [];
                    this.tasks = tasks.message || [];
                    this.pendingRequests = requests.message || [];
                } catch (error) {
                    console.error('Error loading data:', error);
                    frappe.msgprint(__('Error loading data: ') + error.message);
                } finally {
                    this.loading = false;
                }
            },
            
            async selectProject(project) {
                this.selectedProject = project;
                try {
                    const [details, tasks, assignments] = await Promise.all([
                        frappe.call('smart_pro.api.projects.get_project_details', { project_name: project.name }),
                        frappe.call('smart_pro.api.projects.get_project_tasks', { project_name: project.name }),
                        frappe.call('smart_pro.api.projects.get_employee_assignments', { project_name: project.name })
                    ]);
                    
                    this.projectDetails = details.message;
                    this.projectTasks = tasks.message || [];
                    this.projectAssignments = assignments.message || [];
                } catch (error) {
                    console.error('Error loading project details:', error);
                    frappe.msgprint(__('Error loading project details: ') + error.message);
                }
            },
            
            formatDate(dateString) {
                if (!dateString) return '';
                return frappe.datetime.str_to_user(dateString);
            },
            
            getStatusColor(status) {
                const colors = {
                    'Active': 'green',
                    'Planning': 'blue',
                    'Completed': 'gray',
                    'Cancelled': 'red',
                    'On Hold': 'orange',
                    'Open': 'blue',
                    'Working': 'orange',
                    'Pending Review': 'yellow',
                    'Pending Approval': 'yellow',
                    'Approved': 'green',
                    'Rejected': 'red'
                };
                return colors[status] || 'gray';
            }
        },
        template: `
            <div class="container-fluid">
                <div class="page-header">
                    <h1>Projects Dashboard</h1>
                    <p class="text-muted">Manage your projects, tasks, and employee assignments</p>
                </div>
                
                <div v-if="loading" class="text-center p-5">
                    <div class="spinner-border" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>
                
                <div v-else class="row">
                    <!-- Left Column: Projects and Tasks -->
                    <div class="col-md-8">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">My Projects</h5>
                            </div>
                            <div class="card-body">
                                <div v-if="projects.length === 0" class="text-muted">
                                    No projects found
                                </div>
                                <div v-else class="list-group">
                                    <a href="#" 
                                       v-for="project in projects" 
                                       :key="project.name"
                                       class="list-group-item list-group-item-action"
                                       @click.prevent="selectProject(project)">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ project.title }}</h6>
                                            <small :class="'badge bg-' + getStatusColor(project.status)">
                                                {{ project.status }}
                                            </small>
                                        </div>
                                        <p class="mb-1 text-muted">
                                            {{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) }}
                                        </p>
                                        <small v-if="project.budget_amount" class="text-muted">
                                            Budget: {{ project.budget_amount }}
                                        </small>
                                    </a>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">My Tasks</h5>
                            </div>
                            <div class="card-body">
                                <div v-if="tasks.length === 0" class="text-muted">
                                    No tasks assigned
                                </div>
                                <div v-else class="list-group">
                                    <div v-for="task in tasks" :key="task.name" class="list-group-item">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small :class="'badge bg-' + getStatusColor(task.status)">
                                                {{ task.status }}
                                            </small>
                                        </div>
                                        <p class="mb-1 text-muted">
                                            Project: {{ task.project }} | Due: {{ formatDate(task.due_date) }}
                                        </p>
                                        <div class="progress" style="height: 5px;">
                                            <div class="progress-bar" :style="{ width: task.progress + '%' }"></div>
                                        </div>
                                        <small class="text-muted">Progress: {{ task.progress }}%</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Right Column: Selected Project Details -->
                    <div class="col-md-4">
                        <div v-if="selectedProject" class="card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">Project Details</h5>
                            </div>
                            <div class="card-body">
                                <h6>{{ projectDetails ? projectDetails.title : '' }}</h6>
                                <p class="text-muted">{{ projectDetails ? projectDetails.description : '' }}</p>
                                
                                <div class="mb-3">
                                    <strong>Status:</strong>
                                    <span :class="'badge ms-2 bg-' + getStatusColor(projectDetails ? projectDetails.status : '')">
                                        {{ projectDetails ? projectDetails.status : '' }}
                                    </span>
                                </div>
                                
                                <div class="mb-3">
                                    <strong>Manager:</strong> {{ projectDetails ? projectDetails.project_manager : '' }}
                                </div>
                                
                                <div class="mb-3">
                                    <strong>Budget:</strong> {{ projectDetails ? projectDetails.budget_amount : '' }} {{ projectDetails ? projectDetails.currency : '' }}
                                </div>
                                
                                <div class="mb-3">
                                    <strong>Timeline:</strong> {{ formatDate(projectDetails ? projectDetails.start_date : '') }} to {{ formatDate(projectDetails ? projectDetails.end_date : '') }}
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Pending Approvals</h5>
                            </div>
                            <div class="card-body">
                                <div v-if="pendingRequests.length === 0" class="text-muted">
                                    No pending requests
                                </div>
                                <div v-else class="list-group">
                                    <div v-for="request in pendingRequests" :key="request.name" class="list-group-item">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ request.employee_name }}</h6>
                                            <small class="badge bg-warning">{{ request.request_type }}</small>
                                        </div>
                                        <p class="mb-1 text-muted">
                                            {{ formatDate(request.from_date) }} - {{ formatDate(request.to_date) }}
                                        </p>
                                        <small class="text-muted">{{ request.reason }}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `
    });
};