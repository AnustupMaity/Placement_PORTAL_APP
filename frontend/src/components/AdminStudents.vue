<template>
  <div class="ppa-page">
    <div class="section-header">
      <div>
        <h1 class="page-title">Manage Students</h1>
        <p class="page-subtitle">View and manage student profiles</p>
      </div>
    </div>

    <div class="ppa-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span>Registered Students</span>
        <div class="input-group input-group-sm" style="max-width: 250px;">
          <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" placeholder="Search students..." v-model="searchQuery">
        </div>
      </div>
      <div class="table-responsive table-wrapper">
        <table class="table ppa-table mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Branch</th>
              <th>Year</th>
              <th>CGPA</th>
              <th>Blacklisted</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="7" class="text-center py-4"><span class="ppa-spinner ppa-spinner-sm"></span></td></tr>
            <tr v-else-if="filteredStudents.length === 0"><td colspan="7" class="text-center py-4 text-muted">No students found.</td></tr>
            <tr v-for="s in filteredStudents" :key="s.id" v-else>
              <td>#{{ s.id }}</td>
              <td class="fw-medium">{{ s.full_name }}</td>
              <td>{{ s.branch || '-' }}</td>
              <td>{{ s.year || '-' }}</td>
              <td>{{ s.cgpa ? s.cgpa.toFixed(2) : '-' }}</td>
              <td>
                <span v-if="s.is_blacklisted" class="badge bg-danger rounded-pill">Yes</span>
                <span v-else class="text-muted small">No</span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button @click="viewStudentInfo(s.id)" class="btn btn-sm btn-outline-info" title="View Details">
                    <i class="bi bi-info-circle me-1"></i> View Details
                  </button>
                  <button @click="toggleBlacklist(s.id)" class="btn btn-sm" :class="s.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'" :title="s.is_blacklisted ? 'Unblacklist' : 'Blacklist'">
                    <i class="bi bi-slash-circle"></i>
                  </button>
                  <button @click="deleteStudent(s.id)" class="btn btn-sm btn-outline-danger" title="Delete Student">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Student Info Modal -->
    <div class="modal fade" id="studentInfoModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedStudent?.full_name }} 
              <span v-if="selectedStudent?.is_blacklisted" class="badge bg-danger ms-2">Blacklisted</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedStudent">
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Profile Details</h6>
                <p class="mb-1"><i class="bi bi-person-badge me-2"></i><strong>Roll No:</strong> {{ selectedStudent.roll_number || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-diagram-2 me-2"></i><strong>Branch:</strong> {{ selectedStudent.branch || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-calendar me-2"></i><strong>Grad Year:</strong> {{ selectedStudent.year || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-award me-2"></i><strong>CGPA:</strong> {{ selectedStudent.cgpa || 'N/A' }}</p>
                <p class="mb-1" v-if="selectedStudent.skills"><i class="bi bi-tools me-2"></i><strong>Skills:</strong> {{ selectedStudent.skills }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Contact Information</h6>
                <p class="mb-1"><i class="bi bi-envelope me-2"></i><strong>Email:</strong> {{ selectedStudent.email || 'N/A' }}</p>
                <p class="mb-1"><i class="bi bi-telephone me-2"></i><strong>Phone:</strong> {{ selectedStudent.phone || 'N/A' }}</p>
                <p class="mb-1 mt-2" v-if="selectedStudent.resume_path">
                  <i class="bi bi-link-45deg me-2"></i><strong>Resume:</strong> 
                  <a :href="selectedStudent.resume_path" target="_blank" style="word-break: break-all;">
                    {{ selectedStudent.resume_path }}
                  </a>
                </p>
              </div>
            </div>
            
            <h6 class="border-top pt-3 text-primary">Application History</h6>
            <div v-if="loadingDetails" class="text-center py-3"><span class="ppa-spinner ppa-spinner-sm"></span></div>
            <div v-else-if="studentApplications.length === 0" class="text-muted small">No applications found for this student.</div>
            <div v-else class="list-group">
              <div v-for="app in studentApplications" :key="app.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <div>
                    <div class="fw-bold">{{ app.drive_title }} <span class="text-muted fw-normal">at</span> {{ app.company_name }}</div>
                    <div class="small text-muted"><i class="bi bi-clock me-1"></i>Applied: {{ new Date(app.date_applied).toLocaleDateString() }}</div>
                  </div>
                  <span class="badge" :class="'badge-' + app.status">{{ app.status }}</span>
                </div>
                <div v-if="app.feedback" class="small text-muted mb-2"><i class="bi bi-chat-text me-1"></i>Feedback: {{ app.feedback }}</div>
                <!-- Placement Details if Selected -->
                <div v-if="app.placement" class="mt-2 p-2 bg-light rounded small border border-success">
                  <div class="fw-medium text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i>Placement Offer Received</div>
                  <div><strong>Role:</strong> {{ app.placement.position || 'N/A' }}</div>
                  <div><strong>Package:</strong> <i class="bi bi-currency-rupee"></i>{{ app.placement.salary || 'N/A' }}</div>
                  <div><strong>Offer Date:</strong> {{ app.placement.created_at ? new Date(app.placement.created_at).toLocaleDateString() : 'N/A' }}</div>
                  <div class="mt-2">
                    <span class="badge" :class="app.placement.is_accepted ? 'bg-success' : 'bg-warning'">
                      {{ app.placement.is_accepted ? 'Student Accepted Offer' : 'Pending Acceptance' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance, computed } from 'vue';

export default {
  name: 'AdminStudents',
  setup() {
    const students = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const selectedStudent = ref(null);
    const studentApplications = ref([]);
    const loadingDetails = ref(false);
    const { proxy } = getCurrentInstance();

    const loadStudents = async () => {
      loading.value = true;
      try {
        const res = await axios.get('/api/admin/students');
        students.value = res.data;
      } catch (err) {
        proxy.$toast('Failed to load students.', 'error');
      } finally {
        loading.value = false;
      }
    };

    const toggleBlacklist = async (id) => {
      try {
        await axios.put(`/api/admin/students/${id}/blacklist`);
        proxy.$toast('Student blacklist status updated.', 'success');
        loadStudents();
      } catch (err) {
        proxy.$toast('Failed to update blacklist.', 'error');
      }
    };

    const deleteStudent = async (id) => {
      if (!confirm('Are you sure you want to permanently remove this student?')) return;
      try {
        await axios.delete(`/api/admin/students/${id}`);
        proxy.$toast('Student deleted successfully.', 'success');
        loadStudents();
      } catch (err) {
        proxy.$toast('Failed to delete student.', 'error');
      }
    };

    const filteredStudents = computed(() => {
      if (!searchQuery.value) return students.value;
      const q = searchQuery.value.toLowerCase();
      return students.value.filter(s => 
        (s.full_name && s.full_name.toLowerCase().includes(q)) ||
        (s.branch && s.branch.toLowerCase().includes(q)) ||
        (s.registration_number && s.registration_number.toLowerCase().includes(q))
      );
    });

    const viewStudentInfo = async (id) => {
      loadingDetails.value = true;
      selectedStudent.value = null;
      studentApplications.value = [];
      
      const modal = new bootstrap.Modal(document.getElementById('studentInfoModal'));
      modal.show();
      
      try {
        const res = await axios.get(`/api/admin/students/${id}/details`);
        selectedStudent.value = res.data.student;
        studentApplications.value = res.data.applications;
      } catch (err) {
        proxy.$toast('Failed to load student details.', 'error');
        modal.hide();
      } finally {
        loadingDetails.value = false;
      }
    };

    onMounted(loadStudents);

    return { 
      students, 
      loading, 
      searchQuery, 
      filteredStudents, 
      selectedStudent,
      studentApplications,
      loadingDetails,
      viewStudentInfo,
      toggleBlacklist, 
      deleteStudent 
    };
  }
}
</script>
