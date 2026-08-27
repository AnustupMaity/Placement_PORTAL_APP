<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Institute Settings</h1>
        <p class="page-subtitle">Manage global portal settings and institute details</p>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-8">
        <div class="ppa-card">
          <div class="card-header border-bottom-0 pb-0">
            <h5 class="fw-bold mb-0">Institute Details</h5>
          </div>
          <div class="card-body pt-3">
            <div v-if="loading" class="text-center py-4">
              <span class="ppa-spinner ppa-spinner-sm"></span>
            </div>
            <form v-else @submit.prevent="updateSettings">
              <div class="row g-4">
                
                <div class="col-md-12 text-center mb-3">
                  <div class="position-relative d-inline-block">
                    <img v-if="form.institute_logo_url" :src="form.institute_logo_url" alt="Institute Logo" class="img-thumbnail rounded-circle" style="width: 120px; height: 120px; object-fit: contain; border-width: 2px;">
                    <div v-else class="img-thumbnail rounded-circle bg-light d-flex align-items-center justify-content-center text-primary border-2" style="width: 120px; height: 120px; font-size: 2.5rem;">
                      <i class="bi bi-bank"></i>
                    </div>
                  </div>
                  <div class="mt-3">
                    <label class="btn btn-outline-primary btn-sm rounded-pill fw-medium px-4">
                      <i class="bi bi-camera me-2"></i>Change Logo
                      <input type="file" class="d-none" accept="image/*" @change="uploadLogo">
                    </label>
                  </div>
                </div>

                <div class="col-md-12">
                  <label class="form-label text-muted small fw-bold">Institute Name</label>
                  <input type="text" class="form-control" v-model="form.institute_name" placeholder="e.g. ABC Institute of Technology">
                </div>
                
                <div class="col-md-12">
                  <label class="form-label text-muted small fw-bold">Institute Address</label>
                  <textarea class="form-control" v-model="form.institute_address" rows="3" placeholder="Enter full address..."></textarea>
                </div>
                
                <div class="col-12 mt-4">
                  <button type="submit" class="btn btn-primary w-100" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    Save Settings
                  </button>
                </div>

              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance } from 'vue';

export default {
  name: 'AdminProfile',
  setup() {
    const { proxy } = getCurrentInstance();
    const loading = ref(true);
    const saving = ref(false);
    
    const form = ref({
      institute_name: '',
      institute_address: '',
      institute_logo_url: ''
    });

    const loadSettings = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/admin/profile');
        if (res.data) {
           form.value.institute_name = res.data.institute_name || '';
           form.value.institute_address = res.data.institute_address || '';
           form.value.institute_logo_url = res.data.institute_logo_url || '';
        }
      } catch (err) {
        proxy.$toast('Failed to load institute settings', 'error');
      } finally {
        loading.value = false;
      }
    };

    const updateSettings = async () => {
      saving.value = true;
      try {
        await axios.put('/api/admin/profile', form.value);
        proxy.$toast('Settings updated successfully', 'success');
      } catch (err) {
        proxy.$toast('Failed to update settings', 'error');
      } finally {
        saving.value = false;
      }
    };

    const uploadLogo = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        proxy.$toast('Please select a valid image file', 'error');
        return;
      }

      if (file.size > 2 * 1024 * 1024) {
        proxy.$toast('File size must be under 2MB', 'error');
        return;
      }

      const formData = new FormData();
      formData.append('image', file);

      try {
        const res = await axios.post('/api/upload/image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        form.value.institute_logo_url = res.data.url;
        proxy.$toast('Logo uploaded successfully. Remember to save settings.', 'info');
      } catch (err) {
        proxy.$toast('Failed to upload logo', 'error');
      }
      
      event.target.value = '';
    };

    onMounted(loadSettings);

    return {
      form,
      loading,
      saving,
      updateSettings,
      uploadLogo
    };
  }
}
</script>
