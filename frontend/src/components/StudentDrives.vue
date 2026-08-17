<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Placement Drives</h1>
        <p class="page-subtitle">Discover and apply to open positions.</p>
      </div>
      <div class="d-flex gap-2 align-items-center flex-wrap">
        <input type="text" class="form-control form-control-sm" v-model="searchQuery" placeholder="Search by role or company..." style="width: 230px;">
        <select v-model="statusFilter" class="form-select form-select-sm" style="width: auto;">
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="appliedFilter" class="form-select form-select-sm" style="width: auto;">
          <option value="all">All Apps</option>
          <option value="applied">Applied</option>
          <option value="not_applied">Not Applied</option>
        </select>
        <select v-model="eligibilityFilter" class="form-select form-select-sm" style="width: auto;">
          <option value="all">All Eligibility</option>
          <option value="eligible">Eligible Only</option>
        </select>
      </div>
    </div>

    <div class="ppa-card">
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>App Status</th>
              <th>Drive Status</th>
              <th>Role</th>
              <th>Company</th>
              <th>Location</th>
              <th>Salary</th>
              <th>Deadline</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="8" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td>
            </tr>
            <tr v-else-if="filteredDrives.length === 0">
              <td colspan="8" class="text-center py-4 text-muted">No drives found matching your criteria.</td>
            </tr>
            <tr v-for="d in filteredDrives" :key="d.id" v-else>
              <td>
                <span v-if="d.applied" class="badge bg-success">Applied</span>
                <span v-else class="text-muted small">Not Applied</span>
              </td>
              <td>
                <span v-if="d.status === 'approved' && isOpen(d)" class="status-badge badge-active">Open</span>
                <span v-else-if="d.status === 'cancelled'" class="status-badge badge-cancelled">Cancelled</span>
                <span v-else class="status-badge badge-closed">Closed</span>
              </td>
              <td class="fw-bold">{{ d.job_title }}</td>
              <td class="text-muted">{{ d.company_name }}</td>
              <td class="text-muted">{{ d.location || '—' }}</td>
              <td class="text-muted">{{ d.salary || '—' }}</td>
              <td class="text-muted">{{ new Date(d.application_deadline).toLocaleDateString() }}</td>
              <td>
                <router-link :to="`/student/drives/${d.id}`" class="btn btn-sm btn-outline-primary">View Details</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, getCurrentInstance } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'StudentDrives',
  setup() {
    const drives = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const eligibilityFilter = ref('all');
    const statusFilter = ref('all');
    const appliedFilter = ref('all');
    const route = useRoute();
    if (route.query.q) {
      searchQuery.value = route.query.q;
    }
    const studentProfile = ref(null);
    const { proxy } = getCurrentInstance();

    const loadDrives = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/student/drives');
        drives.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load drives.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const loadProfile = async () => {
      try {
        const res = await axios.get('/api/student/profile');
        studentProfile.value = res.data;
      } catch (err) {
        // silently fail
      }
    };

    const isOpen = (d) => {
      if (!d.application_deadline) return false;
      return new Date(d.application_deadline) >= new Date();
    };

    const parseBranches = (eligible_branches) => {
      if (!eligible_branches) return [];
      try {
        const parsed = typeof eligible_branches === 'string' ? JSON.parse(eligible_branches) : eligible_branches;
        return Array.isArray(parsed) ? parsed.map(b => b.trim().toLowerCase()) : [eligible_branches.toLowerCase()];
      } catch {
        // fallback: comma separated
        return eligible_branches.split(',').map(b => b.trim().toLowerCase());
      }
    };

    const filteredDrives = computed(() => {
      const q = searchQuery.value.toLowerCase();
      return drives.value.filter(d => {
        const matchesSearch = !q || d.job_title.toLowerCase().includes(q) || d.company_name.toLowerCase().includes(q);
        if (!matchesSearch) return false;

        // Eligibility Filter
        if (eligibilityFilter.value === 'eligible') {
          const s = studentProfile.value;
          if (!s) return false; // no profile loaded yet
          if (d.min_cgpa && (!s.cgpa || parseFloat(s.cgpa) < parseFloat(d.min_cgpa))) return false;
          if (d.eligible_year && d.eligible_year.toString().trim() !== '' && (!s.year || d.eligible_year.toString() !== s.year.toString())) return false;
          if (d.eligible_branches && d.eligible_branches.trim() !== '') {
            if (!s.branch) return false;
            const allowed = parseBranches(d.eligible_branches);
            if (!allowed.includes(s.branch.toLowerCase())) return false;
          }
        }

        // Status Filter
        if (statusFilter.value !== 'all') {
          let currentStatus = 'closed';
          if (d.status === 'approved' && isOpen(d)) currentStatus = 'active';
          else if (d.status === 'cancelled') currentStatus = 'cancelled';
          if (currentStatus !== statusFilter.value) return false;
        }

        // Applied Filter
        if (appliedFilter.value !== 'all') {
          if (appliedFilter.value === 'applied' && !d.applied) return false;
          if (appliedFilter.value === 'not_applied' && d.applied) return false;
        }

        return true;
      });
    });

    onMounted(async () => {
      await loadProfile();
      await loadDrives();
    });

    return {
      drives,
      loading,
      searchQuery,
      eligibilityFilter,
      statusFilter,
      appliedFilter,
      filteredDrives,
      isOpen
    };
  }
}
</script>
