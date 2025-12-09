frappe.pages['connections_dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Connections Dashboard',
        single_column: true
    });

    // Add refresh button
    page.set_primary_action(__('Refresh'), () => {
        load_dashboard(page);
    }, 'refresh');

    // Load dashboard
    load_dashboard(page);
};

function load_dashboard(page) {
    // Show loading
    $(page.body).html(`
        <div class="text-center" style="padding: 50px;">
            <div class="spinner-border text-primary" role="status">
                <span class="sr-only">Loading...</span>
            </div>
            <p class="mt-3">Loading dashboard...</p>
        </div>
    `);

    // Fetch data
    frappe.call({
        method: 'smart_pro.smart_pro.api.projects.get_connections_dashboard',
        callback: function(r) {
            if (r.message) {
                render_dashboard(page, r.message);
            }
        },
        error: function() {
            $(page.body).html(`
                <div class="text-center" style="padding: 50px;">
                    <i class="fa fa-exclamation-triangle text-warning" style="font-size: 48px;"></i>
                    <p class="mt-3">Error loading dashboard. Please try again.</p>
                </div>
            `);
        }
    });
}

function render_dashboard(page, data) {
    const html = `
        <div class="connections-dashboard" style="padding: 20px;">
            <!-- Workflow Banner -->
            <div class="workflow-banner" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0;">Smart Pro Workflow</h3>
                <p style="margin: 0; opacity: 0.9;">Project → Assignment → Date Request → Task → Timesheet</p>
            </div>

            <!-- Stats Cards Grid -->
            <div class="row">
                <!-- Smart Projects -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Smart Project" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #e3f2fd; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-folder-open" style="font-size: 24px; color: #1976d2;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Smart Projects</h4>
                                    <small class="text-muted">Main project container</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #1976d2;">${data.projects}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between" style="border-top: 1px solid #eee; padding-top: 10px;">
                                <span style="color: #4caf50;">${data.activeProjects} Active</span>
                                <span style="color: #2196f3;">${data.planningProjects} Planning</span>
                                <span style="color: #9e9e9e;">${data.completedProjects} Done</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Project Assignments -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Employee Project Assignment" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #f3e5f5; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-users" style="font-size: 24px; color: #9c27b0;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Assignments</h4>
                                    <small class="text-muted">Employee to project</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #9c27b0;">${data.assignments}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                            <div style="border-top: 1px solid #eee; padding-top: 10px; color: #666;">
                                <i class="fa fa-arrow-right"></i> Auto-creates Date Request on assignment
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Date Requests -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Employee Date Request" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #fff3e0; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-calendar" style="font-size: 24px; color: #ff9800;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Date Requests</h4>
                                    <small class="text-muted">Leave, WFH, Project dates</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #ff9800;">${data.dateRequests}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between" style="border-top: 1px solid #eee; padding-top: 10px;">
                                <span style="color: #ff9800;">${data.pendingRequests} Pending</span>
                                <span style="color: #4caf50;">${data.approvedRequests} Approved</span>
                                <span style="color: #f44336;">${data.rejectedRequests} Rejected</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Smart Tasks -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Smart Task" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #e8f5e9; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-check-circle" style="font-size: 24px; color: #4caf50;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Smart Tasks</h4>
                                    <small class="text-muted">Work items & assignments</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #4caf50;">${data.tasks}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between" style="border-top: 1px solid #eee; padding-top: 10px;">
                                <span style="color: #2196f3;">${data.openTasks} Open</span>
                                <span style="color: #ff9800;">${data.workingTasks} Working</span>
                                <span style="color: #4caf50;">${data.completedTasks} Done</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Time Sheets -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Smart Time Sheet" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #e0f2f1; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-clock-o" style="font-size: 24px; color: #009688;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Time Sheets</h4>
                                    <small class="text-muted">Work hour logging</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #009688;">${data.timesheets}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between" style="border-top: 1px solid #eee; padding-top: 10px;">
                                <span style="color: #2196f3;">${data.draftTimesheets} Draft</span>
                                <span style="color: #ff9800;">${data.submittedTimesheets} Submitted</span>
                                <span style="color: #4caf50;">${data.approvedTimesheets} Approved</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Notifications -->
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="card doctype-card" data-doctype="Smart Pro Notification" style="cursor: pointer; border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: #ffebee; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <i class="fa fa-bell" style="font-size: 24px; color: #f44336;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; font-weight: 600;">Notifications</h4>
                                    <small class="text-muted">System alerts & updates</small>
                                </div>
                                <div class="ml-auto text-right">
                                    <h2 style="margin: 0; color: #f44336;">${data.notifications}</h2>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Workflow Diagram -->
            <div class="card mt-4" style="border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div class="card-header" style="background: white; border-bottom: 1px solid #eee;">
                    <h5 style="margin: 0;">Document Flow</h5>
                </div>
                <div class="card-body">
                    <div class="workflow-diagram d-flex align-items-center justify-content-between flex-wrap" style="padding: 20px 0;">
                        <div class="workflow-step text-center">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: #e3f2fd; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                <i class="fa fa-folder-open" style="font-size: 24px; color: #1976d2;"></i>
                            </div>
                            <small class="d-block mt-2">Project</small>
                        </div>
                        <i class="fa fa-arrow-right text-muted"></i>
                        <div class="workflow-step text-center">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: #f3e5f5; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                <i class="fa fa-users" style="font-size: 24px; color: #9c27b0;"></i>
                            </div>
                            <small class="d-block mt-2">Assignment</small>
                        </div>
                        <i class="fa fa-arrow-right text-muted"></i>
                        <div class="workflow-step text-center">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: #fff3e0; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                <i class="fa fa-calendar" style="font-size: 24px; color: #ff9800;"></i>
                            </div>
                            <small class="d-block mt-2">Date Request</small>
                        </div>
                        <i class="fa fa-arrow-right text-muted"></i>
                        <div class="workflow-step text-center">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: #e8f5e9; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                <i class="fa fa-check-circle" style="font-size: 24px; color: #4caf50;"></i>
                            </div>
                            <small class="d-block mt-2">Task</small>
                        </div>
                        <i class="fa fa-arrow-right text-muted"></i>
                        <div class="workflow-step text-center">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: #e0f2f1; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                <i class="fa fa-clock-o" style="font-size: 24px; color: #009688;"></i>
                            </div>
                            <small class="d-block mt-2">Timesheet</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card mt-4" style="border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div class="card-header" style="background: white; border-bottom: 1px solid #eee;">
                    <h5 style="margin: 0;">Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3 col-sm-6 mb-2">
                            <button class="btn btn-primary btn-block quick-action" data-action="new-project">
                                <i class="fa fa-plus"></i> New Project
                            </button>
                        </div>
                        <div class="col-md-3 col-sm-6 mb-2">
                            <button class="btn btn-secondary btn-block quick-action" data-action="new-assignment">
                                <i class="fa fa-user-plus"></i> New Assignment
                            </button>
                        </div>
                        <div class="col-md-3 col-sm-6 mb-2">
                            <button class="btn btn-warning btn-block quick-action" data-action="new-date-request">
                                <i class="fa fa-calendar-plus-o"></i> Date Request
                            </button>
                        </div>
                        <div class="col-md-3 col-sm-6 mb-2">
                            <button class="btn btn-success btn-block quick-action" data-action="new-task">
                                <i class="fa fa-plus-circle"></i> New Task
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    $(page.body).html(html);

    // Add click handlers for doctype cards
    $(page.body).find('.doctype-card').on('click', function() {
        const doctype = $(this).data('doctype');
        frappe.set_route('List', doctype);
    });

    // Add hover effect
    $(page.body).find('.doctype-card').hover(
        function() {
            $(this).css('transform', 'translateY(-5px)');
            $(this).css('box-shadow', '0 5px 20px rgba(0,0,0,0.15)');
        },
        function() {
            $(this).css('transform', 'translateY(0)');
            $(this).css('box-shadow', '0 2px 10px rgba(0,0,0,0.1)');
        }
    );

    // Quick action handlers
    $(page.body).find('.quick-action').on('click', function() {
        const action = $(this).data('action');
        switch(action) {
            case 'new-project':
                frappe.new_doc('Smart Project');
                break;
            case 'new-assignment':
                frappe.new_doc('Employee Project Assignment');
                break;
            case 'new-date-request':
                frappe.new_doc('Employee Date Request');
                break;
            case 'new-task':
                frappe.new_doc('Smart Task');
                break;
        }
    });
}
