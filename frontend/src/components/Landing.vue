<template>
  <div class="landing-page d-flex flex-column" style="min-height: 100vh;">
    <!-- Hero Section -->
    <section class="hero-section flex-grow-1 d-flex align-items-center text-center">
      <div class="container">
        <h1 class="hero-title mb-4">
          Placement Portal
        </h1>
        
        <p class="hero-subtitle mx-auto mb-5">
          A centralized recruitment ecosystem connecting Students, Corporate Recruiters, and the University Placement Cell.
        </p>

        <!-- CTA Action Buttons -->
        <div class="d-flex justify-content-center align-items-center gap-3 flex-wrap">
          <router-link to="/register" class="btn btn-primary btn-lg px-4 py-2 fw-semibold">
            Create Account
          </router-link>
          <router-link to="/login" class="btn btn-outline-primary btn-lg px-4 py-2 fw-semibold">
            Sign In to Portal
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer py-4 border-top bg-white mt-auto">
      <div class="container text-center text-muted small">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            &copy; 2026 <strong>Placement Portal Application</strong>. All rights reserved.
          </div>
          <div class="d-flex align-items-center gap-3">
            <span class="badge bg-success bg-opacity-10 text-success"><i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>System Operational</span>
            <router-link to="/login" class="text-decoration-none text-muted">Login</router-link>
            <router-link to="/register" class="text-decoration-none text-muted">Register</router-link>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'Landing'
}
</script>

<style scoped>
.landing-page {
  font-family: 'Inter', sans-serif;
  color: #334155;
  background-color: #f8fafc;
}

.hero-section {
  background-color: #ffffff;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: #475569;
  max-width: 600px;
}

.btn-primary {
  background-color: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

.btn-outline-primary {
  color: #2563eb;
  border-color: #2563eb;
}

.btn-outline-primary:hover {
  background-color: #eff6ff;
  color: #1d4ed8;
  border-color: #1d4ed8;
}
</style>
