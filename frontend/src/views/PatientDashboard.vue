<script>
import { 
    cancelAppointment,
    fetchUpcomingAppointments,
    fetchDepartments,
    fetchPatientMe,
    logoutUser
 } from '@/services/api';

 export default {
    name: "PatientDashboard",
    data() {
        return {
            user: null,
            departments: [],
            upcomingAppointments: [],
            loading: false,
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
                this.user = await fetchPatientMe();

                this.departments = await fetchDepartments();

                this.upcomingAppointments = await fetchUpcomingAppointments();

            } catch (err) {
                if (err.status === 401) {
                    this.logout();
                    return;
                }
                this.error = "Failed to load Dashboard Data";
                console.error(err);
            } finally {
                this.loading = false;
            }
        },
        goToDepartment(deptId) {
            this.$router.push({
                name: 'DepartmentDetails',
                params: { id: deptId }
            });
        },


        goToHistory() {
            this.$router.push({ name:'PatientHistory' });
        },

        async cancelAppt(apptId) {
            if (!confirm("Are you sure you want to cancel this appointment?")) return;
            try {
                await cancelAppointment(apptId);
                this.successMessage = "Appointment cancelled successfullly.";

                this.upcomingAppointments = await fetchUpcomingAppointments();
            } catch (err) {
                alert(err.message || "Failed to cancel");
            }
        },

        async logout() {
            try {
                await logoutUser();
            } catch (err) {
                console.warn(err);
            } finally {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                this.$router.push("/login")
            }
        }
    }
 };

</script>

<template>
    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <div>
                <h3 class="mb-0">Welcome, {{ user ? user.name: 'Patient' }}</h3>
                <span class="text-muted small">Manage your Health Journey</span>
            </div>

            <div class="text-end">
                <button class="btn btn-link text-decoration-none" @click="$router.push({name: 'PatientEditProfile'})">Edit Profile</button>
                <button class="btn btn-link text-decoration-none" @click="goToHistory">History</button>
                <button class="btn btn-link text-danger text-decoration-none" @click="logout">Logout</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
        <div v-if="loading" class="text-center text-muted">Loading Dashboard...</div>

        <div class="card mb-4 dashboard-card" v-if="!loading">
            <div class="card-header bg-white fw-bold">
                Upcoming Appointments
            </div>
            <div class="card-body p-0">
                <div v-if="upcomingAppointments.length === 0" class="p-3 text-muted text-center">
                    No upcoming appointments. Book one below!!
                </div>

                <table class="table table-hover mb-0" v-else>
                    <thead class="table-light">
                        <tr>
                            <th>Sr No.</th>
                            <th>Doctor</th>
                            <th>Dept</th>
                            <th>Date & Time</th>
                            <th class="text-end">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(appt, index) in upcomingAppointments" :key="appt.id">
                            <td>{{ index + 1 }}.</td>
                            <td>{{ appt.doctor_name }}</td>
                            <td>{{ appt.department_name || 'General' }}</td>
                            <td>{{ appt.date }} at {{ appt.time }}</td>
                            <td class="text-end">
                                <button class="btn btn-outline-danger btn-sm rounded-pill px-3" @click="cancelAppt(appt.id)">Cancel</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card dashboard-card" v-if="!loading">
            <div class="card-header bg-white fw-bold">
                Book an Appointment (Select Department)
            </div>

            <div class="card-body">
                <div v-if="departments.length === 0" class="text-muted">No departments available.</div>

                <div class="row g-3">
                    <div class="col-md-4" v-for="dept in departments" :key="dept.id">
                        <div class="card h-100 border p-3 text-center bg-light">
                            <h5 class="card-title fw-bold">{{ dept.name }}</h5>
                            <p class="card-text small text-muted">{{ dept.description || "Specialized care" }}</p>
                            <button class="btn btn-primary w-100" @click="goToDepartment(dept.id)">View Doctors</button>
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
</style>