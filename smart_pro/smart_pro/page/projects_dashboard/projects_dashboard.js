frappe.pages['projects_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Projects Dashboard',
		single_column: true
	});

	// Store page reference
	wrapper.page = page;
	wrapper.dashboardData = {
		projects: [],
		tasks: [],
		pendingRequests: [],
		filters: {
			projectStatus: 'all',
			taskStatus: 'all',
			search: ''
		}
	};

	// Add refresh button
	page.set_primary_action(__('Refresh'), () => {
		loadDashboardData(wrapper);
	}, 'refresh');

	// Add custom CSS
	addCustomStyles();

	// Initial load
	loadDashboardData(wrapper);
};

frappe.pages['projects_dashboard'].refresh = function(wrapper) {
	loadDashboardData(wrapper);
};

function addCustomStyles() {
	if (document.getElementById('projects-dashboard-styles')) return;

	const styles = document.createElement('style');
	styles.id = 'projects-dashboard-styles';
	styles.textContent = `
		.smart-dashboard {
			padding: 0;
			background: #f8fafc;
			min-height: calc(100vh - 100px);
		}

		.smart-dashboard .stats-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
			gap: 1rem;
			margin-bottom: 1.5rem;
		}

		.smart-dashboard .stat-card {
			background: white;
			border-radius: 12px;
			padding: 1.25rem;
			box-shadow: 0 1px 3px rgba(0,0,0,0.08);
			transition: all 0.2s ease;
			border: 1px solid #e5e7eb;
			cursor: pointer;
		}

		.smart-dashboard .stat-card:hover {
			transform: translateY(-2px);
			box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		}

		.smart-dashboard .stat-card.active {
			border-color: var(--primary);
			background: linear-gradient(135deg, #f0f7ff 0%, #fff 100%);
		}

		.smart-dashboard .stat-icon {
			width: 48px;
			height: 48px;
			border-radius: 10px;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 1.5rem;
			margin-bottom: 0.75rem;
		}

		.smart-dashboard .stat-icon.blue { background: #dbeafe; color: #2563eb; }
		.smart-dashboard .stat-icon.green { background: #d1fae5; color: #059669; }
		.smart-dashboard .stat-icon.orange { background: #fed7aa; color: #ea580c; }
		.smart-dashboard .stat-icon.purple { background: #e9d5ff; color: #9333ea; }
		.smart-dashboard .stat-icon.red { background: #fecaca; color: #dc2626; }
		.smart-dashboard .stat-icon.teal { background: #ccfbf1; color: #0d9488; }

		.smart-dashboard .stat-value {
			font-size: 2rem;
			font-weight: 700;
			color: #1e293b;
			line-height: 1;
		}

		.smart-dashboard .stat-label {
			font-size: 0.875rem;
			color: #64748b;
			margin-top: 0.25rem;
		}

		.smart-dashboard .section-card {
			background: white;
			border-radius: 12px;
			box-shadow: 0 1px 3px rgba(0,0,0,0.08);
			border: 1px solid #e5e7eb;
			margin-bottom: 1.5rem;
			overflow: hidden;
		}

		.smart-dashboard .section-header {
			display: flex;
			align-items: center;
			justify-content: space-between;
			padding: 1rem 1.25rem;
			border-bottom: 1px solid #e5e7eb;
			background: #f9fafb;
		}

		.smart-dashboard .section-title {
			font-size: 1rem;
			font-weight: 600;
			color: #1e293b;
			display: flex;
			align-items: center;
			gap: 0.5rem;
		}

		.smart-dashboard .section-badge {
			background: var(--primary);
			color: white;
			padding: 0.125rem 0.5rem;
			border-radius: 100px;
			font-size: 0.75rem;
			font-weight: 600;
		}

		.smart-dashboard .filter-tabs {
			display: flex;
			gap: 0.5rem;
		}

		.smart-dashboard .filter-tab {
			padding: 0.375rem 0.75rem;
			border-radius: 6px;
			font-size: 0.75rem;
			font-weight: 500;
			cursor: pointer;
			transition: all 0.15s ease;
			border: 1px solid #e5e7eb;
			background: white;
			color: #64748b;
		}

		.smart-dashboard .filter-tab:hover {
			border-color: var(--primary);
			color: var(--primary);
		}

		.smart-dashboard .filter-tab.active {
			background: var(--primary);
			border-color: var(--primary);
			color: white;
		}

		.smart-dashboard .search-box {
			position: relative;
			margin-bottom: 1rem;
		}

		.smart-dashboard .search-box input {
			width: 100%;
			padding: 0.75rem 1rem 0.75rem 2.5rem;
			border: 1px solid #e5e7eb;
			border-radius: 8px;
			font-size: 0.875rem;
			transition: all 0.15s ease;
		}

		.smart-dashboard .search-box input:focus {
			outline: none;
			border-color: var(--primary);
			box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		}

		.smart-dashboard .search-box .search-icon {
			position: absolute;
			left: 0.875rem;
			top: 50%;
			transform: translateY(-50%);
			color: #9ca3af;
		}

		.smart-dashboard .project-card {
			padding: 1rem 1.25rem;
			border-bottom: 1px solid #f1f5f9;
			transition: background 0.15s ease;
			cursor: pointer;
		}

		.smart-dashboard .project-card:last-child {
			border-bottom: none;
		}

		.smart-dashboard .project-card:hover {
			background: #f8fafc;
		}

		.smart-dashboard .project-title {
			font-weight: 600;
			color: #1e293b;
			font-size: 0.9375rem;
			margin-bottom: 0.25rem;
		}

		.smart-dashboard .project-title:hover {
			color: var(--primary);
		}

		.smart-dashboard .project-meta {
			display: flex;
			align-items: center;
			gap: 1rem;
			font-size: 0.8125rem;
			color: #64748b;
		}

		.smart-dashboard .project-meta span {
			display: flex;
			align-items: center;
			gap: 0.25rem;
		}

		.smart-dashboard .status-pill {
			display: inline-flex;
			align-items: center;
			padding: 0.25rem 0.625rem;
			border-radius: 100px;
			font-size: 0.6875rem;
			font-weight: 600;
			text-transform: uppercase;
			letter-spacing: 0.025em;
		}

		.smart-dashboard .status-pill.active { background: #d1fae5; color: #059669; }
		.smart-dashboard .status-pill.planning { background: #dbeafe; color: #2563eb; }
		.smart-dashboard .status-pill.completed { background: #e5e7eb; color: #374151; }
		.smart-dashboard .status-pill.on-hold { background: #fed7aa; color: #ea580c; }
		.smart-dashboard .status-pill.cancelled { background: #fecaca; color: #dc2626; }
		.smart-dashboard .status-pill.open { background: #dbeafe; color: #2563eb; }
		.smart-dashboard .status-pill.working { background: #fef3c7; color: #d97706; }
		.smart-dashboard .status-pill.pending { background: #fef3c7; color: #d97706; }

		.smart-dashboard .task-card {
			padding: 1rem 1.25rem;
			border-bottom: 1px solid #f1f5f9;
			transition: background 0.15s ease;
		}

		.smart-dashboard .task-card:last-child {
			border-bottom: none;
		}

		.smart-dashboard .task-card:hover {
			background: #f8fafc;
		}

		.smart-dashboard .task-header {
			display: flex;
			justify-content: space-between;
			align-items: flex-start;
			margin-bottom: 0.5rem;
		}

		.smart-dashboard .task-title {
			font-weight: 600;
			color: #1e293b;
			font-size: 0.875rem;
		}

		.smart-dashboard .task-title a:hover {
			color: var(--primary);
		}

		.smart-dashboard .task-project {
			font-size: 0.75rem;
			color: #64748b;
			margin-bottom: 0.5rem;
		}

		.smart-dashboard .task-project strong {
			color: #475569;
		}

		.smart-dashboard .progress-wrapper {
			display: flex;
			align-items: center;
			gap: 0.75rem;
		}

		.smart-dashboard .progress-bar-container {
			flex: 1;
			height: 6px;
			background: #e5e7eb;
			border-radius: 100px;
			overflow: hidden;
		}

		.smart-dashboard .progress-bar-fill {
			height: 100%;
			border-radius: 100px;
			transition: width 0.3s ease;
		}

		.smart-dashboard .progress-bar-fill.low { background: #ef4444; }
		.smart-dashboard .progress-bar-fill.medium { background: #f59e0b; }
		.smart-dashboard .progress-bar-fill.high { background: #22c55e; }

		.smart-dashboard .progress-text {
			font-size: 0.75rem;
			font-weight: 600;
			color: #64748b;
			min-width: 40px;
		}

		.smart-dashboard .empty-state {
			text-align: center;
			padding: 3rem 1rem;
			color: #64748b;
		}

		.smart-dashboard .empty-state svg {
			width: 64px;
			height: 64px;
			margin-bottom: 1rem;
			opacity: 0.5;
		}

		.smart-dashboard .empty-state p {
			margin: 0;
			font-size: 0.875rem;
		}

		.smart-dashboard .approval-card {
			padding: 1rem 1.25rem;
			border-bottom: 1px solid #f1f5f9;
		}

		.smart-dashboard .approval-card:last-child {
			border-bottom: none;
		}

		.smart-dashboard .approval-header {
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 0.5rem;
		}

		.smart-dashboard .approval-employee {
			font-weight: 600;
			color: #1e293b;
			font-size: 0.875rem;
		}

		.smart-dashboard .approval-dates {
			font-size: 0.75rem;
			color: #64748b;
		}

		.smart-dashboard .approval-reason {
			font-size: 0.8125rem;
			color: #475569;
			margin-top: 0.5rem;
			padding: 0.5rem;
			background: #f8fafc;
			border-radius: 6px;
		}

		.smart-dashboard .quick-actions {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
			gap: 0.75rem;
			padding: 1rem 1.25rem;
		}

		.smart-dashboard .quick-action-btn {
			display: flex;
			align-items: center;
			justify-content: center;
			gap: 0.5rem;
			padding: 0.75rem 1rem;
			border-radius: 8px;
			font-size: 0.8125rem;
			font-weight: 500;
			cursor: pointer;
			transition: all 0.15s ease;
			border: 1px solid #e5e7eb;
			background: white;
			color: #374151;
		}

		.smart-dashboard .quick-action-btn:hover {
			border-color: var(--primary);
			color: var(--primary);
			background: #f0f7ff;
		}

		@media (max-width: 768px) {
			.smart-dashboard .stats-grid {
				grid-template-columns: repeat(2, 1fr);
			}
		}
	`;
	document.head.appendChild(styles);
}

