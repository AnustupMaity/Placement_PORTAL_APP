<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Manage Placement Drives</h1>
        <p class="page-subtitle">Review drives posted by companies</p>
      </div>
    </div>

    <div class="ppa-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span>Placement Drives</span>
        <div class="d-flex gap-2 align-items-center">
          <div class="dropdown">
            <button class="btn btn-sm btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-download me-1"></i> Export Data
            </button>
            <ul class="dropdown-menu shadow-sm">
              <li><h6 class="dropdown-header">Export Applications</h6></li>
              <li><button class="dropdown-item" @click="exportCSV('all')">Export All</button></li>
              <li><button class="dropdown-item" @click="exportCSV('selected')">Export Selected Only</button></li>
              <li><button class="dropdown-item" @click="exportCSV('shortlisted')">Export Shortlisted Only</button></li>
            </ul>
          </div>
          <select v-model="statusFilter" class="form-select form-select-sm" style="max-width: 150px;">
            <option value="all">All Drives</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
          <div class="input-group input-group-sm" style="max-width: 250px;">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control" placeholder="Search drives..." v-model="searchQuery">
          </div>
        </div>
      </div>
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="6" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td></tr>
            <tr v-else-if="filteredDrives.length === 0"><td colspan="6" class="text-center py-4 text-muted">No drives found.</td></tr>
            <tr v-for="d in filteredDrives" :key="d.id" v-else>
              <td>#{{ d.id }}</td>
              <td class="fw-medium">{{ d.company_name }}</td>
              <td class="fw-bold text-primary">{{ d.job_title }}</td>
              <td>{{ new Date(d.application_deadline).toLocaleDateString() }}</td>
              <td>
                <span :class="'status-badge badge-' + d.status">{{ d.status === 'approved' ? 'active' : d.status }}</span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-info" @click="viewDriveInfo(d.id)">
                    View Details
                  </button>
                  <button v-if="d.status === 'pending'" @click="updateStatus(d.id, 'approve')" class="btn btn-sm btn-outline-success" title="Approve">
                    <i class="bi bi-check-lg"></i>
                  </button>
                  <button v-if="d.status === 'pending'" @click="updateStatus(d.id, 'reject')" class="btn btn-sm btn-outline-warning" title="Reject">
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Drive Info Modal -->
    <div class="modal fade" id="driveInfoModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold">Drive Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body pt-3">
            <div v-if="loadingDetails" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <div v-else-if="selectedDrive">
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Company Info</h6>
                  <p class="mb-1"><i class="bi bi-building me-2"></i><strong>Company:</strong> {{ driveCompany.company_name || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-briefcase me-2"></i><strong>Job Title:</strong> {{ selectedDrive.job_title || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-geo-alt me-2"></i><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-currency-rupee me-2"></i><strong>Salary:</strong> {{ selectedDrive.salary || 'N/A' }}</p>
                </div>
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Requirements & Dates</h6>
                  <p class="mb-1"><i class="bi bi-calendar-x me-2"></i><strong>Deadline:</strong> {{ selectedDrive.application_deadline ? new Date(selectedDrive.application_deadline).toLocaleDateString() : 'N/A' }}</p>

                  <p class="mb-1"><i class="bi bi-award me-2"></i><strong>Min CGPA:</strong> {{ selectedDrive.min_cgpa || 'None' }}</p>
                  <p class="mb-1"><i class="bi bi-diagram-2 me-2"></i><strong>Branches:</strong> {{ selectedDrive.eligible_branches || 'All' }}</p>
                  <p class="mb-1"><i class="bi bi-calendar me-2"></i><strong>Batch:</strong> {{ selectedDrive.eligible_year || 'Any' }}</p>
                  <p class="mb-1"><i class="bi bi-info-circle me-2"></i><strong>Status:</strong> <span :class="'status-badge badge-' + selectedDrive.status" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;">{{ selectedDrive.status }}</span></p>
                </div>
              </div>

              <h6 class="border-top pt-3 text-primary mb-3">Application Statistics</h6>
              <div v-if="driveStats" class="row text-center mb-4 g-2">
                <div class="col-3">
                  <div class="border rounded p-2 bg-light">
                    <div class="fw-bold fs-5">{{ driveStats.total }}</div>
                    <div class="small text-muted">Applied</div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="border rounded p-2 bg-light">
                    <div class="fw-bold fs-5">{{ driveStats.shortlisted }}</div>
                    <div class="small text-muted">Shortlisted</div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="border rounded p-2 bg-light">
                    <div class="fw-bold fs-5">{{ driveStats.selected }}</div>
                    <div class="small text-muted">Selected</div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="border rounded p-2 bg-light">
                    <div class="fw-bold fs-5">{{ driveStats.rejected }}</div>
                    <div class="small text-muted">Rejected</div>
                  </div>
                </div>
              </div>

              <h6 class="border-top pt-3 text-primary mb-3">Applicants</h6>
              <div v-if="driveApplications.length === 0" class="text-muted small">No students have applied yet.</div>
              <div v-else class="list-group list-group-flush border rounded">
                <div v-for="app in driveApplications" :key="app.id" class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <div class="fw-medium">
                        {{ app.student_name }}
                        <button class="btn btn-sm btn-outline-info ms-2" style="padding: 0.1rem 0.4rem; font-size: 0.75rem;" @click="viewStudentInfo(app.student_id)">View Student Info</button>
                      </div>
                      <span class="text-muted small text-uppercase fw-bold">{{ app.status }}</span>
                    </div>
                  <div class="small text-muted">
                    <span class="me-3">Branch: {{ app.branch || 'N/A' }}</span>
                    <span>CGPA: {{ app.cgpa || 'N/A' }}</span>
                  </div>
                  <div v-if="app.placement" class="mt-2 p-2 bg-light rounded small">
                    <div class="fw-bold text-success mb-1">Placement Offer Received</div>
                    <div v-if="app.placement.salary">Package: {{ app.placement.salary }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Info Modal -->
    <div class="modal fade" id="studentInfoModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedStudent?.full_name }} 
              <span v-if="selectedStudent?.is_blacklisted" class="badge bg-danger ms-2">Blacklisted</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedStudent">
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Profile Details</h6>
                <p class="mb-1"><i class="bi bi-person-badge me-2"></i><strong>Roll No:</strong> {{ selectedStudent.roll_number || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-diagram-2 me-2"></i><strong>Branch:</strong> {{ selectedStudent.branch || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-calendar me-2"></i><strong>Grad Year:</strong> {{ selectedStudent.year || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-award me-2"></i><strong>CGPA:</strong> {{ selectedStudent.cgpa || 'N/A' }}</p>
                <p class="mb-1" v-if="selectedStudent.skills"><i class="bi bi-tools me-2"></i><strong>Skills:</strong> {{ selectedStudent.skills }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Contact Information</h6>
                <p class="mb-1"><i class="bi bi-envelope me-2"></i><strong>Email:</strong> {{ selectedStudent.email || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-telephone me-2"></i><strong>Phone:</strong> {{ selectedStudent.phone || 'N/A' }}</p>
                <p class="mb-1 mt-2" v-if="selectedStudent.resume_path">
                  <i class="bi bi-link-45deg me-2"></i><strong>Resume:</strong> 
                  <a :href="selectedStudent.resume_path" target="_blank" style="word-break: break-all;">
                    {{ selectedStudent.resume_path }}
                  </a>
                </p>
              </div>
            </div>
            
            <h6 class="border-top pt-3 text-primary">Application History</h6>
            <div v-if="loadingStudentDetails" class="text-center py-3"><span class="ppa-spinner ppa-spinner-sm"></span></div>
            <div v-else-if="studentApplications.length === 0" class="text-muted small">No applications found for this student.</div>
            <div v-else class="list-group">
              <div v-for="app in studentApplications" :key="app.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <div>
                    <div class="fw-bold">{{ app.drive_title }} <span class="text-muted fw-normal">at</span> {{ app.company_name }}</div>
                    <div class="small text-muted"><i class="bi bi-clock me-1"></i>Applied: {{ new Date(app.date_applied).toLocaleDateString() }}</div>
                  </div>
                  <span class="badge" :class="'badge-' + app.status">{{ app.status }}</span>
                </div>
                <div v-if="app.placement" class="mt-2 p-2 bg-light rounded small border border-success">
                  <div class="fw-medium text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i>Placement Offer Received</div>
                  <div><strong>Role:</strong> {{ app.placement.position || 'N/A' }}</div>
                  <div><strong>Package:</strong> <i class="bi bi-currency-rupee"></i>{{ app.placement.salary || 'N/A' }}</div>
                  <div><strong>Offer Date:</strong> {{ app.placement.created_at ? new Date(app.placement.created_at).toLocaleDateString() : 'N/A' }}</div>
                  <div class="mt-2">
                    <span class="badge" :class="app.placement.is_accepted ? 'bg-success' : 'bg-warning'">
                      {{ app.placement.is_accepted ? 'Student Accepted Offer' : 'Pending Acceptance' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance, computed } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'AdminDrives',
  setup() {
    const drives = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const statusFilter = ref('all');
    const exporting = ref(false);
    const { proxy } = getCurrentInstance();
    const route = useRoute();
    if (route.query.q) {
      searchQuery.value = route.query.q;
    }
    
    // Modal state
    const selectedDrive = ref(null);
    const driveCompany = ref(null);
    const driveStats = ref(null);
    const driveApplications = ref([]);
    const loadingDetails = ref(false);
    let modalInstance = null;

    // Student modal state
    const selectedStudent = ref(null);
    const studentApplications = ref([]);
    const loadingStudentDetails = ref(false);
    let studentModalInstance = null;

    const loadDrives = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/admin/drives');
        drives.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load drives.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const updateStatus = async (id, action) => {
      try {
        await axios.put(`/api/admin/drives/${id}/${action}`);
        proxy.$toast(`Drive ${action}d successfully.`, 'success');
        loadDrives();
      } catch (err) {
        proxy.$toast(`Failed to ${action} drive.`, 'error');
      }
    };

    const viewDriveInfo = async (id) => {
      selectedDrive.value = null;
      driveCompany.value = null;
      driveStats.value = null;
      driveApplications.value = [];
      loadingDetails.value = true;
      
      if (!modalInstance) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('driveInfoModal'));
      }
      modalInstance.show();

      try {
        const res = await axios.get(`/api/admin/drives/${id}/details`);
        selectedDrive.value = res.data.drive;
        driveCompany.value = res.data.company;
        driveStats.value = res.data.stats;
        driveApplications.value = res.data.applications;
      } catch (err) {
        proxy.$toast('Failed to load drive details.', 'error');
        modalInstance.hide();
      } finally {
        loadingDetails.value = false;
      }
    };

    const viewStudentInfo = async (id) => {
      loadingStudentDetails.value = true;
      selectedStudent.value = null;
      studentApplications.value = [];
      
      if (!studentModalInstance && window.bootstrap) {
        studentModalInstance = new window.bootstrap.Modal(document.getElementById('studentInfoModal'));
      }
      if (studentModalInstance) studentModalInstance.show();
      
      try {
        const res = await axios.get(`/api/admin/students/${id}/details`);
        selectedStudent.value = res.data.student;
        studentApplications.value = res.data.applications;
      } catch (err) {
        proxy.$toast('Failed to load student details.', 'error');
        if (studentModalInstance) studentModalInstance.hide();
      } finally {
        loadingStudentDetails.value = false;
      }
    };

    const filteredDrives = computed(() => {
      let result = drives.value;
      
      if (statusFilter.value === 'active') {
        result = result.filter(d => d.status === 'approved' || d.status === 'pending');
      } else if (statusFilter.value === 'closed') {
        result = result.filter(d => d.status === 'closed' || d.status === 'rejected' || d.status === 'cancelled');
      }

      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        result = result.filter(d => 
          (d.company_name && d.company_name.toLowerCase().includes(q)) ||
          (d.job_title && d.job_title.toLowerCase().includes(q)) ||
          (d.status && d.status.toLowerCase().includes(q))
        );
      }
      return result;
    });

    const exportCSV = async (status) => {
      exporting.value = true;
      try {
        const payload = status === 'all' ? {} : { status };
        const res = await axios.post('/api/export/admin/applications', payload);
        
        if (res.data.filename) {
          downloadFile(res.data.filename);
        } else if (res.data.task_id) {
          proxy.$toast(`Export (${status}) started. Processing...`, 'info');
          pollExportStatus(res.data.task_id);
        }
      } catch (err) {
        proxy.$toast('Failed to start export.', 'error');
        exporting.value = false;
      }
    };

    const pollExportStatus = (taskId) => {
      const interval = setInterval(async () => {
        try {
          const res = await axios.get(`/api/export/status/${taskId}`);
          if (res.data.status === 'SUCCESS') {
            clearInterval(interval);
            downloadFile(res.data.result);
          } else if (res.data.status === 'FAILURE') {
            clearInterval(interval);
            exporting.value = false;
            proxy.$toast('Export failed during processing.', 'error');
          }
        } catch (err) {
          clearInterval(interval);
          exporting.value = false;
          proxy.$toast('Error checking export status.', 'error');
        }
      }, 2000);
    };

    const downloadFile = async (filename) => {
      try {
        const response = await axios.get(`/api/export/download/${filename}`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        proxy.$toast('Export downloaded successfully.', 'success');
      } catch (err) {
        proxy.$toast('Failed to download the exported file.', 'error');
      } finally {
        exporting.value = false;
      }
    };

    onMounted(loadDrives);

    return { 
      drives, 
      loading, 
      searchQuery, 
      statusFilter,
      filteredDrives, 
      updateStatus, 
      viewDriveInfo,
      selectedDrive,
      driveCompany,
      driveStats,
      driveApplications,
      loadingDetails,
      selectedStudent,
      studentApplications,
      loadingStudentDetails,
      viewStudentInfo,
      exporting,
      exportCSV
    };
  }
}
</script>
