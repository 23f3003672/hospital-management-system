<script>
import {
  fetchAdminDashboardCounts, addDoctor, updateDoctor, deleteDoctor, addDepartment, deleteDepartment, searchDoctors, searchPatients, updatePatient, deletePatient, logoutUser,fetchAllAppointments, fetchAdminDepartments, triggerDailyReminders, triggerMonthlyReports
} from "@/services/api";

export default {
  name: "AdminDashboard",
  data() {
    return {
      metrics: null,
      departments: [],
      newDeptName: "",
      loading: false,
      error: null,

      //Doctor Form
      showAddDoctor: false,
      isEditing: false,
      editingId: null,
      doctorForm: {
        name: "", email: "", password: "",
        department_id: "", experience: "",
        qualification: "", description: "",
      },
      formMessage: null,
      formError: false,
      createLoading: false,

      doctorResults: [],
      doctorSearch: {name:""},

      //Patient Data & Form
      patientResults: [],
      patientSearch: { name: "" },
      showEditPatient: false,
      patientForm: { id:null, name: "", email: "" },

      appointments: [],
      triggering: false,
    };
  },

  async mounted() {
    this.loading = true;
    try {
      this.metrics = await fetchAdminDashboardCounts();
      await this.loadDepartments();
      await this.searchDoctorsHandler();
      await this.searchPatientsHandler();
      await this.loadAppointmentsAdmin();
    } catch (err) {
      if(err.status === 401 || err.status === 403) {
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        this.$router.push('/login');
      }
      this.error = err.message || "Failed to load dashboard";
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async handleLogout() {
      try {
        await logoutUser();
      } catch(e) {
        console.warn("Logout error:", e);
      }
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      this.$router.push("/login");
    },
    // DEPARTMENT METHODS
    async loadDepartments() {
      try {
        this.departments = await fetchAdminDepartments();
      } catch (e){
        console.warn("Load Departments Error:", e);
      }
    },
    async addNewDepartment() {
      if(!this.newDeptName) return;
      try {
        await addDepartment({name: this.newDeptName});
        this.newDeptName = "";
        this.loadDepartments();
      } catch(e){
        alert(e.message);
      }
    },
    async removeDepartment(id) {
      if(!confirm("Delete department?")) return;
      try {
        await deleteDepartment(id);
        this.loadDepartments();
      } catch(e){
        alert(e.message);
      }
    },

   //DOCTOR METHODS
   resetDoctorForm() {
    this.showAddDoctor = !this.showAddDoctor;
    this.isEditing = false;
    this.doctorForm = {name: "", email: "",password: "", department_id: "", experience: "", qualification: "", description: ""};
    this.formMessage = null;
   },

   startEditDoctor(doc) {
    this.showAddDoctor = true;
    this.isEditing = true;
    this.editingId = doc.doctor_id;
    this.doctorForm = {
      name: doc.name, email: doc.email, department_id: doc.department_id, experience: doc.experience || 0, qualification: doc.qualification || "", description: doc.description || ""
    };
    window.scrollTo(0, 200);
   },
   async submitDoctor() {
    this.formMessage = null;
    this.formError = false;
    this.createLoading = true;

    try {
      if (this.isEditing) {
        await updateDoctor(this.editingId, this.doctorForm);
        this.formMessage = "Doctor updated successfully!";
      } else {
        if(!this.doctorForm.password) throw new Error("Password required");
        await addDoctor(this.doctorForm);
        this.formMessage = "Doctor created successfully!";
      }
      this.searchDoctorsHandler();
      if(!this.isEditing) {
        this.resetDoctorForm();
        this.showAddDoctor = true;
        this.doctorForm = {name: "", email: "",password: "", department_id: "", experience: "", qualification: "", description: ""};
      }
    } catch(e) {
      this.formError = true; this.formMessage = e.message;
    } finally {
      this.createLoading = false;
    }
   },
   async toggleDoctorActive(doc) {
    try {
      await updateDoctor(doc.doctor_id, { is_active: !doc.is_active });
      doc.is_active = !doc.is_active;
    } catch(e){
      alert(e.message);
    }
   },
   async removeDoctor(doc) {
    if(!confirm(`Delete Dr. ${doc.name}?`)) return;
    try {
      await deleteDoctor(doc.doctor_id);
      this.searchDoctorsHandler();
    } catch(e){
      alert(e.message);
    }
   },

   //PATIENT METHODS
   startEditPatient(p) {
        this.showEditPatient = true;
        this.patientForm = {
            id: p.patient_id,
            name: p.name,
            email: p.email
        };
        this.$nextTick(() => {
            const el = document.getElementById('patient-edit-section');
            if(el) el.scrollIntoView({ behavior: 'smooth' });
        });
    },
    cancelEditPatient() {
        this.showEditPatient = false;
        this.patientForm = { id: null, name: "", email: "" };
    },
    async submitPatientUpdate() {
        if(!this.patientForm.name || !this.patientForm.email) {
            alert("Name and Email are required");
            return;
        }
        try {
            await updatePatient(this.patientForm.id, {
                name: this.patientForm.name,
                email: this.patientForm.email
            });
            alert("Patient Updated Successfully!");
            this.showEditPatient = false;
            this.searchPatientsHandler();
        } catch(e) {
            alert(e.message || "Update failed");
        }
    },
    async togglePatientActive(p) { 
        try { 
            await updatePatient(p.patient_id, { is_active: !p.is_active }); 
            p.is_active = !p.is_active; 
        } catch(e){ 
            alert(e.message); 
        } 
    },
    async removePatient(p) { 
        if(!confirm(`Delete Patient ${p.name}?`)) return; 
        try { 
            await deletePatient(p.patient_id); 
            this.searchPatientsHandler(); 
        } catch(e){ 
            alert(e.message); 
        } 
    },

    //SEARCH & LOAD UTILS
    async clearDoctorSearch() { 
        this.doctorSearch.name = ""; 
        await this.searchDoctorsHandler(); 
    },
    async clearPatientSearch() { 
        this.patientSearch.name = ""; 
        await this.searchPatientsHandler(); 
    },
    
    async searchDoctorsHandler() { 
        try { 
            this.doctorResults = await searchDoctors(this.doctorSearch); 
        } catch(e){ 
            console.warn("Doctor Search Error:", e); 
        } 
    },
    async searchPatientsHandler() { 
        try { 
            this.patientResults = await searchPatients(this.patientSearch); 
        } catch(e){ 
            console.warn("Patient Search Error:", e); 
        } 
    },
    async loadAppointmentsAdmin() { 
    try { 
        const allBooked = await fetchAllAppointments({ status: 'BOOKED' }); 
        
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}-${mm}-${dd}`;

        this.appointments = allBooked.filter(appt => appt.date >= todayStr);
        
    } catch(e){ 
        console.warn("Appointments Load Error:", e); 
    } 
   },

   async fireReminders() {
    this.triggering = true;
    try {
        const res = await triggerDailyReminders();
        alert(`${res.message} (Task ID: ${res.task_id})`);
    } catch (err) {
        alert("Failed to trigger reminders: " + err.message);
    } finally {
        this.triggering = false;
    }
  },

    async fireReports() {
      this.triggering = true;
      try {
        const res = await triggerMonthlyReports();
        alert(`${res.message} (Task ID: ${res.task_id})`);
      } catch (err) {
        alert("Failed to trigger reports: " + err.message);
      } finally {
        this.triggering = false;
      }
    }
  }
};
</script>

<template>
  <div class="container mt-4 mb-5">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
      <div>
        <h3 class="mb-0">Welcome Admin</h3>
        <span class="text-muted small">Hospital Management System</span>
      </div>
      <button class="btn btn-danger" @click="handleLogout">Logout</button>
    </div>

    <div v-if="metrics" class="row mb-4">
      <div class="col-md-4"><div class="card p-3 text-center border-dark"><h5>Doctors: {{ metrics.total_doctors }}</h5></div></div>
      <div class="col-md-4"><div class="card p-3 text-center border-dark"><h5>Patients: {{ metrics.total_patients }}</h5></div></div>
      <div class="col-md-4"><div class="card p-3 text-center border-dark"><h5>Appointments: {{ metrics.total_appointments }}</h5></div></div>
    </div>

    <div class="card border-dark rounded-0 mb-4 shadow-sm">
        <div class="card-header bg-dark text-white rounded-0">
          <h5 class="mb-0">System Actions (Manual Job Triggers)</h5>
        </div>
        <div class="card-body d-flex gap-3">
          <button class="btn btn-outline-primary px-4" @click="fireReminders" :disabled="triggering">
              <span v-if="triggering" class="spinner-border spinner-border-sm me-2"></span>
              Send Daily Reminders
          </button>
          <button class="btn btn-outline-success px-4" @click="fireReports" :disabled="triggering">
              <span v-if="triggering" class="spinner-border spinner-border-sm me-2"></span>
              Generate Monthly Reports
          </button>
        </div>
      </div>

    <div v-if="loading" class="text-center">Loading dashboard...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="card mb-4 dashboard-card">
      <div class="card-header bg-white fw-bold">Manage Departments</div>
      <div class="card-body">
        <div class="input-group mb-3" style="max-width: 500px;">
          <input type="text" class="form-control" placeholder="New Department Name" v-model="newDeptName">
          <button class="btn btn-dark" @click="addNewDepartment">Add</button>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <span v-for="d in departments" :key="d.id" class="badge bg-light text-dark border p-2 d-flex align-items-center">
            {{ d.name }}
            <button class="btn-close ms-2" style="font-size: 0.6rem;" @click="removeDepartment(d.id)"></button>
          </span>
        </div>
      </div>
    </div>

    <div class="card mb-4 dashboard-card">
      <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
        <span>Registered Doctors</span>
        <button class="btn btn-sm btn-outline-success" @click="resetDoctorForm">
          {{ showAddDoctor ? 'Close Form' : 'Add New Doctor' }}
        </button>
      </div>

      <div v-if="showAddDoctor" class="card-body bg-light border-bottom">
        <h6 class="mb-3">{{ isEditing ? 'Edit Doctor' : 'Add a New Doctor' }}</h6>
        <div class="row g-3">
          <div class="col-md-4">
            <label class="small fw-bold">Name</label>
            <input class="form-control" v-model="doctorForm.name" placeholder="Dr. Name" />
          </div>

          <div class="col-md-4">
            <label class="small fw-bold">Email</label>
            <input type="email" class="form-control" v-model="doctorForm.email" :disabled="isEditing" placeholder="email@hms.com" />
          </div>

          <div class="col-md-4" v-if="!isEditing">
            <label class="small fw-bold">Password</label>
            <input type="password" class="form-control" v-model="doctorForm.password" placeholder="*******" />
          </div>

          <div class="col-md-4">
            <label class="small fw-bold">Department</label>
            <select class="form-control" v-model="doctorForm.department_id">
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>

          <div class="col-md-4">
            <label class="small fw-bold">Experience(Yrs)</label>
            <input type="number" class="form-control" v-model="doctorForm.experience">
          </div>

          <div class="col-md-4">
            <label class="small fw-bold">Qualification</label>
            <input type="text" class="form-control" v-model="doctorForm.qualification">
          </div>

          <div class="col-12">
            <label class="small fw-bold"> Description </label>
            <textarea class="form-control" v-model="doctorForm.description" rows="2"></textarea>
          </div>
        </div>

        <div class="mt-3 text-end">
          <button v-if="isEditing" class="btn btn-secondary me-2" @click="resetDoctorForm">Cancel</button>
          <button class="btn btn-success px-4" @click="submitDoctor">
            {{ isEditing ? "Update Doctor" : "Create Doctor" }}
          </button>
        </div>
        <div v-if="formMessage" class="small mt-2" :class="formError ? 'text-danger' : 'text-success'">{{ formMessage }}</div>
      </div>

      <div class="card-body p-0">
        <div class="p-2 border-bottom bg-light input-group input-group-sm" style="max-width: 400px;">
          <input type="text" class="form-control" placeholder="Search doctor..." v-model="doctorSearch.name" @keyup.enter="searchDoctorsHandler">
          <button class="btn btn-outline-secondary" @click="searchDoctorsHandler">Search</button>
          <button class="btn btn-danger" v-if="doctorSearch.name" @click="clearDoctorSearch">X</button>
        </div>
        <ul class="list-group list-group-flush" style="max-height: 300px; overflow-y: auto;">
          <li v-for="doc in doctorResults" :key="doc.doctor_id" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <strong>{{ doc.name }}</strong><span class="text-muted small">({{ doc.department }})</span>
              <div class="small text-muted">Exp: {{ doc.experience || 0 }} yrs | {{ doc.qualification || 'MBBS' }}</div>
            </div>
            <div class="btn-grp">
              <button class="btn btn-sm btn-outline-primary" @click="startEditDoctor(doc)">Edit</button>
              <button class="btn btn-sm" :class="doc.is_active ? 'btn-outline-warning' : 'btn-outline-success'" @click="toggleDoctorActive(doc)">
                {{ doc.is_active ? "Blacklist" : "Activate" }}
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="removeDoctor(doc)">Delete</button>
            </div>
          </li>
        </ul>
      </div>
    </div>




    <div class="card mb-4 dashboard-card">
      <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
        <span>Registered Patients</span>
        <span v-if="showEditPatient" class="text-primary small fw-bold">Editing: {{ patientForm.name }}</span>
      </div>

      <div v-if="showEditPatient" id="patient-edit-section" class="card-body bg-light border-bottom">
        
        <div class="row g-2 align-items-end">
          <div class="col-md-5">
            <label class="small fw-bold">Name</label>
            <input type="text" class="form-control form-control-sm" v-model="patientForm.name">
          </div>

          <div class="col-md-5">
            <label class="small fw-bold">Email</label>
            <input type="email" class="form-control form-control-sm" v-model="patientForm.email">
          </div>

          <div class="col-md-2">
            <button class="btn btn-sm btn-success me-1" @click="submitPatientUpdate">Save</button>
            <button class="btn btn-sm btn-secondary" @click="cancelEditPatient">Cancel</button>
          </div>
        </div>
      </div>

      <div class="card-body p-0">
        <div class="p-2 border-bottom bg-light input-group input-group-sm" style="max-width: 400px;">
          <input type="text" class="form-control" placeholder="Search patient..." v-model="patientSearch.name" @keyup.enter="searchPatientsHandler">
          <button class="btn btn-outline-secondary" @click="searchPatientsHandler">Search</button>
          <button class="btn btn-danger" v-if="patientSearch.name" @click="clearPatientSearch">X</button>
        </div>
        <ul class="list-group list-group-flush" style="max-height: 300px; overflow-y: auto;">
          <li v-for="p in patientResults" :key="p.patient_id" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <strong>{{ p.name }}</strong><span class="text-muted small">({{ p.email }})</span>
              <span class="badge ms-2" :class="p.is_active ? 'bg-success' : 'bg-danger'">{{ p.is_active ? "Active" : "Blocked" }}</span>
            </div>
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-info" @click="$router.push({name: 'AdminPatientHistory', params:{patientId: p.patient_id} })">History</button>
              <button class="btn btn-sm btn-outline-primary" @click="startEditPatient(p)">Edit</button>
              <button class="btn btn-sm" :class="p.is_active ? 'btn-outline-warning' : 'btn-outline-success'" @click="togglePatientActive(p)">
                {{ p.is_active ? "Block" : "Unblock" }}
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="removePatient(p)">Delete</button>
            </div>
          </li>
        </ul>
      </div>
    </div>


    <div class="card mb-4 dashboard-card">
        <div class="card-header bg-white fw-bold">Upcoming Appointments</div>
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Sr.</th><th>Date & TIme</th><th>Patient</th><th>Doctor</th><th>Status</th><th>Patient History</th></tr></thead>
                <tbody>
                    <tr v-for="(appt, index) in appointments" :key="appt.appointment_id">
                        <td>{{ index + 1 }}.</td>
                        <td>
                          {{ appt.date }} <br>
                          <span class="small text-muted">{{ appt.time }}</span>
                        </td>
                        <td>{{ appt.patient.name }}</td>
                        <td>{{ appt.doctor.name }}</td>
                        <td>{{ appt.status }}</td>
                        <td><button class="btn btn-sm btn-outline-primary px-3 rounded-pill" @click="$router.push({name:'AdminPatientHistory', params:{patientId:appt.patient.id}})">view</button></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
  </div>
</template>




<style scoped>
.dashboard-card { border: 2px solid #333; border-radius: 0; }
.card-header { border-bottom: 2px solid #333; }
</style>
