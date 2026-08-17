<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Admin Dashboard</h1>
        <p class="page-subtitle">Overview of the placement portal system</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <template v-else>
      <div class="row g-4 mb-4">
        <div class="col-md">
          <div class="stat-card stat-blue">
            <div class="stat-icon"><i class="bi bi-people"></i></div>
            <div class="stat-value">{{ stats.total_students || 0 }}</div>
            <div class="stat-label">Total Students</div>
          </div>
        </div>
        <div class="col-md">
          <div class="stat-card stat-purple">
            <div class="stat-icon"><i class="bi bi-building"></i></div>
            <div class="stat-value">{{ stats.total_companies || 0 }}</div>
            <div class="stat-label">Total Companies</div>
          </div>
        </div>
        <div class="col-md">
          <div class="stat-card stat-orange">
            <div class="stat-icon"><i class="bi bi-briefcase"></i></div>
            <div class="stat-value">{{ stats.total_drives || 0 }}</div>
            <div class="stat-label">Placement Drives</div>
          </div>
        </div>
        <div class="col-md">
          <div class="stat-card stat-green">
            <div class="stat-icon"><i class="bi bi-file-earmark-text"></i></div>
            <div class="stat-value">{{ stats.total_applications || 0 }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
        </div>
        <div class="col-md">
          <div class="stat-card stat-cyan">
            <div class="stat-icon"><i class="bi bi-trophy"></i></div>
            <div class="stat-value">{{ stats.total_placements || 0 }}</div>
            <div class="stat-label">Total Placements</div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span>Quick Links</span>
            </div>
            <div class="card-body flex-grow-1">
              <div class="d-grid gap-2">
                <router-link to="/admin/companies" class="btn btn-outline-primary text-start"><i class="bi bi-building me-2"></i> Manage Companies</router-link>
                <router-link to="/admin/students" class="btn btn-outline-primary text-start"><i class="bi bi-people me-2"></i> Manage Students</router-link>
                <router-link to="/admin/drives" class="btn btn-outline-primary text-start"><i class="bi bi-briefcase me-2"></i> Manage Drives</router-link>
                <router-link to="/admin/applications" class="btn btn-outline-primary text-start"><i class="bi bi-file-earmark-text me-2"></i> Manage Applications</router-link>
                <router-link to="/admin/placements" class="btn btn-outline-primary text-start"><i class="bi bi-trophy me-2"></i> View Placements</router-link>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Application Status Breakdown</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="adminAppChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-12">
          <div class="ppa-card border-info">
            <div class="card-header bg-info text-white">
              <i class="bi bi-gear-fill me-2"></i> Background Tasks
            </div>
            <div class="card-body">
              <p class="text-muted small mb-3 text-center">These tasks run automatically on a schedule, but you can trigger them manually if needed.</p>
              <div class="d-flex flex-wrap justify-content-center gap-3">
                <button @click="triggerDailyReminders" class="btn btn-outline-primary">
                  <i class="bi bi-envelope me-2"></i> Send Daily Reminders
                </button>
                <button @click="triggerMonthlyReport" class="btn btn-outline-primary">
                  <i class="bi bi-file-earmark-bar-graph me-2"></i> Send Monthly Report
                </button>
                <button @click="exportCSV" class="btn btn-outline-primary" :disabled="exporting">
                  <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-download me-2"></i> Export Placement Data
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Placement Drives Status</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="adminDriveChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Company Approvals</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="adminCompanyChart" style="max-height: 250px;"></canvas>
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
  name: 'AdminDashboard',
  setup() {
    const stats = ref({});
    const loading = ref(true);
    const exporting = ref(false);
    const { proxy } = getCurrentInstance();

    const loadStats = async () => {
      try {
        const res = await axios.get('/api/admin/dashboard');
        stats.value = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const loadCharts = async () => {
      try {
        const res = await axios.get('/api/admin/analytics');
        const data = res.data;
        await nextTick(); // ensure DOM is updated

        // Applications Chart (Bar)
        if (document.getElementById('adminAppChart')) {
          new Chart(document.getElementById('adminAppChart'), {
            type: 'bar',
            data: {
              labels: Object.keys(data.applications),
              datasets: [{
                label: 'Applications',
                data: Object.values(data.applications),
                backgroundColor: ['#2c63ff', '#ffb822', '#1dc9b7', '#fd3995'],
                maxBarThickness: 50
              }]
            }
          });
        }

        // Drives Chart (Pie)
        if (document.getElementById('adminDriveChart')) {
          new Chart(document.getElementById('adminDriveChart'), {
            type: 'pie',
            data: {
              labels: Object.keys(data.drives),
              datasets: [{
                data: Object.values(data.drives),
                backgroundColor: ['#1dc9b7', '#ffb822', '#fd3995']
              }]
            }
          });
        }

        // Companies Chart (Pie)
        if (document.getElementById('adminCompanyChart') && data.companies) {
          new Chart(document.getElementById('adminCompanyChart'), {
            type: 'pie',
            data: {
              labels: Object.keys(data.companies),
              datasets: [{
                data: Object.values(data.companies),
                backgroundColor: ['#2c63ff', '#fd3995', '#ffb822']
              }]
            }
          });
        }
      } catch (err) {
        console.error('Failed to load charts', err);
      }
    };

    const triggerDailyReminders = async () => {
      try {
        const res = await axios.post('/api/admin/trigger/daily-reminders');
        alert(res.data.message);
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to trigger daily reminders.');
      }
    };

    const triggerMonthlyReport = async () => {
      try {
        const res = await axios.post('/api/admin/trigger/monthly-report');
        alert(res.data.message);
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to trigger monthly report.');
      }
    };

    const exportCSV = async () => {
      exporting.value = true;
      try {
        const res = await axios.post('/api/export/admin/applications');
        
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

    return { 
      stats, 
      loading,
      exporting,
      triggerDailyReminders,
      triggerMonthlyReport,
      exportCSV
    };
  }
}
</script>

<style>
/* Total Placements box colors */
.stat-cyan .stat-icon {
  background: rgba(13, 202, 240, 0.15);
  color: #0dcaf0;
}
.stat-cyan .stat-value { color: #0dcaf0; }
</style>
