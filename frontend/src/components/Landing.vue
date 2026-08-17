<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section text-center">
      <div class="container">
        <div class="hero-badge mb-3">
          <i class="bi bi-stars text-warning me-2"></i>Next-Generation Campus Recruitment Platform
        </div>
        
        <h1 class="hero-title">
          Empowering University Placements &amp; <span class="gradient-text">Career Growth</span>
        </h1>
        
        <p class="hero-subtitle mx-auto">
          A modern, full-stack recruitment ecosystem connecting Students, Corporate Recruiters, and University Placement Cells with digital signatures, live application tracking, and automated offer management.
        </p>

        <!-- CTA Action Buttons -->
        <div class="d-flex justify-content-center align-items-center gap-3 flex-wrap mb-4">
          <router-link to="/register" class="btn btn-gradient btn-lg px-4 py-2">
            <i class="bi bi-rocket-takeoff-fill me-2"></i>Create Account
          </router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg px-4 py-2">
            <i class="bi bi-box-arrow-in-right me-2"></i>Sign In to Portal
          </router-link>
        </div>

        <!-- Highlights Badges -->
        <div class="d-flex justify-content-center gap-2 flex-wrap hero-tags">
          <span class="hero-tag"><i class="bi bi-pen-fill text-info me-1"></i>Digital Signature Capture</span>
          <span class="hero-tag"><i class="bi bi-google text-danger me-1"></i>Google OAuth 2.0</span>
          <span class="hero-tag"><i class="bi bi-file-earmark-pdf-fill text-danger me-1"></i>Automated PDF Offers</span>
          <span class="hero-tag"><i class="bi bi-bell-fill text-warning me-1"></i>Live Notification Alerts</span>
        </div>
      </div>
    </section>

    <!-- Key Metrics / Stats Section -->
    <section class="stats-section py-4 border-bottom">
      <div class="container">
        <div class="row g-4 text-center">
          <div class="col-6 col-md-3">
            <div class="stat-number gradient-text">100%</div>
            <div class="stat-title">Paperless Offers</div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-number gradient-text">3 Portals</div>
            <div class="stat-title">Student, Recruiter &amp; Admin</div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-number gradient-text">&lt; 1 min</div>
            <div class="stat-title">Digital Signature Signing</div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-number gradient-text">Real-Time</div>
            <div class="stat-title">Application Status Stepper</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Role Spotlight Cards Section -->
    <section class="py-5 bg-light">
      <div class="container py-4">
        <div class="text-center mb-5">
          <span class="badge bg-primary bg-opacity-10 text-primary px-3 py-2 rounded-pill fw-bold text-uppercase" style="letter-spacing: 0.05em;">Designed For Everyone</span>
          <h2 class="section-heading mt-2">Tailored Portals for Every Stakeholder</h2>
          <p class="text-muted mx-auto" style="max-width: 600px;">Experience purpose-built tools crafted to make the campus recruitment lifecycle frictionless.</p>
        </div>

        <div class="row g-4">
          <!-- Student Card -->
          <div class="col-md-4">
            <div class="role-card h-100 p-4 bg-white rounded-4 border shadow-sm">
              <div class="role-card-icon bg-primary bg-opacity-10 text-primary mb-3">
                <i class="bi bi-mortarboard-fill fs-2"></i>
              </div>
              <h4 class="fw-bold text-dark mb-2">Student Candidates</h4>
              <p class="text-muted small mb-4">Discover verified campus drives matching your branch and CGPA. Apply effortlessly and track every interview stage.</p>
              
              <ul class="list-unstyled small text-muted mb-4 d-flex flex-column gap-2">
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Browse eligible placement drives</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>5-Step visual application timeline</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Draw or upload signature for offers</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Download official Acceptance Letter PDF</li>
              </ul>

              <router-link to="/register" class="btn btn-outline-primary w-100 mt-auto">
                Join as Student
              </router-link>
            </div>
          </div>

          <!-- Company Card -->
          <div class="col-md-4">
            <div class="role-card h-100 p-4 bg-white rounded-4 border shadow-sm">
              <div class="role-card-icon bg-success bg-opacity-10 text-success mb-3">
                <i class="bi bi-building-fill fs-2"></i>
              </div>
              <h4 class="fw-bold text-dark mb-2">Corporate Recruiters</h4>
              <p class="text-muted small mb-4">Post customized job profiles, screen candidate resumes, manage interview rounds, and issue employment offers.</p>
              
              <ul class="list-unstyled small text-muted mb-4 d-flex flex-column gap-2">
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Publish placement drives with criteria</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Applicant roster filtering &amp; feedback</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Attach company authorized signature</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Track signed student acceptances</li>
              </ul>

              <router-link to="/register" class="btn btn-outline-success w-100 mt-auto">
                Register as Recruiter
              </router-link>
            </div>
          </div>

          <!-- Admin Card -->
          <div class="col-md-4">
            <div class="role-card h-100 p-4 bg-white rounded-4 border shadow-sm">
              <div class="role-card-icon bg-dark bg-opacity-10 text-dark mb-3">
                <i class="bi bi-shield-lock-fill fs-2"></i>
              </div>
              <h4 class="fw-bold text-dark mb-2">Placement Cell (TPO)</h4>
              <p class="text-muted small mb-4">Complete administrative oversight over university recruiters, verified student records, and recruitment metrics.</p>
              
              <ul class="list-unstyled small text-muted mb-4 d-flex flex-column gap-2">
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Company verification &amp; drive approvals</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Student record and eligibility audits</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Placement signature verification repository</li>
                <li><i class="bi bi-check-circle-fill text-success me-2"></i>Automated institutional analytics</li>
              </ul>

              <router-link to="/login" class="btn btn-outline-dark w-100 mt-auto">
                Admin Sign In
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Interactive How It Works Flow -->
    <section class="py-5">
      <div class="container py-4">
        <div class="text-center mb-5">
          <span class="badge bg-info bg-opacity-10 text-info px-3 py-2 rounded-pill fw-bold text-uppercase" style="letter-spacing: 0.05em;">Step-by-Step</span>
          <h2 class="section-heading mt-2">How Campus Placements Work</h2>
        </div>

        <div class="row g-4 text-center">
          <div class="col-md-3">
            <div class="step-card p-3">
              <div class="step-circle bg-primary text-white mx-auto mb-3">1</div>
              <h5 class="fw-bold mb-2">Drive Announcement</h5>
              <p class="text-muted small">Approved companies post placement drives with CTC, job details, and eligibility criteria.</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="step-card p-3">
              <div class="step-circle bg-primary text-white mx-auto mb-3">2</div>
              <h5 class="fw-bold mb-2">Apply in 1-Click</h5>
              <p class="text-muted small">Eligible students submit applications instantly with their verified resumes and credentials.</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="step-card p-3">
              <div class="step-circle bg-primary text-white mx-auto mb-3">3</div>
              <h5 class="fw-bold mb-2">Selection &amp; Offer</h5>
              <p class="text-muted small">Recruiters conduct evaluations and transition candidates to Selected status to extend official offers.</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="step-card p-3">
              <div class="step-circle bg-success text-white mx-auto mb-3">4</div>
              <h5 class="fw-bold mb-2">Digital Signature Acceptance</h5>
              <p class="text-muted small">Students sign offers online via interactive canvas or image upload, generating official signed PDFs.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Banner -->
    <section class="cta-section py-5 text-center text-white">
      <div class="container py-3">
        <h2 class="fw-bold mb-3">Ready to Streamline Your Campus Placements?</h2>
        <p class="text-light opacity-75 mx-auto mb-4" style="max-width: 550px;">
          Join your university placement portal today. Get started in less than two minutes.
        </p>
        <div class="d-flex justify-content-center gap-3 flex-wrap">
          <router-link to="/register" class="btn btn-gradient btn-lg px-4 py-2">
            Create Free Account
          </router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg px-4 py-2">
            Sign In Now
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer py-4 border-top bg-white">
      <div class="container text-center text-muted small">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            &copy; 2026 <strong>Placement Portal Application</strong>. All rights reserved.
          </div>
          <div class="d-flex align-items-center gap-3">
            <span class="badge bg-success bg-opacity-10 text-success"><i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>System Active &amp; Operational</span>
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
  font-family: var(--ppa-font-primary);
  color: var(--ppa-text);
  overflow-x: hidden;
}

.hero-section {
  padding: 5rem 1.5rem 4rem;
  background: radial-gradient(circle at 50% 20%, #1e1b4b 0%, #0f172a 60%, #020617 100%);
  color: #ffffff;
  position: relative;
}

.hero-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 0.45rem 1.15rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin-bottom: 1.25rem;
  max-width: 850px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.15rem;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #94a3b8;
  max-width: 720px;
  margin-bottom: 2.25rem;
  font-family: var(--ppa-font-body);
}

.hero-tags {
  margin-top: 1rem;
}

.hero-tag {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

.stats-section {
  background: #ffffff;
}

.stat-number {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 0.25rem;
}

.stat-title {
  font-size: 0.85rem;
  color: var(--ppa-text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.section-heading {
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--ppa-text);
}

.role-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.role-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--ppa-shadow-lg) !important;
  border-color: #cbd5e1 !important;
}

.role-card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-weight: 800;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.cta-section {
  background: radial-gradient(circle at center, #1e1b4b 0%, #0f172a 100%);
}
</style>
