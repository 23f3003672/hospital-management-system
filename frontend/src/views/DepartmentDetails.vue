<script>
import {
    fetchDepartmentDetails,
    fetchDoctors,
    logoutUser
} from "@/services/api";

export default {
    name: "DepartmentDetails",
    props: ['id'],
    data() {
        return {
            loading: true,
            error: null,
            department: null,
            doctors: []
        };
    },
    async mounted() {
        await this.loadPageData();
    },
    methods: {
        async loadPageData() {
            this.loading = true;
            try {
                const [deptRes, docsRes] = await Promise.all([
                    fetchDepartmentDetails(this.id),
                    fetchDoctors({ department_id: this.id })
                ]);
                this.department = deptRes;
                this.doctors = docsRes;
            } catch (err) {
                this.error = "Failed to load department details";
                console.error(err);
            } finally {
                this.loading = false;
            }
        },

        goBack() {
            this.$router.push('/patient/dashboard');
        },

        goToHistory() {
            this.$router.push({ name: 'PatientHistory' });
        },

        async logout() {
            try {
                await logoutUser();
            } catch(e) {
                console.warn("Logout error:", e);
            }
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            this.$router.push('/login');
        },

        checkAvailability(doctorId) {
            this.$router.push({
                name: 'PatientBookAppointment',
                params: { doctorId: doctorId }
            });
        },

        viewDoctorDetails(doctorId) {
            this.$router.push({
                name: 'DoctorDetails',
                params: { doctorId: doctorId }
            });
        }
    }
};
</script>

<template>
    <div class="container mt-4 mb-5">
        <div v-if="loading" class="text-center">Loading...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="department && !loading">
            <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
                <h3 class="mb-0">Department of {{ department.name }}</h3>
                <div class="small">
                    <button class="btn btn-link text-decoration-none" @click="goToHistory">History</button> |
                    <button class="btn btn-link text-danger text-decoration-none" @click="logout">Logout</button>
                </div>
            </div>

            <div class="mb-4">
                <h5 class="fw-bold">Overview</h5>
                <p class="text-muted">
                    {{ department.description || `The ${department.name} Department provides specialized care and treatments for patients.` }}
                </p>
            </div>

            <div class="card border-dark rounded-0">
                <div class="card-header bg-white fw-bold">
                    Doctors' list
                </div>
                <div class="card-body p-0">
                    <div v-if="doctors.length === 0" class="p-3 text-muted">
                        No doctors found in this department.
                    </div>

                    <div v-else class="list-group list-group-flush">
                        <div v-for="doc in doctors" :key="doc.id" class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <div>
                                <h6 class="mb-0 fw-bold">Dr. {{ doc.name }}</h6>
                                <small class="text-muted">{{ doc.qualification }} • {{ doc.experience }} years exp</small>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-primary btn-sm" @click="checkAvailability(doc.id)">
                                    check availability
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" @click="viewDoctorDetails(doc.id)">
                                    view details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-3">
                 <button class="btn btn-link text-secondary text-decoration-none" @click="goBack">Back to Dashboard</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.border-dark { border-color: #333 !important; }
.rounded-0 { border-radius: 0 !important; }
</style>