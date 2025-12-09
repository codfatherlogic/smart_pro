// Mobile-optimized dashboard for Smart Pro PWA
frappe.pages['mobile_dashboard'] = {
    onload: function(wrapper) {
        const { __, frappe, frappeui } = window;
        
        // Create a new Vue app
        const app = new Vue({
            el: wrapper,
            data() {
                return {
                    activeTab: 'projects',
                    projects: [],
                    tasks: [],
                    pendingRequests: [],
                    loading: true,
                    offline: !navigator.onLine,
                    showInstallPrompt: false,
                    deferredPrompt: null
                };
            },
            mounted() {
                this.loadData();
                this.setupPWA();
                this.setupOfflineDetection();
                
                // Listen for beforeinstallprompt event
                window.addEventListener('beforeinstallprompt', (e) => {
                    e.preventDefault();
                    this.deferredPrompt = e;
                    this.showInstallPrompt = true;
                });
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
                        if (this.offline) {
                            // Try to load from local storage
                            this.loadFromCache();
                        } else {
                            frappe.msgprint(__('Error loading data: ') + error.message);
                        }
                    } finally {
                        this.loading = false;
                    }
                },
                
                loadFromCache() {
                    // Load cached data from localStorage
                    const cachedProjects = localStorage.getItem('smart_pro_projects');
                    const cachedTasks = localStorage.getItem('smart_pro_tasks');
                    
                    if (cachedProjects) this.projects = JSON.parse(cachedProjects);
                    if (cachedTasks) this.tasks = JSON.parse(cachedTasks);
                },
                
                setupPWA() {
                    // Register service worker
                    if ('serviceWorker' in navigator) {
                        navigator.serviceWorker.register('/assets/smart_pro/sw.js')
                            .then(registration => {
                                console.log('Service Worker registered with scope:', registration.scope);
                            })
                            .catch(error => {
                                console.error('Service Worker registration failed:', error);
                            });
                    }
                },
                
                setupOfflineDetection() {
                    window.addEventListener('online', () => {
                        this.offline = false;
                        this.loadData(); // Refresh data when back online
                    });
                    
                    window.addEventListener('offline', () => {
                        this.offline = true;
                    });
                },
                
                async installPWA() {
                    if (this.deferredPrompt) {
                        this.deferredPrompt.prompt();
                        const { outcome } = await this.deferredPrompt.userChoice;
                        console.log(`User response to the install prompt: ${outcome}`);
                        this.deferredPrompt = null;
                        this.showInstallPrompt = false;
                    }
                },
                
                formatDate(dateString) {
                    if (!dateString) return '';
                    return frappe.datetime.str_to_user(dateString);
                },
                
                getStatusColor(status) {
                    const colors = {
                        'Active': 'success',
                        'Planning': 'primary',
                        'Completed': 'secondary',
                        'Cancelled': 'danger',
                        'On Hold': 'warning',
                        'Open': 'primary',
                        'Working': 'warning',
                        'Pending Review': 'info',
                        'Pending Approval': 'warning',
                        'Approved': 'success',
                        'Rejected': 'danger'
                    };
                    return colors[status] || 'secondary';
                },
                
                switchTab(tab) {
                    this.activeTab = tab;
                },
                
                createNewProject() {
                    frappe.new_doc('Smart Project');
                },
                
                createNewTask() {
                    frappe.new_doc('Smart Task');
                },
                
                createNewRequest() {
                    frappe.new_doc('Employee Date Request');
                }
            },
            template: `
                <div class="mobile-container">
                    <!-- Install Prompt -->
                    <div v-if="showInstallPrompt" class="install-prompt alert alert-info d-flex align-items-center justify-content-between">
                        <span>Install Smart Pro for better experience</span>
                        <button @click="installPWA" class="btn btn-sm btn-primary">Install</button>
                    </div>
                    
                    <!-- Offline Indicator -->
                    <div v-if="offline" class="offline-indicator alert alert-warning text-center">
                        <i class="fa fa-wifi-slash"></i> You are offline
                    </div>
                    
                    <!-- Header -->
                    <div class="mobile-header">
                        <h1 class="app-title">Smart Pro</h1>
                        <div class="user-actions">
                            <button class="btn btn-sm btn-outline-primary" @click="loadData">
                                <i class="fa fa-refresh"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Tabs -->
                    <div class="mobile-tabs">
                        <button 
                            @click="switchTab('projects')" 
                            :class="['tab-btn', { active: activeTab === 'projects' }]">
                            <i class="fa fa-project-diagram"></i>
                            <span>Projects</span>
                        </button>
                        <button 
                            @click="switchTab('tasks')" 
                            :class="['tab-btn', { active: activeTab === 'tasks' }]">
                            <i class="fa fa-tasks"></i>
                            <span>Tasks</span>
                        </button>
                        <button 
                            @click="switchTab('requests')" 
                            :class="['tab-btn', { active: activeTab === 'requests' }]">
                            <i class="fa fa-calendar-check"></i>
                            <span>Requests</span>
                        </button>
                    </div>
                    
                    <!-- Loading State -->
                    <div v-if="loading" class="loading-state text-center p-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                    
                    <!-- Projects Tab -->
                    <div v-else-if="activeTab === 'projects'" class="tab-content">
                        <div class="section-header">
                            <h5>My Projects</h5>
                            <button @click="createNewProject" class="btn btn-sm btn-primary">
                                <i class="fa fa-plus"></i> New
                            </button>
                        </div>
                        
                        <div v-if="projects.length === 0" class="empty-state">
                            <i class="fa fa-project-diagram fa-3x text-muted"></i>
                            <p>No projects found</p>
                        </div>
                        
                        <div v-else class="project-list">
                            <div v-for="project in projects" :key="project.name" class="project-card">
                                <div class="project-header">
                                    <h6>{{ project.title }}</h6>
                                    <span :class="'badge bg-' + getStatusColor(project.status)">
                                        {{ project.status }}
                                    </span>
                                </div>
                                <div class="project-details">
                                    <div class="detail-item">
                                        <i class="fa fa-calendar"></i>
                                        <span>{{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) }}</span>
                                    </div>
                                    <div v-if="project.budget_amount" class="detail-item">
                                        <i class="fa fa-money-bill"></i>
                                        <span>Budget: {{ project.budget_amount }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tasks Tab -->
                    <div v-else-if="activeTab === 'tasks'" class="tab-content">
                        <div class="section-header">
                            <h5>My Tasks</h5>
                            <button @click="createNewTask" class="btn btn-sm btn-primary">
                                <i class="fa fa-plus"></i> New
                            </button>
                        </div>
                        
                        <div v-if="tasks.length === 0" class="empty-state">
                            <i class="fa fa-tasks fa-3x text-muted"></i>
                            <p>No tasks assigned</p>
                        </div>
                        
                        <div v-else class="task-list">
                            <div v-for="task in tasks" :key="task.name" class="task-card">
                                <div class="task-header">
                                    <h6>{{ task.title }}</h6>
                                    <span :class="'badge bg-' + getStatusColor(task.status)">
                                        {{ task.status }}
                                    </span>
                                </div>
                                <div class="task-details">
                                    <div class="detail-item">
                                        <i class="fa fa-project-diagram"></i>
                                        <span>{{ task.project }}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fa fa-calendar"></i>
                                        <span>Due: {{ formatDate(task.due_date) }}</span>
                                    </div>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-label">
                                        <span>Progress: {{ task.progress }}%</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar" :style="{ width: task.progress + '%' }"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Requests Tab -->
                    <div v-else-if="activeTab === 'requests'" class="tab-content">
                        <div class="section-header">
                            <h5>Pending Requests</h5>
                            <button @click="createNewRequest" class="btn btn-sm btn-primary">
                                <i class="fa fa-plus"></i> New
                            </button>
                        </div>
                        
                        <div v-if="pendingRequests.length === 0" class="empty-state">
                            <i class="fa fa-calendar-check fa-3x text-muted"></i>
                            <p>No pending requests</p>
                        </div>
                        
                        <div v-else class="request-list">
                            <div v-for="request in pendingRequests" :key="request.name" class="request-card">
                                <div class="request-header">
                                    <h6>{{ request.employee_name }}</h6>
                                    <span class="badge bg-warning">{{ request.request_type }}</span>
                                </div>
                                <div class="request-details">
                                    <div class="detail-item">
                                        <i class="fa fa-calendar"></i>
                                        <span>{{ formatDate(request.from_date) }} - {{ formatDate(request.to_date) }}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fa fa-comment"></i>
                                        <span class="request-reason">{{ request.reason }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `
        });
    }
};