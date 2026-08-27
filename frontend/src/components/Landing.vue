<template>
  <div class="landing-page d-flex flex-column" style="min-height: 100vh;">
    <!-- Animated Background -->
    <div class="animated-bg"></div>

    <!-- Minimal Header -->
    <header class="d-flex justify-content-between align-items-center p-4 position-relative z-1">
      <div class="fw-bold fs-5 tracking-tight text-dark d-flex align-items-center gap-2">
        <div class="logo-circle"></div> Placement Portal
      </div>
      <div>
        <router-link to="/login" class="text-decoration-none fw-medium text-dark me-4 hover-opacity">Sign In</router-link>
        <router-link to="/register" class="btn btn-dark btn-sm px-4 fw-medium rounded-pill shadow-sm">Create Account</router-link>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="flex-grow-1 d-flex align-items-center justify-content-center text-center px-3 py-5 position-relative z-1">
      <div class="hero-container">
        <div class="badge-pill mb-4 mx-auto pulse-animation">
          <i class="bi bi-stars me-2 text-warning"></i> Next-Gen Campus Placements
        </div>
        
        <h1 class="hero-title mb-4">
          Streamlined placements.<br>
          <span class="text-gradient">Zero friction.</span>
        </h1>
        
        <p class="hero-subtitle mx-auto mb-5 text-dark opacity-75">
          A centralized, intelligent recruitment ecosystem connecting ambitious students, corporate recruiters, and the university placement cell in one unified platform.
        </p>

        <div class="d-flex justify-content-center align-items-center gap-3 flex-wrap">
          <router-link to="/register" class="btn btn-dark btn-lg px-5 py-3 fw-medium rounded-pill shadow hover-lift">
            Start Your Journey
          </router-link>
          <a href="#features" class="btn btn-white btn-lg px-5 py-3 fw-medium rounded-pill shadow-sm hover-lift">
            Explore Features
          </a>
        </div>
      </div>
    </section>

    <!-- Key Features Mini-Section (Compact) -->
    <section id="features" class="py-5 position-relative z-1">
      <div class="container text-center">
        <div class="row g-4 max-w-4xl mx-auto">
          <div class="col-md-4">
            <div class="feature-card p-4 h-100">
              <div class="icon-box mb-3"><i class="bi bi-robot fs-4 text-dark"></i></div>
              <h5 class="fw-bold text-dark fs-6">AI Matchmaking</h5>
              <p class="small text-muted mb-0">Automated NLP-based resume scoring to connect the right talent with the right opportunities instantly.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 h-100">
              <div class="icon-box mb-3"><i class="bi bi-chat-dots fs-4 text-dark"></i></div>
              <h5 class="fw-bold text-dark fs-6">Real-Time Chat</h5>
              <p class="small text-muted mb-0">Seamless WebSocket messaging between recruiters and candidates for rapid communication.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 h-100">
              <div class="icon-box mb-3"><i class="bi bi-file-earmark-pdf fs-4 text-dark"></i></div>
              <h5 class="fw-bold text-dark fs-6">Automated Resumes</h5>
              <p class="small text-muted mb-0">Dynamic PDF resume generation and standardized corporate offer letter templates.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-4 position-relative z-1" style="background: transparent;">
      <div class="container text-center text-dark opacity-75" style="font-size: 0.85rem;">
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
  position: relative;
  overflow-x: hidden;
  background-color: #f8fafc;
}

.animated-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 15% 50%, rgba(220, 252, 231, 0.4), transparent 50%),
              radial-gradient(circle at 85% 30%, rgba(219, 234, 254, 0.4), transparent 50%),
              radial-gradient(circle at 50% 80%, rgba(243, 232, 255, 0.4), transparent 50%);
  z-index: 0;
  animation: bgShift 15s ease-in-out infinite alternate;
}

@keyframes bgShift {
  0% { transform: scale(1); }
  100% { transform: scale(1.05) translate(20px, -20px); }
}

.logo-circle {
  width: 24px; height: 24px;
  background: #000;
  border-radius: 50%;
  display: inline-block;
}

.tracking-tight {
  letter-spacing: -0.025em;
}

.hero-container {
  max-width: 800px;
}

.badge-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #111827;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0,0,0,0.05);
  backdrop-filter: blur(10px);
  border-radius: 9999px;
}

.pulse-animation {
  animation: subtlePulse 3s infinite;
}

@keyframes subtlePulse {
  0% { box-shadow: 0 0 0 0 rgba(0,0,0,0.05); }
  70% { box-shadow: 0 0 0 10px rgba(0,0,0,0); }
  100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); }
}

.hero-title {
  font-size: clamp(3rem, 5vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.04em;
  color: #000000;
}

.text-gradient {
  background: linear-gradient(135deg, #111827 0%, #4b5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: clamp(1.1rem, 2vw, 1.25rem);
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-white {
  background-color: #ffffff;
  border-color: rgba(0,0,0,0.1);
  color: #111827;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
}

.hover-opacity:hover {
  opacity: 0.7;
}

.feature-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 16px;
  transition: transform 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
}

.icon-box {
  width: 48px; height: 48px;
  background: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}
</style>
