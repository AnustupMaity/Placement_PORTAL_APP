<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Company Dashboard</h1>
        <p class="page-subtitle">Welcome back! Manage your recruitment drives.</p>
      </div>
      <div>
        <router-link to="/company/drives/create" class="btn btn-gradient">
          <i class="bi bi-plus-lg me-1"></i> Post New Drive
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <template v-else>
      <div v-if="stats.company?.approval_status === 'pending'" class="alert alert-warning">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        Your company profile is pending admin approval. You can create drives, but they won't be visible to students until your profile is approved.
      </div>
      <div v-else-if="stats.company?.approval_status === 'rejected'" class="alert alert-danger">
        <i class="bi bi-x-circle-fill me-2"></i>
        Your company profile has been rejected by the admin.
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="stat-card stat-blue h-100">
            <div class="stat-icon"><i class="bi bi-briefcase"></i></div>
            <div class="stat-value">{{ stats.total_drives || 0 }}</div>
            <div class="stat-label">Total Drives</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card stat-purple h-100">
            <div class="stat-icon"><i class="bi bi-file-earmark-person"></i></div>
            <div class="stat-value">{{ stats.total_applications || 0 }}</div>
            <div class="stat-label">Applications Received</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card stat-green h-100">
            <div class="stat-icon"><i class="bi bi-check-circle"></i></div>
            <div class="stat-value">{{ stats.active_drives || 0 }}</div>
            <div class="stat-label">Active Drives</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card stat-orange h-100">
            <div class="stat-icon"><i class="bi bi-award"></i></div>
            <div class="stat-value">{{ stats.total_placements || 0 }}</div>
            <div class="stat-label">Total Placements</div>
          </div>
        </div>
      </div>

      <div class="row g-4 align-items-stretch">
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Quick Actions</div>
              <div class="card-body d-flex flex-column flex-grow-1">
                <div class="d-flex flex-column gap-3 h-100 justify-content-between">
                  <router-link to="/company/drives" class="btn btn-outline-success text-start flex-grow-1 d-flex align-items-center px-4">View My Drives</router-link>
                  <router-link to="/company/applications" class="btn btn-outline-success text-start flex-grow-1 d-flex align-items-center px-4">View Applications</router-link>
                  <router-link to="/company/placements" class="btn btn-outline-success text-start flex-grow-1 d-flex align-items-center px-4">View Placements</router-link>
                  <router-link to="/company/profile" class="btn btn-outline-success text-start flex-grow-1 d-flex align-items-center px-4">Update Profile</router-link>
                  <button @click="exportCSV" class="btn btn-outline-success text-start flex-grow-1 d-flex align-items-center px-4" :disabled="exporting">
                    <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                    Export Applicants
                  </button>
                </div>
              </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Application Status Breakdown</div>
            <div class="card-body text-center flex-grow-1 d-flex align-items-center justify-content-center">
              <canvas id="companyAppChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, getCurrentInstance } from 'vue';

export default {
  name: 'CompanyDashboard',
  setup() {
    const stats = ref({});
    const loading = ref(true);
    const exporting = ref(false);
    const { proxy } = getCurrentInstance();

    const loadStats = async () => {
      try {
        const res = await axios.get('/api/company/dashboard');
        stats.value = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const loadCharts = async () => {
      try {
        const res = await axios.get('/api/company/analytics');
        const data = res.data;
        await nextTick();

        if (document.getElementById('companyAppChart')) {
          new Chart(document.getElementById('companyAppChart'), {
            type: 'pie',
            data: {
              labels: Object.keys(data.applications),
              datasets: [{
                data: Object.values(data.applications),
                backgroundColor: ['#2c63ff', '#1dc9b7', '#ffb822', '#fd3995']
              }]
            }
          });
        }
      } catch (err) {
        console.error('Failed to load charts', err);
      }
    };

    const exportCSV = async () => {
      exporting.value = true;
      try {
        const res = await axios.post('/api/export/company/applications');
        
        if (res.data.filename) {
          downloadFile(res.data.filename);
        } else if (res.data.task_id) {
          proxy.$toast('Export started. Processing...', 'info');
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

    onMounted(async () => {
        await loadStats();
        await loadCharts();
    });

    return { stats, loading, exporting, exportCSV };
  }
}
</script>

<style scoped>
/* the big banner shown in CompanyDashboard.vue when the company is waiting for admin approval */
.pending-banner {
  text-align: center;
  padding: 4rem 2rem;
}

.pending-icon {
  font-size: 4rem;
  background: var(--ppa-primary);

  color: var(--ppa-primary);

  display: block;
  margin-bottom: 1rem;
  animation: pulse-scale 2s ease-in-out infinite;
}

@keyframes pulse-scale {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.06);
  }
}
</style>
