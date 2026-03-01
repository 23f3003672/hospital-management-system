<script>
import { fetchAppointmentHistory, requestExportCSV, logoutUser, fetchPatientMe } from '@/services/api';

export default {
    name: "PatientHistory",
    data() {
        return {
            history: [],
            loading: true,
            exporting: false,
            error: null,
            successMessage: "",
            patientName: "Loading..."
        };
    },
    async mounted() {
        await this.loadHistory();
    },
    methods: {
        async loadHistory() {
            this.loading = true;
            try {
                const [userRes, historyRes] = await Promise.all([
                    fetchPatientMe(),
                    fetchAppointmentHistory()
                ]);
                
                this.patientName = userRes.name;
                this.history = historyRes.appointments || [];
            } catch (err) {
                this.error = "Failed to load the History.";
                console.error(err);
            } finally {
                this.loading = false;
            }
        },

        async exportCSV() {
            this.exporting = true;
            try {
                await requestExportCSV();
                alert("CSV Export started! You will receive an email shortly.");
            } catch (err) {
                alert("Failed to start export: " + err.message);
            } finally {
                this.exporting = false;
            }
        },

        goBack() {
            this.$router.push("/patient/dashboard");
        },

        async logout() {
            try {
                await logoutUser();
            } catch (err) {
                console.warn("Server logout failed, forcing local logout", err);
            } finally {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                this.$router.push("/login");
            }
        }
    }
};
</script>

<template>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h3>Patient History</h3>
            <div class="gap-2 d-flex">
                <button class="btn btn-outline-success btn-sm" @click="exportCSV" :disabled="exporting">
                    {{ exporting ? "Exporting..." : "export as csv" }}
                </button>
                <button class="btn btn-outline-primary btn-sm" @click="goBack">back</button>
            </div>
        </div>
        
        <div class="mb-3 text-muted small">
            <div><strong>Patient Name:</strong>{{ patientName }}</div>
            <div><strong>Note:</strong>Showing all past treatments and completed appointments.</div>
        </div>

        <div class="card history-card">
            <div class="card-body p-0">
                <div v-if="loading" class="p-3 text-center">Loading History...</div>

                <div v-if="!loading && history.length === 0" class="p-3 text-muted text-center">
                    No medical history found.
                </div>

                <table v-if="!loading && history.length > 0" class="table table-bordered mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Visit No.</th>
                            <th>Date</th>
                            <th>Doctor</th>
                            <th>Visit Type</th>
                            <th>Diagnosis</th>
                            <th>Prescription</th>
                            <th>Tests Done</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(visit, index) in history" :key="visit.id">
                            <td>{{ index + 1 }}.</td>
                            <td>
                                <strong>{{ visit.date }}</strong><br>
                                <small class="text-muted">{{ visit.time }}</small>
                            </td>
                            <td>Dr. {{ visit.doctor_name }}</td>
                            <td>{{ visit.visit_type || '-' }}</td>
                            <td class="text-danger">{{ visit.diagnosis || '-' }}</td>
                            <td class="text-danger" style="white-space: pre-wrap;">{{ visit.prescription || '-' }}</td>
                            <td class="text-danger">{{ visit.tests_done || '-' }}</td>
                            <td>{{ visit.notes || '-' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</template>

<style scoped>
.history-card {
    border: 2px solid #333;
    border-radius: 0;
}
.btn-outline-success, .btn-outline-primary {
    border-width: 2px;
    font-weight: 500;
}
</style>