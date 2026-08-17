<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">My Placement Drives</h1>
        <p class="page-subtitle">Manage the roles you are hiring for.</p>
      </div>
      <div class="d-flex align-items-center gap-3 flex-wrap">
        <select class="form-select form-select-sm" v-model="statusFilter" style="min-width: 130px; width: auto;">
          <option value="">All Drives</option>
          <option value="approved">Active</option>
          <option value="closed">Closed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <input type="text" class="form-control form-control-sm" placeholder="Search drives..." v-model="searchQuery" style="width: 230px;">
        <router-link to="/company/drives/create" class="btn btn-gradient btn-sm text-nowrap">
          <i class="bi bi-plus-lg me-1"></i> Create Drive
        </router-link>
      </div>
    </div>

    <div class="ppa-card">
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table align-middle mb-0">
          <thead>
            <tr>
              <th>Role</th>
              <th>Location</th>
              <th>Salary</th>
              <th>Deadline</th>
              <th>Stats</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td>
            </tr>
            <tr v-else-if="filteredDrives.length === 0">
              <td colspan="7" class="text-center py-4 empty-state">
                <i class="bi bi-folder-x fs-2 text-muted mb-2 d-block"></i>
                <p class="text-muted">No placement drives found matching your criteria.</p>
              </td>
            </tr>
            <tr v-for="d in filteredDrives" :key="d.id" v-else>
              <td class="fw-medium">{{ d.job_title }}</td>
              <td class="text-muted">{{ d.location || 'Remote' }}</td>
              <td class="text-muted">{{ d.salary || '—' }}</td>
              <td class="text-muted">{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : '—' }}</td>
              <td class="text-muted small" style="min-width: 150px;">
                <div v-if="d.stats && d.stats.total > 0">
                  <div>Total Applied: {{ d.stats.total }}</div>
                  <div v-if="d.stats.selected > 0">Selected: {{ d.stats.selected }}</div>
                  <div v-if="d.stats.interview > 0">Interviewing: {{ d.stats.interview }}</div>
                  <div v-if="d.stats.shortlisted > 0">Shortlisted: {{ d.stats.shortlisted }}</div>
                  <div v-if="d.stats.rejected > 0">Rejected: {{ d.stats.rejected }}</div>
                </div>
                <div v-else>No apps</div>
              </td>
              <td><span :class="'status-badge badge-' + d.status">{{ d.status === 'approved' ? 'active' : d.status }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-info me-2 mb-1" @click="viewDetails(d)">View Details</button>
                <router-link :to="`/company/drives/${d.id}/applications`" class="btn btn-sm btn-outline-primary me-2 mb-1">
                  Applications
                </router-link>
                <button v-if="d.status !== 'closed'" @click="closeDrive(d.id)" class="btn btn-sm btn-outline-secondary mb-1" title="Mark as Closed">
                  Close
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Drive Details Modal -->
    <div class="modal fade" id="companyDriveDetailModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header" v-if="selected">
            <div>
              <h5 class="modal-title fw-bold mb-0">{{ selected.job_title }}</h5>
              <p class="text-muted small mb-0"><span :class="'status-badge badge-' + selected.status">{{ selected.status === 'approved' ? 'active' : selected.status }}</span></p>
            </div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selected">
            <h6 class="fw-bold text-primary mb-3">Drive Information</h6>
            <table class="table table-sm table-borderless mb-0">
              <tbody>
                <tr><td class="text-muted" style="width:30%">Role</td><td class="fw-medium">{{ selected.job_title }}</td></tr>
                <tr><td class="text-muted">Location</td><td>{{ selected.location || 'Remote' }}</td></tr>
                <tr><td class="text-muted">Salary</td><td>{{ selected.salary || '—' }}</td></tr>
                <tr><td class="text-muted">Deadline</td><td>{{ selected.application_deadline ? new Date(selected.application_deadline).toLocaleDateString() : '—' }}</td></tr>

                <tr><td class="text-muted">Min CGPA</td><td>{{ selected.min_cgpa || '—' }}</td></tr>
                <tr><td class="text-muted">Branches</td><td>{{ formatBranches(selected.eligible_branches) }}</td></tr>
                <tr><td class="text-muted">Batch</td><td>{{ selected.eligible_year || '—' }}</td></tr>
                <tr v-if="selected.required_skills"><td class="text-muted">Skills</td><td>{{ selected.required_skills }}</td></tr>
                <tr v-if="selected.job_description"><td class="text-muted">Description</td><td style="white-space: pre-wrap;">{{ selected.job_description }}</td></tr>
              </tbody>
            </table>
          </div>
          <div class="modal-footer border-top-0 d-flex justify-content-between w-100" v-if="selected">
            <div>
                <button v-if="selected.status !== 'closed'" @click="closeDrive(selected.id); closeModal()" class="btn btn-outline-secondary btn-sm">Close Drive</button>
            </div>
            <div>
                <router-link :to="`/company/drives/${selected?.id}/applications`" class="btn btn-primary btn-sm me-2" @click="closeModal">View Applications</router-link>
                <button type="button" class="btn btn-light btn-sm" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, computed, getCurrentInstance } from 'vue';

export default {
  name: 'CompanyDrives',
  setup() {
    const drives = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const statusFilter = ref('');
    const selected = ref(null);
    let modalInstance = null;
    const { proxy } = getCurrentInstance();

    const loadDrives = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/company/drives');
        drives.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load drives.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const filteredDrives = computed(() => {
      const q = searchQuery.value.toLowerCase();
      let filtered = drives.value;
      if (statusFilter.value) {
        filtered = filtered.filter(d => d.status === statusFilter.value);
      }
      if (q) {
        filtered = filtered.filter(d => 
          (d.job_title && d.job_title.toLowerCase().includes(q)) ||
          (d.location && d.location.toLowerCase().includes(q)) ||
          (d.status && (d.status === 'approved' ? 'active' : d.status).toLowerCase().includes(q)) ||
          (d.salary && d.salary.toLowerCase().includes(q))
        );
      }
      return filtered;
    });

    const closeDrive = async (id) => {
      if (!confirm('Are you sure you want to close this drive? Students will no longer be able to apply.')) return;
      try {
        await axios.put(`/api/company/drives/${id}/close`);
        proxy.$toast('Drive closed successfully.', 'success');
        if (selected.value && selected.value.id === id) {
           selected.value.status = 'closed';
        }
        await loadDrives();
      } catch (err) {
        proxy.$toast('Failed to close drive.', 'error');
      }
    };

    const viewDetails = (drive) => {
      selected.value = drive;
      if (!modalInstance && window.bootstrap) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('companyDriveDetailModal'));
      }
      if (modalInstance) modalInstance.show();
    };

    const closeModal = () => {
      if (modalInstance) modalInstance.hide();
    };

    const formatBranches = (branches) => {
      if (!branches) return '—';
      try {
        const arr = typeof branches === 'string' ? JSON.parse(branches) : branches;
        return Array.isArray(arr) ? arr.join(', ') : branches;
      } catch {
        return branches;
      }
    };

    onMounted(loadDrives);

    return { 
      drives, loading, searchQuery, statusFilter, filteredDrives, selected,
      closeDrive, viewDetails, closeModal, formatBranches
    };
  }
}
</script>