function loadDashboardData(wrapper) {
	const $container = $(wrapper).find('.layout-main-section');

	// Show loading
	$container.html(`
		<div class="smart-dashboard">
			<div class="text-center p-5">
				<div class="spinner-border text-primary" role="status"></div>
				<p class="mt-3 text-muted">Loading dashboard...</p>
			</div>
		</div>
	`);

	// Fetch data
	Promise.all([
		frappe.call({ method: 'smart_pro.smart_pro.api.projects.get_user_projects' }),
		frappe.call({ method: 'smart_pro.smart_pro.api.projects.get_user_tasks' }),
		frappe.call({ method: 'smart_pro.smart_pro.api.projects.get_pending_date_requests' })
	]).then(([projectsRes, tasksRes, requestsRes]) => {
		wrapper.dashboardData.projects = projectsRes.message || [];
		wrapper.dashboardData.tasks = tasksRes.message || [];
		wrapper.dashboardData.pendingRequests = requestsRes.message || [];

		renderDashboard($container, wrapper);
	}).catch(err => {
		console.error('Error loading dashboard:', err);
		$container.html(`
			<div class="smart-dashboard">
				<div class="alert alert-danger m-4">
					<strong>Error loading dashboard:</strong> ${err.message || 'Unknown error'}
				</div>
			</div>
		`);
	});
}

