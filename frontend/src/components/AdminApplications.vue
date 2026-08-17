<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">All Applications</h1>
        <p class="page-subtitle">View all student applications across the platform</p>
      </div>
    </div>

    <div class="ppa-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span>Application Records</span>
        <div class="input-group input-group-sm" style="max-width: 250px;">
          <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" placeholder="Search applications..." v-model="searchQuery">
        </div>
      </div>
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student Name</th>
              <th>Company</th>
              <th>Role</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="6" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td></tr>
            <tr v-else-if="filteredApps.length === 0"><td colspan="6" class="text-center py-4 text-muted">No applications found.</td></tr>
            <tr v-for="app in filteredApps" :key="app.id" v-else>
              <td>#{{ app.id }}</td>
              <td class="fw-medium">{{ app.student_name }}</td>
              <td>{{ app.company_name }}</td>
              <td>{{ app.drive_title }}</td>
              <td>{{ new Date(app.application_date).toLocaleDateString() }}</td>
              <td>
                <span :class="'status-badge badge-' + app.status">{{ app.status }}</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-info" @click="viewAppInfo(app.id)">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Application Info Modal -->
    <div class="modal fade" id="appInfoModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold">Application Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body pt-3">
            <div v-if="loadingDetails" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <div v-else-if="selectedApp">
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Student Details</h6>
                  <p class="mb-1"><i class="bi bi-person me-2"></i><strong>Name:</strong> {{ selectedApp.student.full_name }}</p>
                  <p class="mb-1"><i class="bi bi-person-badge me-2"></i><strong>Roll No:</strong> {{ selectedApp.student.roll_number || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-diagram-2 me-2"></i><strong>Branch:</strong> {{ selectedApp.student.branch || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-award me-2"></i><strong>CGPA:</strong> {{ selectedApp.student.cgpa || 'N/A' }}</p>
                </div>
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Drive Details</h6>
                  <p class="mb-1"><i class="bi bi-building me-2"></i><strong>Company:</strong> {{ selectedApp.company.company_name }}</p>
                  <p class="mb-1"><i class="bi bi-briefcase me-2"></i><strong>Role:</strong> {{ selectedApp.drive.job_title }}</p>
                  <p class="mb-1"><i class="bi bi-geo-alt me-2"></i><strong>Location:</strong> {{ selectedApp.drive.location || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-currency-rupee me-2"></i><strong>Salary:</strong> {{ selectedApp.drive.salary || 'N/A' }}</p>
                </div>
              </div>

              <h6 class="border-top pt-3 text-primary">Application Status</h6>
              <div class="mb-3">
                <p class="mb-1"><i class="bi bi-calendar me-2"></i><strong>Applied On:</strong> {{ new Date(selectedApp.application.application_date).toLocaleDateString() }}</p>
                <p class="mb-1"><i class="bi bi-info-circle me-2"></i><strong>Status:</strong> <span :class="'status-badge badge-' + selectedApp.application.status">{{ selectedApp.application.status }}</span></p>
                <p v-if="selectedApp.application.feedback" class="mb-1 mt-2 text-muted"><i class="bi bi-chat-text me-2"></i><strong>Feedback:</strong> {{ selectedApp.application.feedback }}</p>
              </div>

              <div v-if="selectedApp.placement" class="p-3 bg-light rounded border border-success">
                <h6 class="fw-bold text-success mb-2"><i class="bi bi-check-circle-fill me-2"></i>Placement Offer Received</h6>
                <p class="mb-0"><strong>Package:</strong> <i class="bi bi-currency-rupee"></i>{{ selectedApp.placement.salary || 'N/A' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance, computed } from 'vue';

export default {
  name: 'AdminApplications',
  setup() {
    const applications = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const { proxy } = getCurrentInstance();
    
    // Modal state
    const selectedApp = ref(null);
    const loadingDetails = ref(false);
    let modalInstance = null;

    const loadApps = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/admin/applications');
        applications.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load applications.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const viewAppInfo = async (id) => {
      selectedApp.value = null;
      loadingDetails.value = true;
      
      if (!modalInstance) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('appInfoModal'));
      }
      modalInstance.show();

      try {
        const res = await axios.get(`/api/admin/applications/${id}/details`);
        selectedApp.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load application details.', 'error');
        modalInstance.hide();
      } finally {
        loadingDetails.value = false;
      }
    };

    const filteredApps = computed(() => {
      if (!searchQuery.value) return applications.value;
      const q = searchQuery.value.toLowerCase();
      return applications.value.filter(app => 
        (app.student_name && app.student_name.toLowerCase().includes(q)) ||
        (app.company_name && app.company_name.toLowerCase().includes(q)) ||
        (app.drive_title && app.drive_title.toLowerCase().includes(q)) ||
        (app.status && app.status.toLowerCase().includes(q))
      );
    });

    onMounted(loadApps);

    return { 
      applications, 
      loading, 
      searchQuery, 
      filteredApps,
      viewAppInfo,
      selectedApp,
      loadingDetails
    };
  }
}
</script>
