<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">My Applications</h1>
        <p class="page-subtitle">Track the status of roles you have applied for.</p>
      </div>
      <div>
        <input type="text" class="form-control" v-model="searchQuery" placeholder="Search by role or company..." style="width: 260px;">
      </div>
    </div>

    <div class="ppa-card">
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Date Applied</th>
              <th>App Status</th>
              <th>Drive Status</th>
              <th>Offer Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td>
            </tr>
            <tr v-else-if="filteredApplications.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">No applications found.</td>
            </tr>
            <tr v-for="app in filteredApplications" :key="app.id" v-else>
              <td class="fw-medium">{{ app.company_name }}</td>
              <td>{{ app.job_title }}</td>
              <td class="text-muted">{{ new Date(app.application_date).toLocaleDateString() }}</td>
              <td><span :class="'status-badge badge-' + app.status">{{ app.status }}</span></td>
              <td>
                <span v-if="app.drive_status === 'approved' && isDriveOpen(app)" class="status-badge badge-active">Open</span>
                <span v-else-if="app.drive_status === 'cancelled'" class="status-badge badge-cancelled">Cancelled</span>
                <span v-else class="status-badge badge-closed">Closed</span>
              </td>
              <td>
                <span v-if="app.placement">
                  <span v-if="app.placement.is_accepted" class="badge bg-success">Accepted</span>
                  <span v-else class="badge bg-warning text-dark">Pending</span>
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary" @click="viewDetails(app)">View Details</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Application Detail Modal -->
    <div class="modal fade" id="appDetailModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header" v-if="selected">
            <div>
              <h5 class="modal-title fw-bold mb-0">{{ selected.job_title }}</h5>
              <p class="text-muted small mb-0">{{ selected.company_name }}<span v-if="selected.company_industry"> · {{ selected.company_industry }}</span></p>
            </div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selected">
            <!-- Visual Progress Stepper -->
            <div class="ppa-stepper mb-4">
              <div class="stepper-step completed">
                <div class="stepper-icon"><i class="bi bi-send-check"></i></div>
                <div class="stepper-label">Applied</div>
              </div>
              <div class="stepper-step" :class="{ completed: ['shortlisted', 'interview', 'selected'].includes(selected.status), active: selected.status === 'shortlisted' }">
                <div class="stepper-icon"><i class="bi bi-file-earmark-person"></i></div>
                <div class="stepper-label">Shortlisted</div>
              </div>
              <div class="stepper-step" :class="{ completed: ['interview', 'selected'].includes(selected.status), active: selected.status === 'interview' }">
                <div class="stepper-icon"><i class="bi bi-person-video"></i></div>
                <div class="stepper-label">Interview</div>
              </div>
              <div class="stepper-step" :class="{ completed: selected.status === 'selected', active: selected.status === 'selected' && (!selected.placement || !selected.placement.is_accepted) }">
                <div class="stepper-icon"><i class="bi bi-award"></i></div>
                <div class="stepper-label">Offer Extended</div>
              </div>
              <div class="stepper-step" :class="{ completed: selected.placement && selected.placement.is_accepted }">
                <div class="stepper-icon"><i class="bi bi-pen"></i></div>
                <div class="stepper-label">Signed & Accepted</div>
              </div>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-2">Drive Details</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width:40%">Company</td><td class="fw-medium">{{ selected.company_name }}</td></tr>
                    <tr><td class="text-muted">Industry</td><td>{{ selected.company_industry || '—' }}</td></tr>
                    <tr><td class="text-muted">Role</td><td class="fw-medium">{{ selected.job_title }}</td></tr>
                    <tr><td class="text-muted">Location</td><td>{{ selected.location || '—' }}</td></tr>
                    <tr><td class="text-muted">Salary/yr</td><td>{{ selected.salary || '—' }}</td></tr>
                    <tr><td class="text-muted">Deadline</td><td>{{ selected.application_deadline ? new Date(selected.application_deadline).toLocaleDateString() : '—' }}</td></tr>

                    <tr><td class="text-muted">Min CGPA</td><td>{{ selected.min_cgpa || '—' }}</td></tr>
                    <tr><td class="text-muted">Branches</td><td>{{ formatBranches(selected.eligible_branches) }}</td></tr>
                    <tr><td class="text-muted">Batch</td><td>{{ selected.eligible_year || '—' }}</td></tr>
                    <tr><td class="text-muted">Status</td><td>
                      <span v-if="selected.drive_status === 'approved' && isDriveOpen(selected)" class="status-badge badge-active">Open</span>
                      <span v-else-if="selected.drive_status === 'cancelled'" class="status-badge badge-cancelled">Cancelled</span>
                      <span v-else class="status-badge badge-closed">Closed</span>
                    </td></tr>
                  </tbody>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-2">Application Status</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width:40%">Status</td><td><span :class="'status-badge badge-' + selected.status">{{ selected.status }}</span></td></tr>
                    <tr><td class="text-muted">Applied On</td><td>{{ selected.application_date ? new Date(selected.application_date).toLocaleDateString() : '—' }}</td></tr>
                    <tr v-if="selected.accepted_at"><td class="text-muted">Accepted On</td><td>{{ new Date(selected.accepted_at).toLocaleDateString() }}</td></tr>
                    <tr v-if="selected.feedback"><td class="text-muted">Feedback</td><td class="small">{{ selected.feedback }}</td></tr>
                  </tbody>
                </table>

                <div v-if="selected.placement" class="mt-3 p-3 rounded border border-success bg-light">
                  <h6 class="fw-bold text-success mb-2">Placement Offer</h6>
                  <table class="table table-sm table-borderless mb-0">
                    <tbody>
                      <tr><td class="text-muted" style="width:40%">Position</td><td class="fw-medium">{{ selected.placement.position || selected.job_title }}</td></tr>
                      <tr><td class="text-muted">Package</td><td class="fw-bold text-success">{{ selected.placement.salary || '—' }}</td></tr>
                      <tr><td class="text-muted">Offer Date</td><td>{{ selected.placement.created_at ? new Date(selected.placement.created_at).toLocaleDateString() : '—' }}</td></tr>
                      <tr><td class="text-muted">Accepted</td><td>
                        <span v-if="selected.placement.is_accepted" class="badge bg-success">Yes</span>
                        <span v-else class="badge bg-warning text-dark">Pending</span>
                      </td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0">
            <router-link :to="`/student/drives/${selected?.drive_id}`" class="btn btn-outline-primary btn-sm" v-if="selected">Go to Drive</router-link>
            <button type="button" class="btn btn-light btn-sm" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, getCurrentInstance } from 'vue';

export default {
  name: 'StudentApplications',
  setup() {
    const applications = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const selected = ref(null);
    let modalInstance = null;
    const { proxy } = getCurrentInstance();

    const loadApps = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/student/applications');
        applications.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load applications.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const filteredApplications = computed(() => {
      const q = searchQuery.value.toLowerCase();
      if (!q) return applications.value;
      return applications.value.filter(a =>
        a.job_title.toLowerCase().includes(q) ||
        a.company_name.toLowerCase().includes(q) ||
        a.status.toLowerCase().includes(q)
      );
    });

    const viewDetails = (app) => {
      selected.value = app;
      if (!modalInstance && window.bootstrap) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('appDetailModal'));
      }
      if (modalInstance) modalInstance.show();
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

    const isDriveOpen = (d) => {
      if (!d || !d.application_deadline) return false;
      return new Date(d.application_deadline) >= new Date();
    };

    onMounted(loadApps);

    return { applications, loading, searchQuery, filteredApplications, selected, viewDetails, formatBranches, isDriveOpen };
  }
}
</script>