function renderDashboard($container, wrapper) {
	const { projects, tasks, pendingRequests, filters } = wrapper.dashboardData;

	// Calculate stats
	const stats = {
		totalProjects: projects.length,
		activeProjects: projects.filter(p => p.status === 'Active').length,
		totalTasks: tasks.length,
		openTasks: tasks.filter(t => t.status === 'Open').length,
		workingTasks: tasks.filter(t => t.status === 'Working').length,
		completedTasks: tasks.filter(t => t.status === 'Completed').length,
		pendingApprovals: pendingRequests.length
	};

	const html = `
		<div class="smart-dashboard p-4">
			<!-- Stats Grid -->
			<div class="stats-grid">
				<div class="stat-card ${filters.projectStatus === 'all' ? 'active' : ''}" data-filter="project" data-value="all">
					<div class="stat-icon blue">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
					</div>
					<div class="stat-value">${stats.totalProjects}</div>
					<div class="stat-label">Total Projects</div>
				</div>
				<div class="stat-card ${filters.projectStatus === 'Active' ? 'active' : ''}" data-filter="project" data-value="Active">
					<div class="stat-icon green">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
					</div>
					<div class="stat-value">${stats.activeProjects}</div>
					<div class="stat-label">Active Projects</div>
				</div>
				<div class="stat-card ${filters.taskStatus === 'all' ? 'active' : ''}" data-filter="task" data-value="all">
					<div class="stat-icon purple">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
					</div>
					<div class="stat-value">${stats.totalTasks}</div>
					<div class="stat-label">Total Tasks</div>
				</div>
				<div class="stat-card ${filters.taskStatus === 'Open' ? 'active' : ''}" data-filter="task" data-value="Open">
					<div class="stat-icon orange">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
					</div>
					<div class="stat-value">${stats.openTasks}</div>
					<div class="stat-label">Open Tasks</div>
				</div>
				<div class="stat-card ${filters.taskStatus === 'Working' ? 'active' : ''}" data-filter="task" data-value="Working">
					<div class="stat-icon teal">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
					</div>
					<div class="stat-value">${stats.workingTasks}</div>
					<div class="stat-label">In Progress</div>
				</div>
				<div class="stat-card" data-filter="approval" data-value="pending">
					<div class="stat-icon red">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
					</div>
					<div class="stat-value">${stats.pendingApprovals}</div>
					<div class="stat-label">Pending Approvals</div>
				</div>
			</div>

			<div class="row">
				<!-- Left Column - Projects & Tasks -->
				<div class="col-lg-8">
					<!-- Search Box -->
					<div class="search-box">
						<svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
						<input type="text" id="dashboard-search" placeholder="Search projects, tasks..." value="${filters.search}">
					</div>

					<!-- Projects Section -->
					<div class="section-card">
						<div class="section-header">
							<div class="section-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
								Projects
								<span class="section-badge">${getFilteredProjects(projects, filters).length}</span>
							</div>
							<div class="filter-tabs">
								<span class="filter-tab ${filters.projectStatus === 'all' ? 'active' : ''}" data-filter="projectStatus" data-value="all">All</span>
								<span class="filter-tab ${filters.projectStatus === 'Active' ? 'active' : ''}" data-filter="projectStatus" data-value="Active">Active</span>
								<span class="filter-tab ${filters.projectStatus === 'Planning' ? 'active' : ''}" data-filter="projectStatus" data-value="Planning">Planning</span>
								<span class="filter-tab ${filters.projectStatus === 'Completed' ? 'active' : ''}" data-filter="projectStatus" data-value="Completed">Done</span>
							</div>
						</div>
						<div class="section-body" id="projects-list">
							${renderProjectsList(getFilteredProjects(projects, filters))}
						</div>
					</div>

					<!-- Tasks Section -->
					<div class="section-card">
						<div class="section-header">
							<div class="section-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
								Tasks
								<span class="section-badge">${getFilteredTasks(tasks, filters).length}</span>
							</div>
							<div class="filter-tabs">
								<span class="filter-tab ${filters.taskStatus === 'all' ? 'active' : ''}" data-filter="taskStatus" data-value="all">All</span>
								<span class="filter-tab ${filters.taskStatus === 'Open' ? 'active' : ''}" data-filter="taskStatus" data-value="Open">Open</span>
								<span class="filter-tab ${filters.taskStatus === 'Working' ? 'active' : ''}" data-filter="taskStatus" data-value="Working">Working</span>
								<span class="filter-tab ${filters.taskStatus === 'Completed' ? 'active' : ''}" data-filter="taskStatus" data-value="Completed">Done</span>
							</div>
						</div>
						<div class="section-body" id="tasks-list">
							${renderTasksList(getFilteredTasks(tasks, filters))}
						</div>
					</div>
				</div>

				<!-- Right Column -->
				<div class="col-lg-4">
					<!-- Quick Actions -->
					<div class="section-card">
						<div class="section-header">
							<div class="section-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
								Quick Actions
							</div>
						</div>
						<div class="quick-actions">
							<button class="quick-action-btn" onclick="frappe.new_doc('Smart Project')">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
								New Project
							</button>
							<button class="quick-action-btn" onclick="frappe.new_doc('Smart Task')">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
								New Task
							</button>
							<button class="quick-action-btn" onclick="frappe.set_route('List', 'Smart Project')">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
								All Projects
							</button>
							<button class="quick-action-btn" onclick="frappe.set_route('List', 'Smart Task')">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
								All Tasks
							</button>
						</div>
					</div>

					<!-- Pending Approvals -->
					<div class="section-card">
						<div class="section-header">
							<div class="section-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
								Pending Approvals
								<span class="section-badge">${pendingRequests.length}</span>
							</div>
						</div>
						<div class="section-body">
							${renderApprovalsList(pendingRequests)}
						</div>
					</div>
				</div>
			</div>
		</div>
	`;

	$container.html(html);

	// Attach event listeners
	attachEventListeners($container, wrapper);
}

