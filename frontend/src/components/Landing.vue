<template>
  <div class="landing-page d-flex flex-column" style="min-height: 100vh;">
    <!-- Minimal Header -->
    <header class="d-flex justify-content-between align-items-center p-4">
      <div class="fw-bold fs-5 tracking-tight text-dark">
        Placement Portal
      </div>
      <div>
        <router-link to="/login" class="text-decoration-none fw-medium text-muted me-4 hover-dark">Sign In</router-link>
        <router-link to="/register" class="btn btn-dark btn-sm px-3 fw-medium rounded-pill">Create Account</router-link>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="flex-grow-1 d-flex align-items-center justify-content-center text-center px-3 py-5">
      <div class="hero-container">
        <div class="badge bg-light text-dark border border-secondary border-opacity-25 rounded-pill mb-4 px-3 py-2 fw-medium mx-auto" style="width: fit-content; font-size: 0.85rem;">
          <i class="bi bi-rocket-takeoff me-2"></i> Elevating Campus Recruitment
        </div>
        
        <h1 class="hero-title mb-4">
          Streamlined placements.<br>
          <span class="text-muted">Zero friction.</span>
        </h1>
        
        <p class="hero-subtitle mx-auto mb-5">
          A centralized, intelligent recruitment ecosystem connecting ambitious students, corporate recruiters, and the university placement cell in one unified platform.
        </p>

        <div class="d-flex justify-content-center align-items-center gap-3 flex-wrap">
          <router-link to="/register" class="btn btn-dark btn-lg px-5 py-3 fw-medium rounded-pill shadow-sm">
            Get Started
          </router-link>
          <a href="#features" class="btn btn-outline-secondary border-opacity-50 btn-lg px-5 py-3 fw-medium rounded-pill bg-white hover-bg-light">
            Explore Features
          </a>
        </div>
      </div>
    </section>

    <!-- Key Features Mini-Section (Compact) -->
    <section id="features" class="bg-light border-top py-5">
      <div class="container text-center">
        <div class="row g-4 max-w-4xl mx-auto">
          <div class="col-md-4">
            <div class="p-3">
              <i class="bi bi-robot fs-3 mb-3 text-dark"></i>
              <h5 class="fw-bold text-dark fs-6">AI Matchmaking</h5>
              <p class="small text-muted mb-0">Automated NLP-based resume scoring to connect the right talent with the right opportunities instantly.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-3">
              <i class="bi bi-chat-dots fs-3 mb-3 text-dark"></i>
              <h5 class="fw-bold text-dark fs-6">Real-Time Chat</h5>
              <p class="small text-muted mb-0">Seamless WebSocket messaging between recruiters and candidates for rapid communication.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-3">
              <i class="bi bi-file-earmark-pdf fs-3 mb-3 text-dark"></i>
              <h5 class="fw-bold text-dark fs-6">Automated Resumes</h5>
              <p class="small text-muted mb-0">Dynamic PDF resume generation and standardized corporate offer letter templates.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-4 border-top bg-white">
      <div class="container text-center text-muted" style="font-size: 0.85rem;">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            &copy; 2026 <strong>Placement Portal</strong>. Crafted for Universities.
          </div>
          <div class="d-flex align-items-center gap-3">
            <span class="d-flex align-items-center gap-2"><div class="status-dot"></div> System Operational</span>
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
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: #111827;
  background-color: #ffffff;
}

.tracking-tight {
  letter-spacing: -0.025em;
}

.hero-container {
  max-width: 800px;
}

.hero-title {
  font-size: clamp(3rem, 5vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.04em;
  color: #000000;
}

.hero-subtitle {
  font-size: clamp(1.1rem, 2vw, 1.25rem);
  color: #4b5563;
  line-height: 1.6;
  max-width: 650px;
}

.max-w-4xl {
  max-width: 56rem; /* 896px */
}

.btn-dark {
  background-color: #000000;
  border-color: #000000;
  color: #ffffff;
  transition: all 0.2s ease;
}

.btn-dark:hover {
  background-color: #374151;
  border-color: #374151;
  transform: translateY(-1px);
}

.hover-dark:hover {
  color: #000000 !important;
}

.hover-bg-light:hover {
  background-color: #f9fafb !important;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}
</style>
