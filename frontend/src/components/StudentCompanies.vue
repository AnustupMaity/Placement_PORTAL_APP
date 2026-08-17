<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Companies</h1>
        <p class="page-subtitle">Explore companies recruiting on campus.</p>
      </div>
      <div>
        <input type="text" class="form-control" v-model="searchQuery" placeholder="Search companies..." style="width: 250px;" @input="debouncedLoad" />
      </div>
    </div>

    <div class="ppa-card">
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Industry</th>
              <th>Active Drives</th>
              <th>Applied Drives</th>
              <th>Not Applied Drives</th>
              <th>Total Drives</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td>
            </tr>
            <tr v-else-if="companies.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">No approved companies found.</td>
            </tr>
            <tr v-for="c in companies" :key="c.id" v-else>
              <td class="fw-bold">{{ c.company_name }}</td>
              <td class="text-muted">{{ c.industry || '—' }}</td>
              <td>
                <span v-if="c.active_drives > 0" class="text-success fw-medium">{{ c.active_drives }}</span>
                <span v-else class="text-muted">0</span>
              </td>
              <td>
                <span v-if="c.applied_drives > 0" class="text-primary fw-medium">{{ c.applied_drives }}</span>
                <span v-else></span>
              </td>
              <td>
                <span v-if="c.not_applied_drives > 0" class="text-danger fw-bold">{{ c.not_applied_drives }}</span>
                <span v-else></span>
              </td>
              <td class="text-muted">{{ c.total_drives }}</td>
              <td>
                <button class="btn btn-sm btn-outline-info" @click="viewCompanyDrives(c)">View Drives</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Company Drives Modal -->
    <div class="modal fade" id="companyDrivesModal" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div v-if="selectedCompany">
              <h5 class="modal-title fw-bold mb-0">{{ selectedCompany.company_name }}</h5>
              <p class="text-muted small mb-0">
                <span v-if="selectedCompany.industry">{{ selectedCompany.industry }}</span>
                <span v-if="selectedCompany.location"> · {{ selectedCompany.location }}</span>
                <span v-if="selectedCompany.description"> — {{ selectedCompany.description }}</span>
              </p>
            </div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body p-0">
            <div v-if="loadingDrives" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>

            <div v-else-if="selectedCompany">
              <div v-if="companyDrives.length === 0" class="text-center py-4 text-muted">
                <p class="mb-0">No drives found for this company.</p>
              </div>

              <div class="table-responsive">
                <table class="table ppa-table mb-0">
                  <thead>
                    <tr>
                      <th>Role</th>
                      <th>Location</th>
                      <th>Salary/yr</th>
                      <th>Deadline</th>
                      <th>Min CGPA</th>
                      <th>Branches</th>
                      <th>Batch</th>
                      <th>App Status</th>
                      <th>Drive Status</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="d in companyDrives" :key="d.id">
                      <td class="fw-bold">{{ d.job_title }}</td>
                      <td class="text-muted">{{ d.location || '—' }}</td>
                      <td class="text-muted">{{ d.salary || '—' }}</td>
                      <td class="text-muted">{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : '—' }}</td>
                      <td class="text-muted">{{ d.min_cgpa || '—' }}</td>
                      <td class="text-muted">{{ formatBranches(d.eligible_branches) }}</td>
                      <td class="text-muted">{{ d.eligible_year || '—' }}</td>
                      <td>
                        <span v-if="d.applied" class="badge bg-success">Applied</span>
                        <span v-else class="text-muted small">Not Applied</span>
                      </td>
                      <td>
                        <span v-if="d.status === 'approved' && d.is_open" class="status-badge badge-active">Open</span>
                        <span v-else-if="d.status === 'cancelled'" class="status-badge badge-cancelled">Cancelled</span>
                        <span v-else class="status-badge badge-closed">Closed</span>
                      </td>
                      <td>
                        <router-link :to="`/student/drives/${d.id}`" class="btn btn-sm btn-outline-primary" @click="closeDrivesModal">Details</router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
import { ref, onMounted, getCurrentInstance } from 'vue';

export default {
  name: 'StudentCompanies',
  setup() {
    const { proxy } = getCurrentInstance();
    const companies = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const selectedCompany = ref(null);
    const companyDrives = ref([]);
    const loadingDrives = ref(false);
    let drivesModalInstance = null;
    let debounceTimer = null;

    const loadCompanies = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/student/companies', {
          params: { search: searchQuery.value }
        });
        companies.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load companies.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const debouncedLoad = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(loadCompanies, 350);
    };

    const viewCompanyDrives = async (company) => {
      selectedCompany.value = company;
      companyDrives.value = [];
      loadingDrives.value = true;

      if (!drivesModalInstance && window.bootstrap) {
        drivesModalInstance = new window.bootstrap.Modal(document.getElementById('companyDrivesModal'));
      }
      if (drivesModalInstance) drivesModalInstance.show();

      try {
        const res = await axios.get(`/api/student/companies/${company.id}/drives`);
        selectedCompany.value = res.data.company;
        companyDrives.value = res.data.drives;
      } catch (err) {
        proxy.$toast('Failed to load company drives.', 'error');
      } finally {
        loadingDrives.value = false;
      }
    };

    const closeDrivesModal = () => {
      if (drivesModalInstance) drivesModalInstance.hide();
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

    onMounted(loadCompanies);

    return {
      companies, loading, searchQuery, debouncedLoad,
      selectedCompany, companyDrives, loadingDrives,
      viewCompanyDrives, closeDrivesModal, formatBranches
    };
  }
}
</script>
