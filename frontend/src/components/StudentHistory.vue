<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Placement History</h1>
        <p class="page-subtitle">Your final placement selections and offers</p>
      </div>
      <div class="d-flex align-items-center gap-3">
        <input type="text" class="form-control" v-model="searchQuery" placeholder="Search by role or company..." style="width: 260px;">
        <button @click="exportCSV" class="btn btn-outline-primary btn-sm" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-download me-1"></i> Export History
        </button>
      </div>
    </div>

    <div class="ppa-card">
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table align-middle mb-0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Salary</th>
              <th>Offer Date</th>
              <th>Status</th>
              <th>Signature</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td>
            </tr>
            <tr v-else-if="filteredPlacements.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">You do not have any final placements yet. Keep applying!</td>
            </tr>
            <tr v-for="app in filteredPlacements" :key="app.id" v-else>
              <td class="fw-medium">{{ app.company_name }}</td>
              <td>{{ app.placement.position || app.job_title }}</td>
              <td class="text-muted"><i class="bi bi-cash me-1 text-primary"></i>{{ app.placement.salary || '—' }}</td>
              <td class="text-muted">{{ app.placement.created_at ? new Date(app.placement.created_at).toLocaleDateString() : '—' }}</td>
              <td>
                <span v-if="app.placement.is_accepted" class="badge bg-success"><i class="bi bi-check-all me-1"></i>Offer Accepted</span>
                <span v-else class="badge bg-warning text-dark"><i class="bi bi-clock-history me-1"></i>Pending Acceptance</span>
              </td>
              <td>
                <span v-if="app.placement.student_signature_path" class="badge bg-info text-dark" title="Signed by candidate">
                  <i class="bi bi-pen me-1"></i>Signed
                </span>
                <span v-else class="text-muted small">Not Signed</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-info me-2 mb-1" @click="viewDetails(app)">View Details</button>
                <button v-if="!app.placement.is_accepted" @click="openAcceptModal(app)" class="btn btn-sm btn-success me-2 mb-1">
                  <i class="bi bi-pen-fill me-1"></i> Sign & Accept
                </button>
                <button @click="downloadOfferLetter(app.placement.id)" class="btn btn-sm btn-outline-primary me-2 mb-1">
                  <i class="bi bi-file-earmark-pdf me-1"></i> Offer
                </button>
                <button v-if="app.placement.is_accepted" @click="downloadAcceptanceLetter(app.placement.id)" class="btn btn-sm btn-outline-success mb-1">
                  <i class="bi bi-file-earmark-check me-1"></i> Acceptance
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Application Detail Modal -->
    <div class="modal fade" id="historyDetailModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header" v-if="selected">
            <div>
              <h5 class="modal-title fw-bold mb-0">{{ selected.job_title }}</h5>
              <p class="text-muted small mb-0">{{ selected.company_name }}<span v-if="selected.company_industry"> · {{ selected.company_industry }}</span></p>
            </div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selected">
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-2">Drive Details</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width:40%">Company</td><td class="fw-medium">{{ selected.company_name }}</td></tr>
                    <tr><td class="text-muted">Industry</td><td>{{ selected.company_industry || '—' }}</td></tr>
                    <tr><td class="text-muted">Role</td><td class="fw-medium">{{ selected.job_title }}</td></tr>
                    <tr><td class="text-muted">Location</td><td>{{ selected.location || '—' }}</td></tr>
                    <tr><td class="text-muted">Salary/yr</td><td>{{ selected.salary || '—' }}</td></tr>
                    <tr><td class="text-muted">Deadline</td><td>{{ selected.application_deadline ? new Date(selected.application_deadline).toLocaleDateString() : '—' }}</td></tr>
                    <tr><td class="text-muted">Min CGPA</td><td>{{ selected.min_cgpa || '—' }}</td></tr>
                    <tr><td class="text-muted">Branches</td><td>{{ formatBranches(selected.eligible_branches) }}</td></tr>
                    <tr><td class="text-muted">Batch</td><td>{{ selected.eligible_year || '—' }}</td></tr>
                    <tr><td class="text-muted">Status</td><td>
                      <span v-if="selected.drive_status === 'approved' && isDriveOpen(selected)" class="status-badge badge-active">Open</span>
                      <span v-else-if="selected.drive_status === 'cancelled'" class="status-badge badge-cancelled">Cancelled</span>
                      <span v-else class="status-badge badge-closed">Closed</span>
                    </td></tr>
                  </tbody>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-2">Application Status</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width:40%">Status</td><td><span :class="'status-badge badge-' + selected.status">{{ selected.status }}</span></td></tr>
                    <tr><td class="text-muted">Applied On</td><td>{{ selected.application_date ? new Date(selected.application_date).toLocaleDateString() : '—' }}</td></tr>
                    <tr v-if="selected.accepted_at"><td class="text-muted">Accepted On</td><td>{{ new Date(selected.accepted_at).toLocaleDateString() }}</td></tr>
                    <tr v-if="selected.feedback"><td class="text-muted">Feedback</td><td class="small">{{ selected.feedback }}</td></tr>
                  </tbody>
                </table>

                <div v-if="selected.placement" class="mt-3 p-3 rounded border border-success bg-light">
                  <h6 class="fw-bold text-success mb-2">Placement Offer</h6>
                  <table class="table table-sm table-borderless mb-0">
                    <tbody>
                      <tr><td class="text-muted" style="width:40%">Position</td><td class="fw-medium">{{ selected.placement.position || selected.job_title }}</td></tr>
                      <tr><td class="text-muted">Package</td><td class="fw-bold text-success">{{ selected.placement.salary || '—' }}</td></tr>
                      <tr><td class="text-muted">Offer Date</td><td>{{ selected.placement.created_at ? new Date(selected.placement.created_at).toLocaleDateString() : '—' }}</td></tr>
                      <tr><td class="text-muted">Accepted</td><td>
                        <span v-if="selected.placement.is_accepted" class="badge bg-success">Yes</span>
                        <span v-else class="badge bg-warning text-dark">Pending</span>
                      </td></tr>
                      <tr v-if="selected.placement.student_signature_path">
                        <td class="text-muted">Your Signature</td>
                        <td>
                          <img :src="selected.placement.student_signature_path" alt="Student Signature" style="max-height: 40px; max-width: 140px; background: #fff; padding: 2px; border: 1px solid #ddd; border-radius: 4px;" />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0">
            <router-link :to="`/student/drives/${selected?.drive_id}`" class="btn btn-outline-primary btn-sm" v-if="selected" @click="closeModal">Go to Drive</router-link>
            <button type="button" class="btn btn-light btn-sm" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Offer Acceptance & Signature Upload Modal -->
    <div class="modal fade" id="acceptOfferModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-primary text-white">
            <div>
              <h5 class="modal-title fw-bold mb-0"><i class="bi bi-pen-fill me-2"></i>Sign & Accept Employment Offer</h5>
              <small class="opacity-75">Upload or draw your signature to formally generate your Letter of Acceptance</small>
            </div>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" :disabled="accepting"></button>
          </div>

          <div class="modal-body p-4" v-if="acceptTarget">
            <!-- Offer Overview Card -->
            <div class="card mb-4 bg-light border-primary border-opacity-25">
              <div class="card-body p-3">
                <div class="row g-2 align-items-center">
                  <div class="col-md-6">
                    <small class="text-muted text-uppercase fw-semibold" style="font-size: 0.75rem;">Company</small>
                    <div class="fw-bold fs-6 text-dark">{{ acceptTarget.company_name }}</div>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted text-uppercase fw-semibold" style="font-size: 0.75rem;">Position Offered</small>
                    <div class="fw-bold fs-6 text-primary">{{ acceptTarget.placement.position || acceptTarget.job_title }}</div>
                  </div>
                  <div class="col-md-6 mt-2">
                    <small class="text-muted text-uppercase fw-semibold" style="font-size: 0.75rem;">Compensation Package</small>
                    <div class="fw-bold text-success">{{ acceptTarget.placement.salary || 'As per offer letter' }}</div>
                  </div>
                  <div class="col-md-6 mt-2">
                    <small class="text-muted text-uppercase fw-semibold" style="font-size: 0.75rem;">Offer Issued On</small>
                    <div class="fw-medium text-dark">{{ acceptTarget.placement.created_at ? new Date(acceptTarget.placement.created_at).toLocaleDateString() : '—' }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Signature Upload / Pad Section -->
            <div class="mb-4">
              <label class="form-label fw-bold d-flex justify-content-between align-items-center">
                <span>Candidate Digital Signature <span class="text-danger">*</span></span>
                <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25">Mandatory</span>
              </label>
              
              <!-- Tab Switch: Upload vs Draw -->
              <ul class="nav nav-pills nav-fill mb-3" id="sigTab" role="tablist">
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: sigMode === 'upload' }" @click="sigMode = 'upload'" type="button">
                    <i class="bi bi-cloud-arrow-up me-1"></i> Upload Image (JPEG, PNG)
                  </button>
                </li>
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: sigMode === 'draw' }" @click="initDrawMode" type="button">
                    <i class="bi bi-pencil-square me-1"></i> Draw Signature
                  </button>
                </li>
                <li class="nav-item" v-if="defaultProfileSig">
                  <button class="nav-link" :class="{ active: sigMode === 'profile' }" @click="useProfileSig" type="button">
                    <i class="bi bi-person-badge me-1"></i> Use Saved Profile Signature
                  </button>
                </li>
              </ul>

              <!-- Mode 1: File Upload -->
              <div v-if="sigMode === 'upload'" class="border rounded-3 p-3 text-center bg-white">
                <div v-if="!signaturePreview" class="py-4">
                  <i class="bi bi-file-earmark-image fs-1 text-muted"></i>
                  <p class="mb-2 mt-1 text-muted">Select or drag & drop your signature image</p>
                  <p class="small text-muted mb-3">Accepted formats: <strong>PNG, JPEG, JPG, WEBP</strong> (Max 5MB)</p>
                  <label class="btn btn-outline-primary btn-sm px-4">
                    <i class="bi bi-folder2-open me-1"></i> Browse Image
                    <input type="file" accept="image/png, image/jpeg, image/jpg, image/webp" @change="onFileSelected" class="d-none">
                  </label>
                </div>
                <div v-else class="py-2">
                  <div class="p-2 border rounded bg-light d-inline-block position-relative">
                    <img :src="signaturePreview" alt="Signature Preview" style="max-height: 90px; max-width: 280px; object-fit: contain;" />
                    <button type="button" @click="clearSignature" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 rounded-circle" style="padding: 2px 6px;" title="Remove signature">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                  <div class="mt-2 text-success small fw-medium">
                    <i class="bi bi-check-circle-fill me-1"></i> Signature image ready
                  </div>
                </div>
              </div>

              <!-- Mode 2: Draw on Canvas -->
              <div v-if="sigMode === 'draw'" class="border rounded-3 p-3 bg-white text-center">
                <p class="text-muted small mb-2">Draw your signature smoothly in the box below using your mouse, trackpad, or finger:</p>
                <div class="border border-2 border-secondary border-dashed rounded bg-light d-inline-block" style="touch-action: none;">
                  <canvas 
                    ref="canvasRef" 
                    width="420" 
                    height="120" 
                    style="cursor: crosshair; display: block;"
                    @mousedown="startDrawing" 
                    @mousemove="draw" 
                    @mouseup="stopDrawing" 
                    @mouseleave="stopDrawing"
                    @touchstart.passive="handleTouchStart"
                    @touchmove.prevent="handleTouchMove"
                    @touchend="stopDrawing"
                  ></canvas>
                </div>
                <div class="mt-2 d-flex justify-content-center gap-2">
                  <button type="button" class="btn btn-sm btn-outline-secondary" @click="clearCanvas">
                    <i class="bi bi-eraser me-1"></i> Clear & Redo
                  </button>
                  <button type="button" class="btn btn-sm btn-primary" @click="captureCanvas">
                    <i class="bi bi-check2 me-1"></i> Use this Signature
                  </button>
                </div>
                <div v-if="drawnCaptured" class="mt-2 text-success small fw-medium">
                  <i class="bi bi-check-circle-fill me-1"></i> Signature captured and ready
                </div>
              </div>

              <!-- Mode 3: Profile Signature -->
              <div v-if="sigMode === 'profile'" class="border rounded-3 p-3 bg-white text-center">
                <p class="text-muted small mb-2">Using your saved profile signature:</p>
                <div class="p-2 border rounded bg-light d-inline-block">
                  <img :src="defaultProfileSig" alt="Profile Signature" style="max-height: 80px; max-width: 250px;" />
                </div>
                <div class="mt-2 text-success small fw-medium">
                  <i class="bi bi-check-circle-fill me-1"></i> Profile signature selected
                </div>
              </div>
            </div>

            <!-- Acceptance Declarations -->
            <div class="form-check mb-2 bg-light p-3 rounded border">
              <input class="form-check-input ms-0 me-2" type="checkbox" id="acceptCheck" v-model="confirmedDeclaration">
              <label class="form-check-label small" for="acceptCheck">
                I formally confirm and accept the employment offer from <strong>{{ acceptTarget.company_name }}</strong> for the role of <strong>{{ acceptTarget.placement.position || acceptTarget.job_title }}</strong>, and agree to the digital affixation of my signature.
              </label>
            </div>
          </div>

          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal" :disabled="accepting">Cancel</button>
            <button 
              type="button" 
              class="btn btn-success btn-sm px-4 fw-bold" 
              @click="submitAcceptance" 
              :disabled="!isSignatureReady || !confirmedDeclaration || accepting"
            >
              <span v-if="accepting" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-check2-circle me-1"></i> Confirm & Sign Offer
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, getCurrentInstance, nextTick } from 'vue';

