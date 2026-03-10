<script>
import { fetchDoctors, logoutUser } from '@/services/api';

export default {
    name: "DoctorDetails",
    props: ['doctorId'],
    data() {
        return {
            loading: true,
            error: null,
            doctor: null
        };
    },
    async mounted() {
        try {
            const doctors = await fetchDoctors();
            this.doctor = doctors.find(d => d.id == this.doctorId || d.doctor_id == this.doctorId);
            
            if (!this.doctor) throw new Error("Doctor not found");
        } catch (err) {
            this.error = "Could not load doctor details.";
            console.error(err);
        } finally {
            this.loading = false;
        }
    },
    methods: {
        checkAvailability() {
            this.$router.push({
                name: 'PatientBookAppointment',
                params: { doctorId: this.doctorId }
            });
        },
        goBack() {
            this.$router.go(-1);
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
        }
    }
};
</script>

<template>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <button class="btn btn-outline-secondary" @click="goBack">Back</button>
            <button class="btn btn-link text-danger text-decoration-none" @click="logout">Logout</button>
        </div>

        <div v-if="loading" class="text-center">Loading...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="doctor && !loading" class="row justify-content-center">
            <div class="col-md-8">
                <div class="card border-dark rounded-0 p-4">
                    <div class="row">
                        <div class="col-md-8">
                            <h3 class="fw-bold">Dr. {{ doctor.name }}</h3>
                            <p class="text-muted mb-1">{{ doctor.qualification }}</p>
                            
                            <p class="text-muted mb-1">
                                {{ doctor.department ? doctor.department.name : (doctor.department_name || 'General Medicine') }} Department
                            </p>
                            
                            <p class="fw-bold mt-3">
                                {{ doctor.experience }} Years Experience Overall
                            </p>

                            <p class="mt-3">
                                Dr. {{ doctor.name }} is a specialist. They have been practicing for over {{ doctor.experience }} years and are highly rated by patients.
                            </p>

                            <div class="mt-4 d-flex gap-3">
                                <button class="btn btn-outline-primary px-4" @click="checkAvailability">
                                    Check Availability
                                </button>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="bg-secondary rounded-circle d-inline-block mt-3 d-flex align-items-center justify-content-center text-white display-4" style="width: 120px; height: 120px;">
                                {{ doctor.name.charAt(0) }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.border-dark { border-color: #333 !important; }
.rounded-0 { border-radius: 0 !important; }
</style>