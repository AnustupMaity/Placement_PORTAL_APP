<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Manage Companies</h1>
        <p class="page-subtitle">Approve, reject, or blacklist companies.</p>
      </div>
    </div>

    <div class="ppa-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span>Registered Companies</span>
        <div class="input-group input-group-sm" style="max-width: 250px;">
          <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" placeholder="Search companies..." v-model="searchQuery">
        </div>
      </div>
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company & Industry</th>
              <th>Status</th>
              <th>Blacklisted</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="5" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td></tr>
            <tr v-else-if="filteredCompanies.length === 0"><td colspan="5" class="text-center py-4 text-muted">No companies found.</td></tr>
            <tr v-for="c in filteredCompanies" :key="c.id" v-else>
              <td>#{{ c.id }}</td>
              <td>
                <div class="fw-bold">{{ c.company_name }}</div>
                <div class="text-muted small" style="font-size: 0.8rem;">
                  <span v-if="c.industry"><i class="bi bi-briefcase me-1"></i>{{ c.industry }}</span>
                </div>
              </td>
              <td>
                <span :class="'status-badge badge-' + c.approval_status">{{ c.approval_status }}</span>
              </td>
              <td>
                <span v-if="c.is_blacklisted" class="badge bg-danger rounded-pill">Yes</span>
                <span v-else class="text-muted small">No</span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button @click="viewCompanyInfo(c)" class="btn btn-sm btn-outline-info" title="View Info">
                    <i class="bi bi-info-circle"></i> Info
                  </button>
                  <button v-if="c.approval_status === 'pending'" @click="updateStatus(c.id, 'approve')" class="btn btn-sm btn-outline-success" title="Approve">
                    <i class="bi bi-check-lg"></i>
                  </button>
                  <button v-if="c.approval_status === 'pending'" @click="updateStatus(c.id, 'reject')" class="btn btn-sm btn-outline-warning" title="Reject">
                    <i class="bi bi-x-lg"></i>
                  </button>
                  <button @click="toggleBlacklist(c.id)" class="btn btn-sm" :class="c.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'" :title="c.is_blacklisted ? 'Unblacklist' : 'Blacklist'">
                    <i class="bi bi-slash-circle"></i>
                  </button>
                  <button @click="deleteCompany(c.id)" class="btn btn-sm btn-outline-danger" title="Delete Company">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Company Info Modal -->
    <div class="modal fade" id="companyInfoModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedCompany?.company_name }} <span class="badge ms-2" :class="'badge-' + selectedCompany?.approval_status">{{ selectedCompany?.approval_status }}</span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedCompany">
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Company Details</h6>
                <p class="mb-1"><i class="bi bi-briefcase me-2"></i><strong>Industry:</strong> {{ selectedCompany.industry || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-geo-alt me-2"></i><strong>Location:</strong> {{ selectedCompany.location || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-link-45deg me-2"></i><strong>Website:</strong> <a v-if="selectedCompany.website" :href="selectedCompany.website" target="_blank">{{ selectedCompany.website }}</a><span v-else>N/A</span></p>
                <p class="mb-1 mt-3 text-muted" style="font-size: 0.9rem;">{{ selectedCompany.description }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Contact Details (HR)</h6>
                <p class="mb-1"><i class="bi bi-person me-2"></i><strong>Name:</strong> {{ selectedCompany.hr_name || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-envelope me-2"></i><strong>Email:</strong> {{ selectedCompany.hr_email || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-telephone me-2"></i><strong>Phone:</strong> {{ selectedCompany.hr_phone || 'N/A' }}</p>
              </div>
            </div>
            
            <h6 class="border-top pt-3 text-primary">Placement Drives Hosted</h6>
            <div v-if="loadingDrives" class="text-center py-3"><span class="ppa-spinner ppa-spinner-sm"></span></div>
            <div v-else-if="companyDrives.length === 0" class="text-muted small">No placement drives found for this company.</div>
            <div v-else class="list-group">
              <div v-for="d in companyDrives" :key="d.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-bold">{{ d.job_title }}</div>
                  <div class="small text-muted"><i class="bi bi-calendar me-1"></i> Deadline: {{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : 'N/A' }}</div>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <span class="badge" :class="d.status === 'approved' ? 'bg-success' : 'bg-secondary'">{{ d.status }}</span>
                  <button class="btn btn-sm btn-outline-info" @click="viewDriveInfo(d.id)">View Info</button>
                </div>
              </div>
            </div>
          </div>
        </div>
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
                  <p class="mb-1"><i class="bi bi-building me-2"></i><strong>Company:</strong> {{ driveCompany?.company_name || selectedCompany?.company_name || 'N/A' }}</p>
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

export default {
  name: 'AdminCompanies',
  setup() {
    const companies = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    
    const selectedCompany = ref(null);
    const companyDrives = ref([]);
    const loadingDrives = ref(false);
    let infoModal = null;
    
    // Drive modal state
    const selectedDrive = ref(null);
    const driveCompany = ref(null);
    const driveStats = ref(null);
    const driveApplications = ref([]);
    const loadingDetails = ref(false);
    let driveModalInstance = null;

    // Student modal state
    const selectedStudent = ref(null);
    const studentApplications = ref([]);
    const loadingStudentDetails = ref(false);
    let studentModalInstance = null;

    const { proxy } = getCurrentInstance();

    const loadCompanies = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/admin/companies');
        companies.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load companies.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const updateStatus = async (id, action) => {
      try {
        await axios.put(`/api/admin/companies/${id}/${action}`);
        proxy.$toast(`Company ${action}d successfully.`, 'success');
        loadCompanies();
      } catch (err) {
        proxy.$toast(`Failed to ${action} company.`, 'error');
      }
    };

    const toggleBlacklist = async (id) => {
      try {
        await axios.put(`/api/admin/companies/${id}/blacklist`);
        proxy.$toast('Blacklist status updated.', 'success');
        loadCompanies();
      } catch (err) {
        proxy.$toast('Failed to update blacklist.', 'error');
      }
    };

    const deleteCompany = async (id) => {
      if (!confirm('Are you sure you want to permanently remove this company?')) return;
      try {
        await axios.delete(`/api/admin/companies/${id}`);
        proxy.$toast('Company deleted successfully.', 'success');
        loadCompanies();
      } catch (err) {
        proxy.$toast('Failed to delete company.', 'error');
      }
    };

    const filteredCompanies = computed(() => {
      if (!searchQuery.value) return companies.value;
      const q = searchQuery.value.toLowerCase();
      return companies.value.filter(c => 
        (c.company_name && c.company_name.toLowerCase().includes(q)) ||
        (c.industry && c.industry.toLowerCase().includes(q)) ||
        (c.approval_status && c.approval_status.toLowerCase().includes(q))
      );
    });

    const viewCompanyInfo = async (company) => {
      selectedCompany.value = company;
      companyDrives.value = [];
      loadingDrives.value = true;
      if (infoModal) infoModal.show();
      
      try {
        const res = await axios.get('/api/admin/drives');
        companyDrives.value = res.data.filter(d => d.company_id === company.id);
      } catch (err) {
        proxy.$toast('Failed to load company drives.', 'error');
      } finally {
        loadingDrives.value = false;
      }
    };

    const viewDriveInfo = async (id) => {
      selectedDrive.value = null;
      driveCompany.value = null;
      driveStats.value = null;
      driveApplications.value = [];
      loadingDetails.value = true;
      
      if (!driveModalInstance && window.bootstrap) {
        driveModalInstance = new window.bootstrap.Modal(document.getElementById('driveInfoModal'));
      }
      if (driveModalInstance) driveModalInstance.show();

      try {
        const res = await axios.get(`/api/admin/drives/${id}/details`);
        selectedDrive.value = res.data.drive;
        driveCompany.value = res.data.company;
        driveStats.value = res.data.stats;
        driveApplications.value = res.data.applications;
      } catch (err) {
        proxy.$toast('Failed to load drive details.', 'error');
        if (driveModalInstance) driveModalInstance.hide();
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

    onMounted(() => {
      loadCompanies();
      if (window.bootstrap) {
        infoModal = new window.bootstrap.Modal(document.getElementById('companyInfoModal'));
        driveModalInstance = new window.bootstrap.Modal(document.getElementById('driveInfoModal'));
      }
    });

    return { 
      companies, 
      loading, 
      searchQuery,
      filteredCompanies,
      updateStatus, 
      toggleBlacklist, 
      deleteCompany,
      selectedCompany,
      companyDrives,
      loadingDrives,
      viewCompanyInfo,
      selectedDrive,
      driveCompany,
      driveStats,
      driveApplications,
      loadingDetails,
      viewDriveInfo,
      selectedStudent,
      studentApplications,
      loadingStudentDetails,
      viewStudentInfo
    };
  }
}
</script>