export default {
  name: 'StudentHistory',
  setup() {
    const placements = ref([]);
    const loading = ref(true);
    const exporting = ref(false);
    const searchQuery = ref('');
    const selected = ref(null);
    let modalInstance = null;
    let acceptModalInstance = null;
    const { proxy } = getCurrentInstance();

    // Acceptance & Signature State
    const acceptTarget = ref(null);
    const sigMode = ref('upload'); // 'upload' | 'draw' | 'profile'
    const signatureFile = ref(null);
    const signaturePreview = ref('');
    const defaultProfileSig = ref('');
    const confirmedDeclaration = ref(false);
    const accepting = ref(false);

    // Canvas Drawing State
    const canvasRef = ref(null);
    const isDrawing = ref(false);
    const drawnCaptured = ref(false);

    const loadHistory = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/student/applications');
        placements.value = res.data.filter(app => app.placement !== null);
        
        // Also fetch profile signature
        try {
          const profileRes = await axios.get('/api/student/profile');
          if (profileRes.data && profileRes.data.signature_path) {
            defaultProfileSig.value = profileRes.data.signature_path;
          }
        } catch (_) {}
      } catch (err) {
        proxy.$toast('Failed to load history.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const filteredPlacements = computed(() => {
      const q = searchQuery.value.toLowerCase();
      if (!q) return placements.value;
      return placements.value.filter(app =>
        app.job_title.toLowerCase().includes(q) ||
        app.company_name.toLowerCase().includes(q) ||
        (app.placement.position && app.placement.position.toLowerCase().includes(q))
      );
    });

    const viewDetails = (app) => {
      selected.value = app;
      if (!modalInstance && window.bootstrap) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('historyDetailModal'));
      }
      if (modalInstance) modalInstance.show();
    };

    const closeModal = () => {
      if (modalInstance) modalInstance.hide();
    };

    const openAcceptModal = (app) => {
      acceptTarget.value = app;
      signatureFile.value = null;
      signaturePreview.value = '';
      drawnCaptured.value = false;
      confirmedDeclaration.value = false;

      if (defaultProfileSig.value) {
        sigMode.value = 'profile';
        signaturePreview.value = defaultProfileSig.value;
      } else {
        sigMode.value = 'upload';
      }

      if (!acceptModalInstance && window.bootstrap) {
        acceptModalInstance = new window.bootstrap.Modal(document.getElementById('acceptOfferModal'));
      }
      if (acceptModalInstance) acceptModalInstance.show();
    };

    const onFileSelected = (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        proxy.$toast('Please select a valid image (PNG, JPG, JPEG, WEBP).', 'error');
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        proxy.$toast('Image size must be less than 5MB.', 'error');
        return;
      }

      signatureFile.value = file;
      const reader = new FileReader();
      reader.onload = (event) => {
        signaturePreview.value = event.target.result;
      };
      reader.readAsDataURL(file);
    };

    const clearSignature = () => {
      signatureFile.value = null;
      signaturePreview.value = '';
    };

    const useProfileSig = () => {
      sigMode.value = 'profile';
      signaturePreview.value = defaultProfileSig.value;
    };

    // Canvas drawing helpers
    const initDrawMode = () => {
      sigMode.value = 'draw';
      nextTick(() => {
        clearCanvas();
      });
    };

    const getCanvasPos = (e) => {
      const canvas = canvasRef.value;
      if (!canvas) return { x: 0, y: 0 };
      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
      const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0] ? e.touches[0].clientY : 0);
      return {
        x: clientX - rect.left,
        y: clientY - rect.top
      };
    };

    const startDrawing = (e) => {
      isDrawing.value = true;
      const canvas = canvasRef.value;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.beginPath();
      const pos = getCanvasPos(e);
      ctx.moveTo(pos.x, pos.y);
      ctx.strokeStyle = '#0F4C81';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    };

    const draw = (e) => {
      if (!isDrawing.value) return;
      const canvas = canvasRef.value;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const pos = getCanvasPos(e);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
    };

    const stopDrawing = () => {
      if (isDrawing.value) {
        isDrawing.value = false;
      }
    };

    const handleTouchStart = (e) => {
      startDrawing(e);
    };

    const handleTouchMove = (e) => {
      draw(e);
    };

    const clearCanvas = () => {
      const canvas = canvasRef.value;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawnCaptured.value = false;
      signaturePreview.value = '';
    };

    const captureCanvas = () => {
      const canvas = canvasRef.value;
      if (!canvas) return;
      const dataUri = canvas.toDataURL('image/png');
      signaturePreview.value = dataUri;
      drawnCaptured.value = true;
      proxy.$toast('Signature captured! Click Confirm to accept.', 'success');
    };

    const isSignatureReady = computed(() => {
      if (sigMode.value === 'upload') return !!signaturePreview.value;
      if (sigMode.value === 'draw') return !!signaturePreview.value;
      if (sigMode.value === 'profile') return !!defaultProfileSig.value;
      return false;
    });

    const submitAcceptance = async () => {
      if (!acceptTarget.value) return;
      if (!isSignatureReady.value) {
        proxy.$toast('Please provide your signature before accepting.', 'error');
        return;
      }
      if (!confirmedDeclaration.value) {
        proxy.$toast('Please acknowledge the declaration checkbox.', 'warning');
        return;
      }

      accepting.value = true;
      const placementId = acceptTarget.value.placement.id;

      try {
        let payload = {};
        if (sigMode.value === 'upload' && signaturePreview.value) {
          payload.signature_data = signaturePreview.value;
        } else if (sigMode.value === 'draw' && signaturePreview.value) {
          payload.signature_data = signaturePreview.value;
        } else if (sigMode.value === 'profile') {
          payload.signature_path = defaultProfileSig.value;
        }

        const res = await axios.put(`/api/student/placements/${placementId}/accept`, payload);
        proxy.$toast(res.data.message || 'Offer accepted and signed successfully!', 'success');
        
        if (acceptModalInstance) {
          acceptModalInstance.hide();
        }

        await loadHistory();
      } catch (err) {
        proxy.$toast(err.response?.data?.error || err.response?.data?.message || 'Failed to accept offer.', 'error');
      } finally {
        accepting.value = false;
      }
    };

    const formatBranches = (branches) => {
      if (!branches) return '—';
      try {
        const arr = typeof branches === 'string' ? JSON.parse(branches) : branches;
        return Array.isArray(arr) ? arr.join(', ') : branches;
      } catch {
        return branches;
      }
    };

    const isDriveOpen = (d) => {
      if (!d || !d.application_deadline) return false;
      return new Date(d.application_deadline) >= new Date();
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

    const downloadOfferLetter = async (placementId) => {
      try {
        const response = await axios.get(`/api/export/offer_letter/${placementId}`, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Offer_Letter_${placementId}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        proxy.$toast('Offer letter downloaded successfully.', 'success');
      } catch (err) {
        let msg = 'Failed to download offer letter.';
        if (err.response && err.response.data instanceof Blob) {
          try {
            const errText = await err.response.data.text();
            const parsed = JSON.parse(errText);
            if (parsed.error) msg = parsed.error;
          } catch(e) {}
        }
        proxy.$toast(msg, 'error');
      }
    };

    const downloadAcceptanceLetter = async (placementId) => {
      try {
        const response = await axios.get(`/api/export/acceptance_letter/${placementId}`, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Acceptance_Letter_${placementId}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        proxy.$toast('Acceptance letter downloaded successfully.', 'success');
      } catch (err) {
        let msg = 'Failed to download acceptance letter.';
        if (err.response && err.response.data instanceof Blob) {
          try {
            const errText = await err.response.data.text();
            const parsed = JSON.parse(errText);
            if (parsed.error) msg = parsed.error;
          } catch(e) {}
        }
        proxy.$toast(msg, 'error');
      }
    };

    onMounted(loadHistory);

    return { 
      placements, loading, exporting, searchQuery, filteredPlacements, selected,
      exportCSV, downloadOfferLetter, downloadAcceptanceLetter,
      viewDetails, closeModal, formatBranches, isDriveOpen,
      acceptTarget, openAcceptModal, sigMode, signaturePreview, defaultProfileSig,
      confirmedDeclaration, accepting, onFileSelected, clearSignature, useProfileSig,
      canvasRef, startDrawing, draw, stopDrawing, handleTouchStart, handleTouchMove,
      clearCanvas, captureCanvas, drawnCaptured, isSignatureReady, submitAcceptance
    };
  }
}
</script>