function getFilteredProjects(projects, filters) {
	let filtered = projects;

	if (filters.projectStatus !== 'all') {
		filtered = filtered.filter(p => p.status === filters.projectStatus);
	}

	if (filters.search) {
		const search = filters.search.toLowerCase();
		filtered = filtered.filter(p =>
			(p.title || '').toLowerCase().includes(search) ||
			(p.name || '').toLowerCase().includes(search)
		);
	}

	return filtered;
}

function getFilteredTasks(tasks, filters) {
	let filtered = tasks;

	if (filters.taskStatus !== 'all') {
		filtered = filtered.filter(t => t.status === filters.taskStatus);
	}

	if (filters.search) {
		const search = filters.search.toLowerCase();
		filtered = filtered.filter(t =>
			(t.title || '').toLowerCase().includes(search) ||
			(t.name || '').toLowerCase().includes(search) ||
			(t.project || '').toLowerCase().includes(search)
		);
	}

	return filtered;
}

function renderProjectsList(projects) {
	if (projects.length === 0) {
		return `
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
				<p>No projects found</p>
			</div>
		`;
	}

	return projects.map(project => `
		<div class="project-card" onclick="frappe.set_route('Form', 'Smart Project', '${encodeURIComponent(project.name)}')">
			<div class="d-flex justify-content-between align-items-start">
				<div>
					<div class="project-title">${frappe.utils.escape_html(project.title || project.name)}</div>
					<div class="project-meta">
						<span>
							<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
							${formatDate(project.start_date)} - ${formatDate(project.end_date)}
						</span>
						${project.project_manager ? `
							<span>
								<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
								${frappe.utils.escape_html(project.project_manager)}
							</span>
						` : ''}
					</div>
				</div>
				<span class="status-pill ${getStatusClassCss(project.status)}">${frappe.utils.escape_html(project.status || 'Unknown')}</span>
			</div>
		</div>
	`).join('');
}

