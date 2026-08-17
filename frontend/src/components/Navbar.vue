<template>
  <nav class="navbar navbar-expand-lg ppa-navbar">
    <div class="container-fluid">
      <!-- Brand Logo Mark & Name -->
      <router-link class="navbar-brand" to="/">
        <div class="ppa-brand-icon">
          <i class="bi bi-mortarboard-fill"></i>
        </div>
        <span>Placement Portal</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#ppaNavbar">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="ppaNavbar">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="user">
          
          <!-- Admin Links -->
          <template v-if="user.role === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin"><i class="bi bi-grid me-1"></i> Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/companies"><i class="bi bi-building me-1"></i> Companies</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/students"><i class="bi bi-people me-1"></i> Students</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/drives"><i class="bi bi-briefcase me-1"></i> Drives</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/applications"><i class="bi bi-file-earmark-text me-1"></i> Applications</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/placements"><i class="bi bi-award me-1"></i> Placements</router-link>
            </li>
          </template>

          <!-- Company Links -->
          <template v-else-if="user.role === 'company'">
            <li class="nav-item">
              <router-link class="nav-link" to="/company"><i class="bi bi-grid me-1"></i> Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/company/drives"><i class="bi bi-briefcase me-1"></i> My Drives</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/company/applications"><i class="bi bi-people me-1"></i> Applicants</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/company/placements"><i class="bi bi-award me-1"></i> Placements</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/company/profile"><i class="bi bi-building me-1"></i> Profile</router-link>
            </li>
          </template>

          <!-- Student Links -->
          <template v-else-if="user.role === 'student'">
            <li class="nav-item">
              <router-link class="nav-link" to="/student"><i class="bi bi-grid me-1"></i> Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/companies"><i class="bi bi-building me-1"></i> Companies</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/drives"><i class="bi bi-briefcase me-1"></i> Placement Drives</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/applications"><i class="bi bi-file-earmark-text me-1"></i> My Applications</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/history"><i class="bi bi-award me-1"></i> Offers & History</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/profile"><i class="bi bi-person me-1"></i> Profile</router-link>
            </li>
          </template>
        </ul>

        <div class="d-flex align-items-center gap-2 ms-auto">
          <template v-if="user">
            <!-- Global Search Bar -->
            <form v-if="user.role === 'admin' || user.role === 'student'" class="d-none d-md-flex me-1" @submit.prevent="handleGlobalSearch">
              <div class="input-group input-group-sm">
                <input type="text" class="form-control form-control-sm" placeholder="Quick search..." v-model="globalSearchQuery" style="width: 140px;">
                <button class="btn btn-outline-secondary btn-sm bg-light" type="submit"><i class="bi bi-search"></i></button>
              </div>
            </form>

            <!-- Notifications Center Dropdown -->
            <div class="dropdown me-2">
              <button class="notification-btn dropdown-toggle no-arrow" type="button" data-bs-toggle="dropdown" aria-expanded="false" @click="loadNotifications">
                <i class="bi bi-bell-fill"></i>
                <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
              </button>
              <div class="dropdown-menu dropdown-menu-end notification-dropdown shadow-lg">
                <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-light">
                  <h6 class="mb-0 fw-bold"><i class="bi bi-bell me-2"></i>Notifications</h6>
                  <span class="badge bg-primary rounded-pill small">{{ notifications.length }} recent</span>
                </div>
                <div v-if="loadingNotifs" class="text-center py-4">
                  <span class="spinner-border spinner-border-sm text-primary"></span>
                </div>
                <div v-else-if="notifications.length === 0" class="text-center py-4 text-muted small">
                  <i class="bi bi-check-circle fs-3 d-block mb-1 text-success"></i>
                  No new notifications. You're all caught up!
                </div>
                <div v-else>
                  <router-link 
                    v-for="n in notifications" 
                    :key="n.id" 
                    :to="n.link || '#'" 
                    class="notification-item"
                    :class="{ unread: n.unread }"
                  >
                    <div class="d-flex align-items-start gap-2">
                      <i class="bi fs-5" :class="{
                        'bi-award-fill text-warning': n.type === 'offer',
                        'bi-briefcase-fill text-primary': n.type === 'drive',
                        'bi-info-circle-fill text-info': n.type === 'status',
                        'bi-building-fill text-success': n.type === 'company'
                      }"></i>
                      <div>
                        <div class="fw-bold small text-dark mb-0">{{ n.title }}</div>
                        <div class="small text-muted mb-1">{{ n.message }}</div>
                        <span class="text-muted" style="font-size: 0.7rem;">{{ n.time ? new Date(n.time).toLocaleDateString() : 'Today' }}</span>
                      </div>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Profile Dropdown -->
            <div class="dropdown">
              <button class="btn btn-link text-decoration-none dropdown-toggle p-0 d-flex align-items-center gap-2" type="button" data-bs-toggle="dropdown">
                <div class="ppa-avatar">{{ user.username ? user.username.charAt(0).toUpperCase() : 'U' }}</div>
                <div class="d-none d-md-block text-start" style="line-height: 1.2;">
                  <div class="fw-bold text-dark small">{{ user.username }}</div>
                  <span class="badge bg-secondary bg-opacity-10 text-primary border border-primary border-opacity-25" style="font-size: 0.65rem; text-transform: uppercase;">
                    {{ user.role }}
                  </span>
                </div>
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm mt-2">
                <li v-if="user.role !== 'admin'">
                  <router-link class="dropdown-item" :to="user.role === 'student' ? '/student/profile' : '/company/profile'">
                    <i class="bi bi-person me-2 text-primary"></i>My Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item text-danger fw-semibold" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right me-2"></i>Sign Out
                  </a>
                </li>
              </ul>
            </div>
          </template>

          <template v-else>
            <router-link class="btn btn-outline-primary btn-sm me-2" to="/login">Sign In</router-link>
            <router-link class="btn btn-gradient btn-sm" to="/register">Create Account</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'Navbar',
  setup() {
    const user = ref(null);
    const router = useRouter();
    const globalSearchQuery = ref('');
    const notifications = ref([]);
    const unreadCount = ref(0);
    const loadingNotifs = ref(false);

    const loadUser = () => {
      const u = localStorage.getItem('ppa_user');
      user.value = u ? JSON.parse(u) : null;
      if (user.value) {
        loadNotifications();
      }
    };

    const loadNotifications = async () => {
      if (!user.value) return;
      loadingNotifs.value = true;
      try {
        const res = await axios.get('/api/notifications');
        notifications.value = res.data.notifications || [];
        unreadCount.value = res.data.unread_count || 0;
      } catch (err) {
        // silent fail
      } finally {
        loadingNotifs.value = false;
      }
    };

    const handleGlobalSearch = () => {
      if (!globalSearchQuery.value || !user.value) return;
      if (user.value.role === 'admin') {
        router.push({ path: '/admin/students', query: { q: globalSearchQuery.value } });
      } else if (user.value.role === 'student') {
        router.push({ path: '/student/drives', query: { q: globalSearchQuery.value } });
      }
      globalSearchQuery.value = '';
    };

    const logout = () => {
      localStorage.removeItem('ppa_token');
      localStorage.removeItem('ppa_user');
      localStorage.removeItem('token');
      user.value = null;
      window.dispatchEvent(new Event('user-logged-out'));
      router.push('/login');
    };

    onMounted(() => {
      loadUser();
      window.addEventListener('storage', loadUser);
      window.addEventListener('user-logged-in', loadUser);
      window.addEventListener('user-logged-out', loadUser);
    });

    onUnmounted(() => {
      window.removeEventListener('user-logged-in', loadUser);
      window.removeEventListener('user-logged-out', loadUser);
    });

    return {
      user, logout, globalSearchQuery, handleGlobalSearch,
      notifications, unreadCount, loadingNotifs, loadNotifications
    };
  }
}
</script>

<style scoped>
.no-arrow::after {
  display: none !important;
}
</style>
