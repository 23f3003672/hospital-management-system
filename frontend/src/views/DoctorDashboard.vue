<script>
import {
    fetchDoctorMe,
    fetchDoctorAppointments,
    completeAppointment,
    cancelDoctorAppointment,
    logoutUser
} from '@/services/api';

export default {
    name: "DoctorDashboard",
    data() {
        return {
            doctor: null,
            todayAppointments: [],
            appointments: [],    
            uniquePatients: [],
            loading: true,
            error: null,
            successMessage: ""
        };
    },

    async mounted() {
        await this.loadDashboardData();
    },

    methods: {
        async loadDashboardData() {
            this.loading = true;
            try {
                this.doctor = await fetchDoctorMe();

                const [dayRes, weekRes] = await Promise.all([
                    fetchDoctorAppointments("day"),
                    fetchDoctorAppointments("week")
                ]);

                this.todayAppointments = dayRes.appointments || [];
                
                const todayStr = new Date().toLocaleDateString('en-CA'); // Gets local YYYY-MM-DD
                this.appointments = (weekRes.appointments || []).filter(appt => appt.date !== todayStr);

                const patientsMap = new Map();
                [...this.todayAppointments, ...this.appointments].forEach(appt => {
                    if (appt.patient && appt.patient.id) {
                        patientsMap.set(appt.patient.id, appt.patient);
                    }
                });
                this.uniquePatients = Array.from(patientsMap.values());
            } catch (err) {
                if (err.status === 401) {
                    this.$router.push('/login');
                    return;
                }
                this.error = "Failed to load Dashboard Data";
                console.error(err);
            } finally {
                this.loading = false;
            }
        },
        
        goToTreatment(apptId) {
            this.$router.push({
                name: 'DoctorTreatment',
                params: { id: apptId }
            });
        },

        viewPatientHistory(patientId) {
            this.$router.push({
                name: 'DoctorPatientHistory',
                params: { patientId: patientId }
            });
        },

        goToAvailability() {
            this.$router.push({ name: 'DoctorAvailability' });
        },

        async markComplete(apptId) {
            if (!confirm("Mark this appointment as completed?")) return;
            try {
                await completeAppointment(apptId);
                this.successMessage = "Appointment marked as completed.";
                await this.loadDashboardData()
            } catch (err) {
                alert(err.message || "Failed to mark the appointment complete");
            }
        },

        async cancelAppt(apptId) {
            if (!confirm("Are you sure you want to cancel this appointment?")) return;
            try {
                await cancelDoctorAppointment(apptId);
                this.successMessage = "Appointment cancelled.";
                await this.loadDashboardData()
            } catch (err) {
                alert(err.message || "Failed to cancel");
            }
        },

        async logout() {
            try {
                await logoutUser();
            } catch (err) {
                console.warn("Logout error", err);
            } finally {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                this.$router.push("/login")
            }
        }
    }
}
</script>

<template>
    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h3>Welcome Dr. {{ doctor ? doctor.name : '...' }}</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
        </div>

        <div v-if="loading" class="text-center text-muted">Loading Dashboard...</div>
        <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="!loading">
            
            <div class="card mb-4 dashboard-card border-primary">
                <div class="card-header bg-primary text-white fw-bold d-flex justify-content-between align-items-center">
                    <span> Today's Appointments</span>
                </div>

                <div class="card-body p-0">
                    <div v-if="todayAppointments.length === 0" class="p-3 text-muted text-center">
                        No appointments scheduled for today. Have a day off!
                    </div>

                    <table class="table table-hover mb-0" v-else>
                        <thead class="table-light">
                            <tr>
                                <th>Time</th>
                                <th>Patient Name</th>
                                <th>Action</th>
                                <th>Status Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(appt) in todayAppointments" :key="'today-'+appt.id">
                                <td>
                                    <strong>{{ appt.time }}</strong>
                                </td>
                                <td class="fw-bold text-primary">{{ appt.patient ? appt.patient.name : 'Unknown' }}</td>
                                <td>
                                    <button class="btn btn-outline-primary btn-sm rounded-pill px-3" @click="goToTreatment(appt.id || appt.appointment_id)" :disabled="appt.status === 'CANCELLED'">
                                        {{ appt.status === 'COMPLETED' ? 'View/Edit Rx' : 'Add Treatment' }}
                                    </button>
                                </td>
                                <td>
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-outline-success btn-sm rounded-pill" @click="markComplete(appt.id || appt.appointment_id)" :disabled="appt.status !== 'BOOKED'">Complete</button>
                                        <button class="btn btn-outline-danger btn-sm rounded-pill" @click="cancelAppt(appt.id || appt.appointment_id)" :disabled="appt.status !== 'BOOKED'">Cancel</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card mb-4 dashboard-card">
                <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
                    <span>Upcoming This Week</span>
                    <button class="btn btn-sm btn-outline-secondary" @click="$router.push({name: 'DoctorHistory'})">
                        View Past History
                    </button>
                </div>

                <div class="card-body p-0">
                    <div v-if="appointments.length === 0" class="p-3 text-muted">No additional appointments this week.</div>

                    <table class="table table-hover mb-0" v-else>
                        <thead class="table-light">
                            <tr>
                                <th>Date & Time</th>
                                <th>Patient Name</th>
                                <th>Action</th>
                                <th>Status Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(appt) in appointments" :key="'week-'+appt.id">
                                <td>
                                    <strong>{{ appt.date }}</strong><br>
                                    <span class="text-muted small">{{ appt.time }}</span>
                                </td>
                                <td>{{ appt.patient ? appt.patient.name : 'Unknown' }}</td>
                                <td>
                                    <button class="btn btn-outline-primary btn-sm rounded-pill px-3" @click="goToTreatment(appt.id || appt.appointment_id)" :disabled="appt.status === 'CANCELLED'">
                                        {{ appt.status === 'COMPLETED' ? 'View/Edit Rx' : 'Add Treatment' }}
                                    </button>
                                </td>
                                <td>
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-outline-success btn-sm rounded-pill" @click="markComplete(appt.id || appt.appointment_id)" :disabled="appt.status !== 'BOOKED'">Complete</button>
                                        <button class="btn btn-outline-danger btn-sm rounded-pill" @click="cancelAppt(appt.id || appt.appointment_id)" :disabled="appt.status !== 'BOOKED'">Cancel</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card mb-4 dashboard-card">
                <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
                    <span>Assigned Patients</span>
                    <button class="btn btn-outline-success btn-sm rounded-pill" @click="goToAvailability">Manage Availability</button>
                </div>
                <div class="card-body p-0">
                    <div v-if="uniquePatients.length === 0" class="p-3 text-muted">No patients assigned yet.</div>

                    <div class="list-group list-group-flush" v-else>
                        <div v-for="patient in uniquePatients" :key="patient.id" class="list-group-item d-flex justify-content-between align-items-center">
                            <span class="fw-bold">{{ patient.name }}</span>
                            <button class="btn btn-outline-primary btn-sm rounded-pill px-4" @click="viewPatientHistory(patient.id)">View History</button>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<style scoped>
.dashboard-card {
    border: 2px solid #333;
    border-radius: 0;
}
.card-header {
    border-bottom: 2px solid #333;
}
.border-primary {
    border-color: #0f766e !important; 
}
.bg-primary {
    background-color: #0f766e !important;
}
</style>