function renderTasksList(tasks) {
	if (tasks.length === 0) {
		return `
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
				<p>No tasks found</p>
			</div>
		`;
	}

	return tasks.map(task => {
		const progress = task.progress || 0;
		const progressClass = progress < 30 ? 'low' : progress < 70 ? 'medium' : 'high';

		return `
			<div class="task-card">
				<div class="task-header">
					<div class="task-title">
						<a href="/app/smart-task/${encodeURIComponent(task.name)}">${frappe.utils.escape_html(task.title || task.name)}</a>
					</div>
					<span class="status-pill ${getStatusClassCss(task.status)}">${frappe.utils.escape_html(task.status || 'Unknown')}</span>
				</div>
				<div class="task-project">
					Project: <strong>${frappe.utils.escape_html(task.project || '-')}</strong> | Due: ${formatDate(task.due_date)}
				</div>
				<div class="progress-wrapper">
					<div class="progress-bar-container">
						<div class="progress-bar-fill ${progressClass}" style="width: ${progress}%"></div>
					</div>
					<span class="progress-text">${progress}%</span>
				</div>
			</div>
		`;
	}).join('');
}

function renderApprovalsList(requests) {
	if (requests.length === 0) {
		return `
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
				<p>No pending approvals</p>
			</div>
		`;
	}

	return requests.map(request => `
		<div class="approval-card">
			<div class="approval-header">
				<span class="approval-employee">${frappe.utils.escape_html(request.employee_name || request.employee)}</span>
				<span class="status-pill pending">${frappe.utils.escape_html(request.request_type || 'Request')}</span>
			</div>
			<div class="approval-dates">
				<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
				${formatDate(request.from_date)} - ${formatDate(request.to_date)}
			</div>
			${request.reason ? `<div class="approval-reason">${frappe.utils.escape_html(request.reason)}</div>` : ''}
		</div>
	`).join('');
}

