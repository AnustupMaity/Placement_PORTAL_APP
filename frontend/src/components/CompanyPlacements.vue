<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Final Placements</h1>
        <p class="page-subtitle">Candidates who have been extended offers</p>
      </div>
      <div class="d-flex gap-2 align-items-center">
        <input type="text" class="form-control form-control-sm" placeholder="Search by name or role..." v-model="searchQuery" style="width: 230px;">
        <button @click="exportCSV" class="btn btn-outline-success btn-sm text-nowrap">
          <i class="bi bi-file-earmark-excel me-1"></i> Export to CSV
        </button>
      </div>
    </div>

    <div class="ppa-card mt-4">
      <div v-if="loading" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></div>
      <div v-else-if="placements.length === 0" class="text-muted text-center py-4">No placements found.</div>
      <div class="table-responsive table-wrapper" v-else>
        <table class="table ppa-table mb-0 align-middle">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Role</th>
                <th>Salary</th>
                <th>Offer Date</th>
                <th>Status</th>
                <th>Signature</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filteredPlacements" :key="p.id">
                <td class="fw-bold">{{ p.student_name }}</td>
                <td>{{ p.position }}</td>
                <td>{{ p.salary || 'N/A' }}</td>
                <td class="text-muted">{{ formatDate(p.created_at) }}</td>
                <td>
                  <span class="badge" :class="p.is_accepted ? 'bg-success' : 'bg-warning'">
                    {{ p.is_accepted ? 'Accepted' : 'Pending' }}
                  </span>
                </td>
                <td>
                  <span v-if="p.student_signature_path" class="badge bg-info text-dark">
                    <i class="bi bi-pen me-1"></i>Candidate Signed
                  </span>
                  <span v-else class="text-muted small">Not Signed</span>
                </td>
                <td>
                  <button @click="viewDetails(p)" class="btn btn-sm btn-outline-primary me-2 mb-1" title="View Details">
                    View Details
                  </button>
                  <button @click="downloadOfferLetter(p.id)" class="btn btn-sm btn-outline-secondary me-2 mb-1" title="Download Offer Letter">
                    <i class="bi bi-file-earmark-pdf me-1"></i> Offer Letter
                  </button>
                  <button v-if="p.is_accepted" @click="downloadAcceptanceLetter(p.id)" class="btn btn-sm btn-outline-success mb-1" title="Download Acceptance Letter">
                    <i class="bi bi-file-earmark-check me-1"></i> Acceptance Letter
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    <!-- View Details Modal -->
    <div class="modal fade" id="placementModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title fw-bold mb-0">Placement Details</h5>
              <div class="text-muted small mt-1" v-if="selectedPlacement">
                Candidate: <strong class="text-dark">{{ selectedPlacement.student_name }}</strong>
              </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedPlacement">
            <div class="row g-3">
              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-3">Candidate Details</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width: 130px;">Name</td><td class="fw-medium">{{ selectedPlacement.student_name }}</td></tr>
                    <tr><td class="text-muted">Email</td><td>{{ selectedPlacement.student_email || '—' }}</td></tr>
                    <tr><td class="text-muted">Phone</td><td>{{ selectedPlacement.student_phone || '—' }}</td></tr>
                    <tr><td class="text-muted">Branch</td><td>{{ selectedPlacement.student_branch || '—' }}</td></tr>
                    <tr><td class="text-muted">Skills</td><td>{{ selectedPlacement.student_skills || '—' }}</td></tr>
                    <tr v-if="selectedPlacement.student_resume"><td class="text-muted">Resume</td>
                      <td><a :href="selectedPlacement.student_resume" target="_blank" style="word-break: break-all;" class="text-primary text-decoration-none">{{ selectedPlacement.student_resume }}</a></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="col-md-6">
                <h6 class="fw-bold text-primary mb-3">Placement Details</h6>
                <table class="table table-sm table-borderless mb-0">
                  <tbody>
                    <tr><td class="text-muted" style="width: 130px;">Role</td><td class="fw-medium">{{ selectedPlacement.position }}</td></tr>
                    <tr><td class="text-muted">Salary</td><td class="fw-bold text-success">{{ selectedPlacement.salary || '—' }}</td></tr>
                    <tr><td class="text-muted">Offer Date</td><td>{{ formatDate(selectedPlacement.created_at) }}</td></tr>
                    <tr><td class="text-muted">Status</td>
                      <td>
                        <span class="badge" :class="selectedPlacement.is_accepted ? 'bg-success' : 'bg-warning'">
                          {{ selectedPlacement.is_accepted ? 'Accepted' : 'Pending' }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="selectedPlacement.accepted_at"><td class="text-muted">Accepted Date</td><td>{{ formatDate(selectedPlacement.accepted_at) }}</td></tr>
                    <tr v-if="selectedPlacement.feedback"><td class="text-muted">Feedback</td><td class="small text-muted">{{ selectedPlacement.feedback }}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Signatures Section -->
            <div class="row g-3 mt-3 border-top pt-3">
              <div class="col-md-6">
                <h6 class="fw-bold text-dark mb-2"><i class="bi bi-pen me-1"></i>Candidate Acceptance Signature</h6>
                <div v-if="selectedPlacement.student_signature_path" class="p-2 border rounded bg-light text-center">
                  <img :src="selectedPlacement.student_signature_path" alt="Candidate Signature" style="max-height: 55px; max-width: 200px; object-fit: contain;" />
                  <div class="small text-success mt-1"><i class="bi bi-check-circle-fill me-1"></i>Signed & Verified</div>
                </div>
                <div v-else class="alert alert-secondary small mb-0 py-2">
                  <i class="bi bi-clock me-1"></i>Pending candidate signature & acceptance.
                </div>
              </div>

              <div class="col-md-6">
                <h6 class="fw-bold text-dark mb-2"><i class="bi bi-building me-1"></i>Company Offer Signature</h6>
                <div v-if="selectedPlacement.company_signature_path" class="p-2 border rounded bg-light text-center">
                  <img :src="selectedPlacement.company_signature_path" alt="Company Signature" style="max-height: 55px; max-width: 200px; object-fit: contain;" />
                  <div class="small text-primary mt-1"><i class="bi bi-check-circle-fill me-1"></i>Attached to Offer Letter</div>
                </div>
                <div v-else class="alert alert-light border small mb-0 py-2 text-muted">
                  Standard digital authorization used.
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-light" v-if="selectedPlacement">
            <button v-if="selectedPlacement.is_accepted" @click="downloadAcceptanceLetter(selectedPlacement.id)" class="btn btn-outline-success btn-sm me-auto">
              <i class="bi bi-file-earmark-check me-1"></i> Download Acceptance Letter
            </button>
            <button @click="downloadOfferLetter(selectedPlacement.id)" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-file-earmark-pdf me-1"></i> Download Offer Letter
            </button>
            <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
          </div>    </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';

export default {
  name: 'CompanyPlacements',
  setup() {
    const placements = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const selectedPlacement = ref(null);
    const { proxy } = getCurrentInstance();
    let modalInstance = null;

    const formatDate = (dateString) => {
      if (!dateString) return '—';
      let ds = dateString;
      if (!ds.endsWith('Z') && !ds.includes('+')) ds += 'Z';
      const d = new Date(ds);
      if (isNaN(d)) return '—';
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const filteredPlacements = computed(() => {
      const q = searchQuery.value.toLowerCase();
      if (!q) return placements.value;
      return placements.value.filter(p => 
        p.student_name.toLowerCase().includes(q) || 
        p.position.toLowerCase().includes(q)
      );
    });

    const viewDetails = (placement) => {
      selectedPlacement.value = placement;
      if (!modalInstance) {
        modalInstance = new bootstrap.Modal(document.getElementById('placementModal'));
      }
      modalInstance.show();
    };

    const exportCSV = () => {
      const data = filteredPlacements.value;
      if (data.length === 0) {
        proxy.$toast('No data to export', 'warning');
        return;
      }
      const headers = ['Candidate Name', 'Role', 'Salary', 'Offer Date', 'Status', 'Accepted Date'];
      const rows = data.map(p => [
        `"${p.student_name || ''}"`,
        `"${p.position || ''}"`,
        `"${p.salary || ''}"`,
        `"${formatDate(p.created_at)}"`,
        `"${p.is_accepted ? 'Accepted' : 'Pending'}"`,
        `"${formatDate(p.accepted_at)}"`
      ]);
      const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "placements_export.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    const loadPlacements = async () => {
      try {
        const res = await axios.get('/api/company/placements');
        placements.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load placements.', 'error');
      } finally {
        loading.value = false;
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

    onMounted(loadPlacements);

    return { 
      placements, 
      loading, 
      searchQuery,
      filteredPlacements,
      formatDate,
      exportCSV,
      viewDetails,
      selectedPlacement,
      downloadOfferLetter, 
      downloadAcceptanceLetter 
    };
  }
}
</script>
