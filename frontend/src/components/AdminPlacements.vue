<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">All Placements</h1>
        <p class="page-subtitle">Track final offers and student acceptances across all drives</p>
      </div>
      <button @click="exportCSV" class="btn btn-outline-primary" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-download me-2"></i>Export Placement Data
      </button>
    </div>

    <div class="ppa-card mt-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span>Placement Records</span>
        <input type="text" class="form-control form-control-sm" placeholder="Search placements..." v-model="searchQuery" style="width: 250px;">
      </div>
      <div class="table-responsive table-wrapper">
        <div v-if="loading" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></div>
        <div v-else-if="filteredPlacements.length === 0" class="text-muted text-center py-4">No placements recorded yet.</div>
        <table class="table ppa-table mb-0 align-middle" v-else>
          <thead>
              <tr>
                <th>Candidate</th>
                <th>Company</th>
                <th>Role</th>
                <th>Status</th>
                <th>Signature</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filteredPlacements" :key="p.id">
                <td>
                  <div class="fw-bold">{{ p.student_name }}</div>
                  <small class="text-muted">ID: {{ p.student_id }}</small>
                </td>
                <td>{{ p.company_name }}</td>
                <td>{{ p.position }}</td>
                <td>
                  <span class="badge" :class="p.is_accepted ? 'bg-success' : 'bg-warning'">
                    {{ p.is_accepted ? 'Offer Accepted' : 'Pending Acceptance' }}
                  </span>
                </td>
                <td>
                  <span v-if="p.student_signature_path" class="badge bg-info text-dark">
                    <i class="bi bi-pen me-1"></i>Signed
                  </span>
                  <span v-else class="text-muted small">Not Signed</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-info me-2 mb-1" @click="viewPlacementInfo(p.id)">
                    View Details
                  </button>
                  <button @click="downloadOfferLetter(p.id)" class="btn btn-sm btn-outline-primary me-2 mb-1" title="Download Offer Letter">
                    <i class="bi bi-file-earmark-pdf"></i> Offer
                  </button>
                  <button v-if="p.is_accepted" @click="downloadAcceptanceLetter(p.id)" class="btn btn-sm btn-outline-success mb-1" title="Download Acceptance Letter">
                    <i class="bi bi-file-earmark-check"></i> Acceptance
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
    </div>

    <!-- Placement Info Modal -->
    <div class="modal fade" id="placementInfoModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold">Placement Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body pt-3">
            <div v-if="loadingDetails" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <div v-else-if="selectedPlacement">
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Student Details</h6>
                  <p class="mb-1"><i class="bi bi-person me-2"></i><strong>Name:</strong> {{ selectedPlacement.student.full_name }}</p>
                  <p class="mb-1"><i class="bi bi-person-badge me-2"></i><strong>Roll No:</strong> {{ selectedPlacement.student.roll_number || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-diagram-2 me-2"></i><strong>Branch:</strong> {{ selectedPlacement.student.branch || 'N/A' }}</p>
                  <p class="mb-1"><i class="bi bi-award me-2"></i><strong>CGPA:</strong> {{ selectedPlacement.student.cgpa || 'N/A' }}</p>
                  <p class="mb-1" v-if="selectedPlacement.student.email"><i class="bi bi-envelope me-2"></i><strong>Email:</strong> {{ selectedPlacement.student.email }}</p>
                  <p class="mb-1" v-if="selectedPlacement.student.phone"><i class="bi bi-telephone me-2"></i><strong>Phone:</strong> {{ selectedPlacement.student.phone }}</p>
                  <p class="mb-1 mt-2" v-if="selectedPlacement.student.resume_path">
                    <i class="bi bi-link-45deg me-2"></i><strong>Resume:</strong> 
                    <a :href="selectedPlacement.student.resume_path" target="_blank" style="word-break: break-all;">{{ selectedPlacement.student.resume_path }}</a>
                  </p>
                </div>
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">Drive Details</h6>
                  <p class="mb-1"><i class="bi bi-building me-2"></i><strong>Company:</strong> {{ selectedPlacement.company.company_name }}</p>
                  <p class="mb-1"><i class="bi bi-briefcase me-2"></i><strong>Role:</strong> {{ selectedPlacement.drive.job_title }}</p>
                  <p class="mb-1"><i class="bi bi-geo-alt me-2"></i><strong>Location:</strong> {{ selectedPlacement.drive.location || 'N/A' }}</p>
                  <p class="mb-1" v-if="selectedPlacement.drive.salary"><i class="bi bi-cash-stack me-2"></i><strong>Base Salary:</strong> {{ selectedPlacement.drive.salary }}</p>
                  <p class="mb-1" v-if="selectedPlacement.drive.application_deadline"><i class="bi bi-calendar-x me-2"></i><strong>Deadline:</strong> {{ new Date(selectedPlacement.drive.application_deadline).toLocaleDateString() }}</p>
                </div>
              </div>

              <h6 class="border-top pt-3 text-primary">Offer Information</h6>
              <div class="p-3 bg-light rounded border border-success mb-3">
                <h6 class="fw-bold text-success mb-3"><i class="bi bi-check-circle-fill me-2"></i>Final Placement Offer</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-2"><strong>Application Date:</strong> <br> {{ selectedPlacement.application.application_date ? new Date(selectedPlacement.application.application_date).toLocaleDateString() : 'N/A' }}</p>
                    <p class="mb-0"><strong>Package Offered:</strong> <br> <i class="bi bi-currency-rupee"></i>{{ selectedPlacement.placement.salary || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-2">
                      <strong>Student Response:</strong> <br>
                      <span :class="selectedPlacement.placement.is_accepted ? 'text-success fw-bold' : 'text-warning fw-bold'">
                        {{ selectedPlacement.placement.is_accepted ? 'Offer Accepted' : 'Pending Acceptance' }}
                      </span>
                    </p>
                    <p class="mb-0" v-if="selectedPlacement.placement.accepted_at">
                      <strong>Accepted On:</strong> <br>
                      <span class="small text-dark">{{ new Date(selectedPlacement.placement.accepted_at).toLocaleDateString() }}</span>
                    </p>
                  </div>
                </div>

                <!-- Signatures Preview in Admin Modal -->
                <div class="row g-2 mt-2 pt-2 border-top">
                  <div class="col-md-6">
                    <small class="fw-bold text-dark d-block mb-1">Student Acceptance Signature:</small>
                    <div v-if="selectedPlacement.placement.student_signature_path" class="p-1 border rounded bg-white text-center">
                      <img :src="selectedPlacement.placement.student_signature_path" alt="Student Signature" style="max-height: 45px; max-width: 160px; object-fit: contain;" />
                    </div>
                    <span v-else class="text-muted small">Not signed yet</span>
                  </div>

                  <div class="col-md-6">
                    <small class="fw-bold text-dark d-block mb-1">Company Offer Signature:</small>
                    <div v-if="selectedPlacement.placement.company_signature_path" class="p-1 border rounded bg-white text-center">
                      <img :src="selectedPlacement.placement.company_signature_path" alt="Company Signature" style="max-height: 45px; max-width: 160px; object-fit: contain;" />
                    </div>
                    <span v-else class="text-muted small">Standard authorization</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0">
            <button v-if="selectedPlacement?.placement?.is_accepted" @click="downloadAcceptanceLetter(selectedPlacement.placement.id)" class="btn btn-outline-success btn-sm me-auto">
              <i class="bi bi-file-earmark-check me-1"></i> Acceptance Letter
            </button>
            <button v-if="selectedPlacement?.placement" @click="downloadOfferLetter(selectedPlacement.placement.id)" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-file-earmark-pdf me-1"></i> Offer Letter
            </button>
            <button type="button" class="btn btn-light btn-sm" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance, computed } from 'vue';

export default {
  name: 'AdminPlacements',
  setup() {
    const placements = ref([]);
    const loading = ref(true);
    const exporting = ref(false);
    const searchQuery = ref('');
    const { proxy } = getCurrentInstance();
    
    // Modal state
    const selectedPlacement = ref(null);
    const loadingDetails = ref(false);
    let modalInstance = null;

    const loadPlacements = async () => {
      try {
        const res = await axios.get('/api/admin/placements');
        placements.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load placements.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const viewPlacementInfo = async (id) => {
      selectedPlacement.value = null;
      loadingDetails.value = true;
      
      if (!modalInstance) {
        modalInstance = new window.bootstrap.Modal(document.getElementById('placementInfoModal'));
      }
      modalInstance.show();

      try {
        const res = await axios.get(`/api/admin/placements/${id}/details`);
        selectedPlacement.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load placement details.', 'error');
        modalInstance.hide();
      } finally {
        loadingDetails.value = false;
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
        proxy.$toast('Offer letter downloaded.', 'success');
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
        proxy.$toast('Acceptance letter downloaded.', 'success');
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

    const filteredPlacements = computed(() => {
      if (!searchQuery.value) return placements.value;
      const q = searchQuery.value.toLowerCase();
      return placements.value.filter(p => 
        (p.student_name && p.student_name.toLowerCase().includes(q)) ||
        (p.company_name && p.company_name.toLowerCase().includes(q)) ||
        (p.position && p.position.toLowerCase().includes(q))
      );
    });

    onMounted(loadPlacements);

    return { 
      placements, 
      loading, 
      exporting,
      searchQuery, 
      filteredPlacements, 
      downloadOfferLetter, 
      downloadAcceptanceLetter,
      viewPlacementInfo,
      exportCSV,
      selectedPlacement,
      loadingDetails
    };
  }
}
</script>
