<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Community & Experiences</h1>
        <p class="page-subtitle">Read and share interview experiences with peers</p>
      </div>
      <div>
        <button v-if="userRole === 'student'" class="btn btn-primary btn-sm shadow-sm" @click="openPostModal">
          <i class="bi bi-pencil-square me-2"></i>Share Experience
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="d-flex align-items-center gap-3 mb-4">
      <div style="width: 250px;">
        <select class="form-select form-select-sm border-primary text-primary fw-medium" v-model="filterCompanyId">
          <option value="">All Companies</option>
          <option v-for="comp in companies" :key="comp.id" :value="comp.id">{{ comp.company_name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="ppa-spinner ppa-spinner-sm"></div>
    </div>

    <div v-else-if="experiences.length === 0" class="text-center py-5 text-muted bg-white border rounded">
      <i class="bi bi-chat-square-text text-light" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No experiences found.</h5>
      <p>Be the first to share your interview experience!</p>
    </div>

    <div class="row g-4" v-else>
      <div class="col-md-6 col-lg-4" v-for="exp in filteredExperiences" :key="exp.id">
        <div class="card h-100 border-0 shadow-sm custom-hover-card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div class="d-flex align-items-center gap-2">
                <img v-if="exp.company_logo" :src="exp.company_logo" alt="logo" style="width:24px; height:24px; object-fit:contain;">
                <i v-else class="bi bi-building text-muted"></i>
                <span class="fw-bold text-primary">{{ exp.company_name }}</span>
              </div>
              <span class="badge bg-light text-muted border" v-if="exp.role">{{ exp.role }}</span>
            </div>
            
            <h5 class="card-title mt-2 fw-bold">{{ exp.title }}</h5>
            <p class="card-text small text-muted text-truncate" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; white-space: normal;">
              {{ stripHtml(exp.content) }}
            </p>
            
          </div>
          <div class="card-footer bg-white border-top-0 pt-0 pb-3 d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white fw-bold" style="width: 28px; height: 28px; font-size: 12px;">
                {{ exp.is_anonymous ? 'A' : (exp.student_name ? exp.student_name.charAt(0) : 'U') }}
              </div>
              <div class="small">
                <div class="fw-medium text-dark lh-1">{{ exp.is_anonymous ? 'Anonymous' : exp.student_name }}</div>
                <div class="text-muted" style="font-size: 0.7rem;">{{ formatDate(exp.created_at) }}</div>
              </div>
            </div>
            <button class="btn btn-sm btn-outline-primary" @click="viewExperience(exp)">Read</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Post Modal -->
    <div class="modal fade" id="postModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-light border-0">
            <h5 class="modal-title fw-bold"><i class="bi bi-pencil-square me-2 text-primary"></i>Share Interview Experience</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="submitPost">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label text-muted small fw-bold">Company *</label>
                  <select class="form-select" v-model="postForm.company_id" required>
                    <option value="" disabled>Select Company</option>
                    <option v-for="comp in companies" :key="comp.id" :value="comp.id">{{ comp.company_name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-muted small fw-bold">Job Role / Profile</label>
                  <input type="text" class="form-control" v-model="postForm.role" placeholder="e.g. Software Engineer">
                </div>
                <div class="col-12">
                  <label class="form-label text-muted small fw-bold">Title *</label>
                  <input type="text" class="form-control" v-model="postForm.title" required placeholder="e.g. SDE 1 Interview Experience at Google">
                </div>
                <div class="col-12">
                  <label class="form-label text-muted small fw-bold">Experience Content *</label>
                  <textarea class="form-control" v-model="postForm.content" rows="8" required placeholder="Describe rounds, questions asked, tips, etc."></textarea>
                </div>
                <div class="col-12">
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="anonSwitch" v-model="postForm.is_anonymous">
                    <label class="form-check-label text-muted" for="anonSwitch">Post Anonymously (Hide your name)</label>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer border-0 bg-light">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary shadow-sm" @click="submitPost" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>Post Experience
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- View Modal -->
    <div class="modal fade" id="viewModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 bg-light pb-2">
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4 pt-2" v-if="selectedExp">
            <div class="d-flex align-items-center gap-3 mb-3 pb-3 border-bottom">
              <img v-if="selectedExp.company_logo" :src="selectedExp.company_logo" style="width: 48px; height: 48px; object-fit: contain;">
              <div v-else class="rounded bg-light text-primary d-flex align-items-center justify-content-center" style="width: 48px; height: 48px; font-size: 24px;">
                <i class="bi bi-building"></i>
              </div>
              <div>
                <h4 class="mb-0 fw-bold">{{ selectedExp.title }}</h4>
                <div class="text-muted small mt-1">
                  {{ selectedExp.company_name }} • {{ selectedExp.role || 'General' }}
                </div>
              </div>
            </div>
            
            <div class="d-flex align-items-center justify-content-between mb-4 bg-light rounded p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white fw-bold" style="width: 32px; height: 32px;">
                  {{ selectedExp.is_anonymous ? 'A' : (selectedExp.student_name ? selectedExp.student_name.charAt(0) : 'U') }}
                </div>
                <span class="fw-medium">{{ selectedExp.is_anonymous ? 'Anonymous Student' : selectedExp.student_name }}</span>
              </div>
              <span class="text-muted small"><i class="bi bi-clock me-1"></i>{{ formatDate(selectedExp.created_at) }}</span>
            </div>

            <div class="experience-content" style="white-space: pre-wrap; line-height: 1.7;">
              {{ selectedExp.content }}
            </div>
          </div>
          <div class="modal-footer border-0">
             <button v-if="userRole === 'admin' && selectedExp" class="btn btn-sm btn-outline-danger me-auto" @click="deleteExp(selectedExp.id)">Delete Post</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';

export default {
  name: 'CommunityBoard',
  setup() {
    const { proxy } = getCurrentInstance();
    const experiences = ref([]);
    const companies = ref([]);
    const loading = ref(true);
    const filterCompanyId = ref('');
    const userRole = ref(localStorage.getItem('ppa_role') || localStorage.getItem('role'));

    // Modals
    let postModalInstance = null;
    let viewModalInstance = null;
    
    const postForm = ref({
      company_id: '',
      role: '',
      title: '',
      content: '',
      is_anonymous: false
    });
    const submitting = ref(false);
    const selectedExp = ref(null);

    const loadData = async () => {
      loading.value = true;
      try {
        const [expRes, compRes] = await Promise.all([
          axios.get('/api/community/experiences'),
          axios.get('/api/student/companies') // assuming any authenticated user can view approved companies
        ]);
        experiences.value = expRes.data;
        // The student/companies endpoint works for students. For admin/company, we might need a generic companies endpoint.
        // As a workaround, we'll fetch from the public-like or existing endpoints if possible, or just extract unique companies from experiences.
        if (compRes.data && Array.isArray(compRes.data)) {
           companies.value = compRes.data;
        } else {
           // extract from experiences
           const compMap = new Map();
           experiences.value.forEach(e => {
             if(e.company_id && e.company_name) compMap.set(e.company_id, {id: e.company_id, company_name: e.company_name});
           });
           companies.value = Array.from(compMap.values());
        }
      } catch (err) {
        // If /api/student/companies fails for non-students, extract from experiences
        try {
           const expRes = await axios.get('/api/community/experiences');
           experiences.value = expRes.data;
           const compMap = new Map();
           experiences.value.forEach(e => {
             if(e.company_id && e.company_name) compMap.set(e.company_id, {id: e.company_id, company_name: e.company_name});
           });
           companies.value = Array.from(compMap.values());
        } catch (e) {
           console.error('Failed to load experiences', e);
        }
      } finally {
        loading.value = false;
      }
    };

    const filteredExperiences = computed(() => {
      let filtered = experiences.value;
      if (filterCompanyId.value) {
        filtered = filtered.filter(e => String(e.company_id) === String(filterCompanyId.value));
      }
      return filtered;
    });

    const openPostModal = () => {
      postForm.value = { company_id: '', role: '', title: '', content: '', is_anonymous: false };
      if (!postModalInstance && window.bootstrap) {
        postModalInstance = new window.bootstrap.Modal(document.getElementById('postModal'));
      }
      if (postModalInstance) postModalInstance.show();
    };

    const submitPost = async () => {
      if (!postForm.value.title || !postForm.value.content || !postForm.value.company_id) {
        proxy.$toast('Please fill all required fields', 'error');
        return;
      }
      submitting.value = true;
      try {
        await axios.post('/api/community/experiences', postForm.value);
        proxy.$toast('Experience shared successfully!', 'success');
        if (postModalInstance) postModalInstance.hide();
        loadData();
      } catch (err) {
        proxy.$toast(err.response?.data?.error || 'Failed to post experience.', 'error');
      } finally {
        submitting.value = false;
      }
    };

    const viewExperience = (exp) => {
      selectedExp.value = exp;
      if (!viewModalInstance && window.bootstrap) {
        viewModalInstance = new window.bootstrap.Modal(document.getElementById('viewModal'));
      }
      if (viewModalInstance) viewModalInstance.show();
    };

    const deleteExp = async (id) => {
      if(!confirm('Delete this post?')) return;
      try {
        await axios.delete(`/api/community/experiences/${id}`);
        proxy.$toast('Deleted', 'success');
        if (viewModalInstance) viewModalInstance.hide();
        loadData();
      } catch (e) {
         proxy.$toast('Failed to delete', 'error');
      }
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const stripHtml = (html) => {
      let tmp = document.createElement("DIV");
      tmp.innerHTML = html;
      return tmp.textContent || tmp.innerText || "";
    };

    onMounted(loadData);

    return {
      experiences,
      companies,
      loading,
      filterCompanyId,
      filteredExperiences,
      userRole,
      openPostModal,
      postForm,
      submitPost,
      submitting,
      viewExperience,
      selectedExp,
      deleteExp,
      formatDate,
      stripHtml
    };
  }
}
</script>

<style scoped>
.custom-hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
}
.custom-hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
}
</style>