function attachEventListeners($container, wrapper) {
	// Filter tabs
	$container.on('click', '.filter-tab', function() {
		const filterType = $(this).data('filter');
		const filterValue = $(this).data('value');

		wrapper.dashboardData.filters[filterType] = filterValue;
		renderDashboard($container, wrapper);
	});

	// Stat cards as filters
	$container.on('click', '.stat-card[data-filter="project"]', function() {
		wrapper.dashboardData.filters.projectStatus = $(this).data('value');
		renderDashboard($container, wrapper);
	});

	$container.on('click', '.stat-card[data-filter="task"]', function() {
		wrapper.dashboardData.filters.taskStatus = $(this).data('value');
		renderDashboard($container, wrapper);
	});

	// Search
	let searchTimeout;
	$container.on('input', '#dashboard-search', function() {
		clearTimeout(searchTimeout);
		const searchValue = $(this).val();

		searchTimeout = setTimeout(() => {
			wrapper.dashboardData.filters.search = searchValue;
			// Update lists without full re-render
			$('#projects-list').html(renderProjectsList(getFilteredProjects(wrapper.dashboardData.projects, wrapper.dashboardData.filters)));
			$('#tasks-list').html(renderTasksList(getFilteredTasks(wrapper.dashboardData.tasks, wrapper.dashboardData.filters)));
		}, 300);
	});
}

function formatDate(dateString) {
	if (!dateString) return '-';
	return frappe.datetime.str_to_user(dateString);
}

function getStatusClassCss(status) {
	const statusMap = {
		'Active': 'active',
		'Planning': 'planning',
		'Completed': 'completed',
		'Cancelled': 'cancelled',
		'On Hold': 'on-hold',
		'Open': 'open',
		'Working': 'working',
		'Pending Review': 'pending',
		'Pending Approval': 'pending'
	};
	return statusMap[status] || '';
}
