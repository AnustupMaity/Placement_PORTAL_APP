<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Student Dashboard</h1>
        <p class="page-subtitle">Welcome to your placement portal</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <template v-else>
      <div class="row g-4 mb-4 row-cols-2 row-cols-md-3 row-cols-lg-5">
        <div class="col">
          <div class="stat-card stat-blue">
            <div class="stat-icon"><i class="bi bi-send"></i></div>
            <div class="stat-value">{{ stats.total_applications || 0 }}</div>
            <div class="stat-label">Applications Submitted</div>
          </div>
        </div>
        <div class="col">
          <div class="stat-card stat-orange">
            <div class="stat-icon"><i class="bi bi-person-video2"></i></div>
            <div class="stat-value">{{ stats.shortlisted_count || 0 }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
        </div>
        <div class="col">
          <div class="stat-card stat-green">
            <div class="stat-icon"><i class="bi bi-award"></i></div>
            <div class="stat-value">{{ stats.selected_count || 0 }}</div>
            <div class="stat-label">Offers Received</div>
          </div>
        </div>
        <div class="col">
          <div class="stat-card stat-purple">
            <div class="stat-icon"><i class="bi bi-briefcase"></i></div>
            <div class="stat-value">{{ stats.active_drives_count || 0 }}</div>
            <div class="stat-label">Active Drives</div>
          </div>
        </div>
        <div class="col">
          <div class="stat-card stat-red">
            <div class="stat-icon"><i class="bi bi-exclamation-circle"></i></div>
            <div class="stat-value">{{ stats.not_applied_count || 0 }}</div>
            <div class="stat-label">Not Applied Yet</div>
          </div>
        </div>
      </div>
      
      <!-- Advanced Analytics Row -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="ppa-card h-100">
            <div class="card-header bg-primary text-white border-bottom-0"><i class="bi bi-lightning-charge me-2"></i>Application Conversion Rate</div>
            <div class="card-body text-center d-flex flex-column justify-content-center">
              <div class="display-4 fw-bold text-primary mb-2">{{ stats.conversion_rate || 0 }}%</div>
              <p class="text-muted mb-0">of your applications result in an offer.</p>
              <div class="progress mt-3" style="height: 10px;">
                <div class="progress-bar bg-primary" :style="`width: ${stats.conversion_rate || 0}%`"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="ppa-card h-100">
            <div class="card-header bg-dark text-white border-bottom-0"><i class="bi bi-graph-up me-2"></i>CGPA Benchmark</div>
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <div class="small text-muted text-uppercase fw-bold">Your CGPA</div>
                  <div class="fs-3 fw-bold" :class="stats.student?.cgpa >= stats.avg_placed_cgpa ? 'text-success' : 'text-warning'">{{ stats.student?.cgpa || 'N/A' }}</div>
                </div>
                <div class="text-end">
                  <div class="small text-muted text-uppercase fw-bold">Avg Placed CGPA</div>
                  <div class="fs-3 fw-bold text-dark">{{ stats.avg_placed_cgpa || 'N/A' }}</div>
                </div>
              </div>
              <div class="progress" style="height: 10px;">
                <div class="progress-bar bg-success" :style="`width: ${(stats.student?.cgpa / 10) * 100}%`"></div>
              </div>
              <p v-if="stats.student?.cgpa >= stats.avg_placed_cgpa" class="small text-success mt-2 mb-0"><i class="bi bi-check-circle-fill me-1"></i>You are above the placement average!</p>
              <p v-else class="small text-warning mt-2 mb-0"><i class="bi bi-info-circle-fill me-1"></i>Focus on skill-building to stand out.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">Quick Actions</div>
            <div class="card-body flex-grow-1">
              <div class="d-grid gap-2">
                <router-link to="/student/drives" class="btn btn-outline-primary text-start">Browse Placement Drives</router-link>
                <router-link to="/student/companies" class="btn btn-outline-primary text-start">Browse Companies</router-link>
                <router-link to="/student/applications" class="btn btn-outline-primary text-start">My Applications</router-link>
                <router-link to="/student/history" class="btn btn-outline-primary text-start">Placement History</router-link>
                <router-link to="/student/mock-interview" class="btn btn-outline-primary text-start">AI Mock Interview <span class="badge bg-primary ms-2">New</span></router-link>
                <router-link to="/student/profile" class="btn btn-outline-primary text-start">Update Profile</router-link>
                <button @click="exportCSV" class="btn btn-outline-primary text-start" :disabled="exporting">
                  <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                  Export History
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="ppa-card h-100 d-flex flex-column">
            <div class="card-header">My Application Statuses</div>
            <div class="card-body flex-grow-1 text-center d-flex align-items-center justify-content-center">
              <canvas id="studentAppChart" style="max-height: 250px;"></canvas>
            </div>
          </div>
        </div>
      </div>
      <div class="row g-4 mt-1">
        <div class="col-12">
          <div class="ppa-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span>Recent Notifications</span>
              <router-link to="/student/applications" class="btn btn-sm btn-link p-0 text-decoration-none">View All</router-link>
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
  name: 'StudentDashboard',
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
        const res = await axios.get('/api/student/dashboard');
        stats.value = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const loadCharts = async () => {
      try {
        const res = await axios.get('/api/student/analytics');
        const data = res.data;
        await nextTick();

        if (document.getElementById('studentAppChart')) {
          new Chart(document.getElementById('studentAppChart'), {
            type: 'doughnut',
            data: {
              labels: Object.keys(data.applications),
              datasets: [{
                data: Object.values(data.applications),
                backgroundColor: ['#2c63ff', '#ffb822', '#1dc9b7', '#fd3995']
              }]
            }
          });
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

    const exportCSV = async () => {
      exporting.value = true;
      try {
        const res = await axios.post('/api/export/applications');
        
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

    return { stats, loading, exporting, exportCSV, notifications, loadingNotifs, formatDate };
  }
}
</script>

<!--CSS -->
<style scoped>
/* PAGE LAYOUT & BACKGROUND */

/* Main page container */
.ppa-page {
  padding: 2rem 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* TYPOGRAPHY (TEXT & TITLES) */

/* Page Header container */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

/* Main title text */
.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: .25rem;
}

/* Subtitle text */
.page-subtitle {
  color: var(--ppa-text-muted);
  font-size: .9rem;
  margin-bottom: 2rem;
}

/* DASHBOARD CARDS */

/* Base Card Style (Used for Quick Actions, Upcoming Events, etc.) */
.ppa-card {
  background: var(--ppa-surface);
  border: 1px solid var(--ppa-border);
  border-radius: var(--ppa-radius);
  transition: var(--transition);
  overflow: hidden;
}

/* Card header bar */
.ppa-card .card-header {
  background: rgba(0, 0, 0, .03);
  border-bottom: 1px solid var(--ppa-border);
  padding: 1rem 1.25rem;
  font-weight: 600;
  color: var(--ppa-text);
}

/* Card body content area */
.ppa-card .card-body {
  padding: 1.25rem;
}

/* TOP STATISTIC BOXES */

/* Main container for stat boxes */
.stat-card {
  background: var(--ppa-surface);
  border: 1px solid var(--ppa-border);
  border-radius: var(--ppa-radius);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: var(--transition);
}

/* Icon container in stat boxes */
.stat-card .stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--ppa-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin-bottom: 1rem;
}

/* Large number value */
.stat-card .stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: .25rem;
}

/* Small label text below number */
.stat-card .stat-label {
  font-size: .8rem;
  color: var(--ppa-text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* STATISTIC COLORS */

/* Applications box colors */
.stat-blue .stat-icon {
  background: rgba(13, 110, 253, .15);
  color: #0d6efd;
}
.stat-blue .stat-value { color: #0d6efd; }

/* Shortlisted box colors */
.stat-orange .stat-icon {
  background: rgba(253, 126, 20, .15);
  color: #fd7e14;
}
.stat-orange .stat-value { color: #fd7e14; }

/* Offers box colors */
.stat-green .stat-icon {
  background: rgba(25, 135, 84, .15);
  color: #198754;
}
.stat-green .stat-value { color: #198754; }

/* Active Drives box colors */
.stat-purple .stat-icon {
  background: rgba(111, 66, 193, .15);
  color: #6f42c1;
}
.stat-purple .stat-value { color: #6f42c1; }

/* Not Applied Yet box colors */
.stat-red .stat-icon {
  background: rgba(220, 53, 69, .15);
  color: #dc3545;
}
.stat-red .stat-value { color: #dc3545; }
</style>
