<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Drive Applications</h1>
        <p class="page-subtitle">Review applications for this drive</p>
      </div>
      <div class="d-flex align-items-center gap-3">
        <select class="form-select form-select-sm" v-model="statusFilter" style="width: auto;">
          <option value="">All Statuses</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview">Interview</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
        </select>
        <input type="text" class="form-control form-control-sm" placeholder="Search applicant..." v-model="searchQuery" style="width: 230px;">
        <router-link to="/company/drives" class="btn btn-outline-secondary btn-sm text-nowrap">Back to Drives</router-link>
      </div>
    </div>

    <!-- Bulk Actions Toolbar -->
    <div v-if="selectedApplicants.length > 0" class="alert alert-primary d-flex align-items-center justify-content-between p-2 mb-3 shadow-sm border-primary border-opacity-25" style="background-color: #f0f7ff;">
      <div>
        <span class="badge bg-primary rounded-pill me-2">{{ selectedApplicants.length }}</span> 
        <span class="fw-medium text-primary">Applicants Selected</span>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-success bg-white fw-medium" @click="openBulkStatusModal('shortlisted')">Shortlist Selected</button>
        <button class="btn btn-sm btn-outline-danger bg-white fw-medium" @click="openBulkStatusModal('rejected')">Reject Selected</button>
        <button class="btn btn-sm btn-outline-primary bg-white fw-medium" @click="openTestLinkModal">Send Test Link</button>
        <button class="btn btn-sm btn-outline-info bg-white fw-medium" @click="openInterviewModal">Schedule Interview</button>
      </div>
    </div>

    <div class="ppa-card">
      <div class="card-header">Applicants</div>
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0 align-middle">
          <thead>
            <tr>
              <th style="width: 40px;">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" :checked="isAllSelected" @change="toggleSelectAll">
                </div>
              </th>
              <th>Applicant Name</th>
              <th v-if="isGeneralView">Drive</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Date Applied</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td></tr>
            <tr v-else-if="filteredApplications.length === 0"><td colspan="7" class="text-center py-4 text-muted">No applications found.</td></tr>
            <tr v-for="app in filteredApplications" :key="app.id" v-else>
              <td>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" :value="app.id" v-model="selectedApplicants">
                </div>
              </td>
              <td class="fw-medium">{{ app.full_name }}</td>
              <td v-if="isGeneralView">{{ app.drive_title }}</td>
              <td>{{ app.branch || '-' }}</td>
              <td>{{ app.cgpa ? app.cgpa.toFixed(2) : '-' }}</td>
              <td>{{ formatDate(app.application_date) }}</td>
              <td>
                <span :class="'status-badge badge-' + app.status">{{ app.status }}</span>
              </td>
              <td>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                  <button @click="reviewStudent(app)" class="btn btn-sm btn-outline-info text-nowrap">
                    Review Student
                  </button>
                  <select 
                    class="form-select form-select-sm border-primary text-primary fw-medium" 
                    style="width: 140px; cursor: pointer;" 
                    :value="app.status" 
                    @change="openStatusModal(app, $event.target.value)"
                    :disabled="app.status === 'selected' || app.status === 'rejected'"
                  >
                    <option value="applied" disabled>Update Status...</option>
                    <option value="shortlisted">Shortlist</option>
                    <option value="interview">Interview</option>
                    <option value="selected">Select</option>
                    <option value="rejected">Reject</option>
                  </select>
                  <a v-if="isGeneralView" :href="`/company/drives/${app.drive_id}/applications`" class="btn btn-sm btn-outline-secondary text-nowrap">
                    View Drive Details
                  </a>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Review Student Modal -->
    <div class="modal fade" id="reviewStudentModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title fw-bold mb-0">Review Applicant: {{ selectedApp?.full_name }}</h5>
              <div class="text-muted small mt-1" v-if="selectedApp?.drive_title">
                Applying for: <strong class="text-dark">{{ selectedApp.drive_title }}</strong>
              </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedApp">
            <div class="row g-4">
              <div class="col-12">
                <h6 class="fw-bold text-primary mb-3">Applicant Details</h6>
                <table class="table table-sm table-borderless mb-0" style="table-layout: fixed;">
                  <tbody>
                    <tr><td class="text-muted" style="width: 150px;">Name</td><td class="fw-medium">{{ selectedApp.full_name }}</td></tr>
                    <tr><td class="text-muted">Branch</td><td>{{ selectedApp.branch || '—' }}</td></tr>
                    <tr><td class="text-muted">Batch</td><td>{{ selectedApp.year || '—' }}</td></tr>
                    <tr><td class="text-muted">CGPA</td><td>{{ selectedApp.cgpa ? selectedApp.cgpa.toFixed(2) : '—' }}</td></tr>
                    <tr><td class="text-muted">Phone</td><td>{{ selectedApp.phone || '—' }}</td></tr>
                    <tr><td class="text-muted">Skills</td><td>{{ selectedApp.skills || '—' }}</td></tr>
                    <tr>
                      <td class="text-muted align-middle">Resume</td>
                      <td>
                        <a v-if="selectedApp.resume_path" :href="selectedApp.resume_path" target="_blank" style="word-break: break-all;" class="text-primary text-decoration-none">
                          {{ selectedApp.resume_path }}
                        </a>
                        <span v-else class="text-muted small">No resume provided</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="col-12 border-top pt-3">
                <h6 class="fw-bold text-primary mb-3">Previous Applications to Company</h6>
                <div v-if="loadingStudentApps" class="text-center py-4">
                  <span class="ppa-spinner ppa-spinner-sm"></span>
                </div>
                <div v-else-if="studentPastApps.length === 0" class="alert alert-secondary small mb-0">
                  No previous applications found for this student.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-sm mb-0 small">
                    <thead>
                      <tr>
                        <th>Drive Role</th>
                        <th>Applied Date</th>
                        <th>Status</th>
                        <th>Status Date</th>
                        <th>Acceptance</th>
                        <th>Feedback</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="pastApp in studentPastApps" :key="pastApp.id">
                        <td class="fw-medium">{{ pastApp.drive_title }}</td>
                        <td class="text-muted">{{ formatDate(pastApp.application_date) }}</td>
                        <td><span :class="'status-badge badge-' + pastApp.status" style="font-size: 0.65rem;">{{ pastApp.status }}</span></td>
                        <td class="text-muted">{{ formatDate(pastApp.status_date) }}</td>
                        <td>
                          <span v-if="pastApp.student_acceptance" :class="'badge bg-' + (pastApp.student_acceptance === 'Accepted' ? 'success' : 'warning')">{{ pastApp.student_acceptance }}</span>
                          <span v-else>—</span>
                        </td>
                        <td>
                          <span v-if="pastApp.feedback" class="text-muted d-inline-block text-truncate" style="max-width: 150px;" :title="pastApp.feedback">{{ pastApp.feedback }}</span>
                          <span v-else>—</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
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

    <!-- Status Feedback Modal -->
    <div class="modal fade" id="statusFeedbackModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title fw-bold mb-0">Update Application Status</h5>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="statusUpdateApp">
            <div class="mb-3">
              <p>Updating status for <strong>{{ statusUpdateApp.full_name }}</strong> to <strong class="text-primary text-uppercase">{{ newStatus }}</strong></p>
              
              <div v-if="newStatus === 'selected'" class="alert alert-success small mb-3">
                <i class="bi bi-info-circle-fill me-1"></i> Selecting this candidate creates an official <strong>Placement Offer</strong>. If you have configured an Authorized Signatory Signature in your Company Profile, it will automatically be affixed to their Offer Letter.
              </div>

              <div v-if="newStatus === 'interview'" class="mb-3 border p-3 rounded bg-white">
                <h6 class="fw-bold text-primary mb-2"><i class="bi bi-calendar-event me-2"></i>Schedule Interview</h6>
                <div class="mb-2">
                  <label class="form-label text-muted small mb-1">Interview Date & Time</label>
                  <input type="datetime-local" class="form-control form-control-sm" v-model="statusInterviewDate">
                </div>
                <div>
                  <label class="form-label text-muted small mb-1">Meeting Link (e.g., Google Meet, Zoom)</label>
                  <input type="url" class="form-control form-control-sm" v-model="statusInterviewLink" placeholder="https://...">
                </div>
                <div class="small text-muted mt-2"><i class="bi bi-envelope me-1"></i>An invite email will be sent automatically.</div>
              </div>

              <div v-if="newStatus === 'test_invited'" class="mb-3 border p-3 rounded bg-white">
                <h6 class="fw-bold text-primary mb-2"><i class="bi bi-link-45deg me-2"></i>Send Test Link</h6>
                <div class="mb-2">
                  <label class="form-label text-muted small mb-1">Test Deadline / Scheduled Time</label>
                  <input type="datetime-local" class="form-control form-control-sm" v-model="statusTestDate">
                </div>
                <div>
                  <label class="form-label text-muted small mb-1">Test URL</label>
                  <input type="url" class="form-control form-control-sm" v-model="statusTestLink" placeholder="https://...">
                </div>
                <div class="small text-muted mt-2"><i class="bi bi-envelope me-1"></i>An invite email will be sent automatically.</div>
              </div>

              <label class="form-label text-muted">Feedback / Message to Candidate (Optional)</label>
              <textarea class="form-control" v-model="statusFeedback" rows="3" placeholder="Enter message here..."></textarea>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal" @click="loadApps">Cancel</button>
            <button type="button" class="btn btn-primary btn-sm" @click="confirmUpdateStatus" :disabled="isUpdatingStatus">
              <span v-if="isUpdatingStatus" class="spinner-border spinner-border-sm me-2"></span>
              Save Status
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'CompanyApplications',
  setup() {
    const route = useRoute();
    const applications = ref([]);
    const searchQuery = ref('');
    const statusFilter = ref('');
    const loading = ref(true);
    const selectedApp = ref(null);
    const studentPastApps = ref([]);
    const loadingStudentApps = ref(false);
    
    // Bulk Selection State
    const selectedApplicants = ref([]);
    const isAllSelected = computed(() => {
      return filteredApplications.value.length > 0 && 
             selectedApplicants.value.length === filteredApplications.value.length;
    });

    const toggleSelectAll = (e) => {
      if (e.target.checked) {
        selectedApplicants.value = filteredApplications.value.map(a => a.id);
      } else {
        selectedApplicants.value = [];
      }
    };
    
    // Status Modal State
    let statusModalInstance = null;
    const statusUpdateApp = ref(null);
    const newStatus = ref('');
    const statusFeedback = ref('');
    const statusInterviewDate = ref('');
    const statusInterviewLink = ref('');
    const statusTestDate = ref('');
    const statusTestLink = ref('');
    const isUpdatingStatus = ref(false);
    let modalInstance = null;
    
    const { proxy } = getCurrentInstance();

    const loadApps = async () => {
      loading.value = true;
      try {
        const endpoint = route.params.id 
          ? `/api/company/drives/${route.params.id}/applications`
          : '/api/company/applications';
        const res = await axios.get(endpoint);
        applications.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load applications.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const isGeneralView = !route.params.id;

    const formatDate = (dateString) => {
      if (!dateString) return '—';
      let ds = dateString;
      if (!ds.endsWith('Z') && !ds.includes('+')) ds += 'Z';
      const d = new Date(ds);
      if (isNaN(d)) return '—';
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const filteredApplications = computed(() => {
      const q = searchQuery.value.toLowerCase();
      let filtered = applications.value;
      if (statusFilter.value) {
        filtered = filtered.filter(a => a.status === statusFilter.value);
      }
      if (q) {
        filtered = filtered.filter(a => 
          (a.full_name && a.full_name.toLowerCase().includes(q)) ||
          (a.branch && a.branch.toLowerCase().includes(q))
        );
      }
      return filtered;
    });

    const openStatusModal = (app, status) => {
      statusUpdateApp.value = app;
      newStatus.value = status;
      statusFeedback.value = app.feedback || '';
      
      // Reset fields
      statusInterviewDate.value = '';
      statusInterviewLink.value = '';
      statusTestDate.value = '';
      statusTestLink.value = '';
      
      if (!statusModalInstance && window.bootstrap) {
        statusModalInstance = new window.bootstrap.Modal(document.getElementById('statusFeedbackModal'));
      }
      if (statusModalInstance) statusModalInstance.show();
    };

    const confirmUpdateStatus = async () => {
      if (!statusUpdateApp.value) return;
      isUpdatingStatus.value = true;
      let payload = { 
        status: newStatus.value, 
        feedback: statusFeedback.value,
        custom_message: statusFeedback.value
      };

      if (newStatus.value === 'interview') {
         if (statusInterviewDate.value) payload.interview_scheduled = new Date(statusInterviewDate.value).toISOString();
         payload.interview_link = statusInterviewLink.value;
      }
      if (newStatus.value === 'test_invited') {
         if (statusTestDate.value) payload.test_scheduled = new Date(statusTestDate.value).toISOString();
         payload.test_link = statusTestLink.value;
      }

      try {
        await axios.put(`/api/company/applications/${statusUpdateApp.value.id}/status`, payload);
        proxy.$toast(`Application marked as ${newStatus.value}.`, 'success');
        if (statusModalInstance) statusModalInstance.hide();
        loadApps();
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to update status.', 'error');
        loadApps();
      } finally {
        isUpdatingStatus.value = false;
      }
    };

    const reviewStudent = async (app) => {
      selectedApp.value = app;
      studentPastApps.value = [];
      loadingStudentApps.value = true;

      if (!modalInstance && window.bootstrap) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('reviewStudentModal'));
      }
      if (modalInstance) modalInstance.show();

      try {
        const res = await axios.get(`/api/company/students/${app.student_id}/applications`);
        studentPastApps.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load student history.', 'error');
      } finally {
        loadingStudentApps.value = false;
      }
    };

    onMounted(loadApps);

    };

    const openBulkStatusModal = async (status) => {
      if (!selectedApplicants.value.length) return;
      let msg = `Are you sure you want to mark ${selectedApplicants.value.length} applicants as ${status}?`;
      let notifyAdmin = false;
      
      if (status === 'shortlisted') {
        msg += "\n\nWould you also like to notify the admin about this shortlist update?";
        notifyAdmin = confirm(msg); // First confirm includes admin notify option if they say yes to admin
        if (!notifyAdmin) {
           if (!confirm(`Mark as ${status} without notifying admin?`)) return;
        }
      } else {
        if (!confirm(msg)) return;
      }
      
      try {
        await axios.put('/api/company/applications/bulk-status', {
          application_ids: selectedApplicants.value,
          status: status,
          notify_admin: notifyAdmin
        });
        proxy.$toast(`Successfully marked as ${status}.`, 'success');
        selectedApplicants.value = [];
        loadApps();
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to update applications.', 'error');
      }
    };
    
    const openTestLinkModal = () => {
      proxy.$toast('Select applicants individually to send distinct test links, or shortlist them first.', 'info');
    };
    
    const openInterviewModal = () => {
      proxy.$toast('Select applicants individually to schedule interviews.', 'info');
    };

    return { 
      applications, 
      loading, 
      searchQuery,
      statusFilter,
      filteredApplications,
      selectedApplicants,
      isAllSelected,
      toggleSelectAll,
      openBulkStatusModal,
      openTestLinkModal,
      openInterviewModal,
      isGeneralView,
      formatDate,
      reviewStudent,
      selectedApp,
      studentPastApps,
      loadingStudentApps,
      openStatusModal,
      confirmUpdateStatus,
      statusUpdateApp,
      newStatus,
      statusFeedback,
      statusInterviewDate,
      statusInterviewLink,
      statusTestDate,
      statusTestLink,
      isUpdatingStatus
    };
  }
}
</script>
