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
      <div class="row g-4 mt-1">
        <div class="col-md-4">
          <div class="ppa-card h-100 d-flex flex-column border-primary">
            <div class="card-header bg-primary text-white"><i class="bi bi-bar-chart-fill me-2"></i>Placements by Branch</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="placementsByBranchChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="ppa-card h-100 d-flex flex-column border-success">
            <div class="card-header bg-success text-white"><i class="bi bi-graph-up me-2"></i>Salary Trends (LPA)</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="salaryTrendsChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="ppa-card h-100 d-flex flex-column border-danger">
            <div class="card-header bg-danger text-white"><i class="bi bi-star-fill me-2"></i>Top Recruiters</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="topRecruitersChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
      </div>
      <div class="row g-4 mt-1">
        <div class="col-12">
          <div class="ppa-card border-warning">
            <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
              <span><i class="bi bi-bell-fill me-2"></i>Recent Notifications</span>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div v-if="loadingNotifs" class="text-center py-4">
                  <span class="spinner-border spinner-border-sm text-primary"></span>
                </div>
                <div v-else-if="notifications.length === 0" class="text-center py-4 text-muted">
                  No recent notifications.
                </div>
                <a 
                  v-for="n in notifications.slice(0, 5)" 
                  :key="n.id" 
                  :href="n.link || '#'" 
                  class="list-group-item list-group-item-action d-flex align-items-start gap-3 p-3"
                  :class="{'bg-light': !n.is_read}"
                >
                  <i class="bi fs-4 mt-1" :class="{
                    'bi-award-fill text-warning': n.title.toLowerCase().includes('offer') || n.title.toLowerCase().includes('selected'),
                    'bi-calendar-check-fill text-info': n.title.toLowerCase().includes('interview') || n.title.toLowerCase().includes('test'),
                    'bi-bell-fill text-primary': !n.title.toLowerCase().includes('offer') && !n.title.toLowerCase().includes('interview')
                  }"></i>
                  <div>
                    <div class="d-flex justify-content-between align-items-center w-100 mb-1">
                      <h6 class="mb-0 fw-bold" :class="{'text-dark': !n.is_read, 'text-muted': n.is_read}">{{ n.title }}</h6>
                      <small class="text-muted">{{ formatDate(n.created_at) }}</small>
                    </div>
                    <p class="mb-0 small" :class="{'text-dark': !n.is_read, 'text-muted': n.is_read}">{{ n.message }}</p>
                  </div>
                </a>
              </div>
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
    const notifications = ref([]);
    const loadingNotifs = ref(true);
    const { proxy } = getCurrentInstance();

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    };

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

        // Advanced Analytics Charts
        if (data.charts) {
          // Placements by Branch (Bar)
          if (document.getElementById('placementsByBranchChart') && data.charts.placements_by_branch.labels.length) {
            new Chart(document.getElementById('placementsByBranchChart'), {
              type: 'bar',
              data: {
                labels: data.charts.placements_by_branch.labels,
                datasets: [{
                  label: 'Placements',
                  data: data.charts.placements_by_branch.data,
                  backgroundColor: '#2c63ff',
                  maxBarThickness: 40
                }]
              }
            });
          }

          // Top Recruiters (Bar/Horizontal)
          if (document.getElementById('topRecruitersChart') && data.charts.top_recruiters.labels.length) {
            new Chart(document.getElementById('topRecruitersChart'), {
              type: 'bar',
              options: { indexAxis: 'y' },
              data: {
                labels: data.charts.top_recruiters.labels,
                datasets: [{
                  label: 'Hires',
                  data: data.charts.top_recruiters.data,
                  backgroundColor: '#fd3995',
                  maxBarThickness: 30
                }]
              }
            });
          }

          // Salary Trends (Line)
          if (document.getElementById('salaryTrendsChart') && data.charts.salary_trends.labels.length) {
            new Chart(document.getElementById('salaryTrendsChart'), {
              type: 'line',
              data: {
                labels: data.charts.salary_trends.labels,
                datasets: [{
                  label: 'Avg Salary',
                  data: data.charts.salary_trends.data,
                  borderColor: '#1dc9b7',
                  backgroundColor: 'rgba(29, 201, 183, 0.2)',
                  tension: 0.3,
                  fill: true
                }]
              }
            });
          }
        }
      } catch (err) {
        console.error('Failed to load charts', err);
      }
    };

    const loadNotifications = async () => {
      try {
        const token = localStorage.getItem('ppa_token') || localStorage.getItem('token');
        if (!token) return;
        const res = await axios.get('/api/notifications', {
          headers: { Authorization: `Bearer ${token}` }
        });
        notifications.value = res.data || [];
      } catch (err) {
        console.error('Failed to load notifications', err);
      } finally {
        loadingNotifs.value = false;
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
        await Promise.all([
          loadStats(),
          loadCharts(),
          loadNotifications()
        ]);
    });

    return { 
      stats, 
      loading,
      exporting,
      triggerDailyReminders,
      triggerMonthlyReport,
      exportCSV,
      notifications,
      loadingNotifs,
      formatDate
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
