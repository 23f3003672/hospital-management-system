<script>
import { fetchAdminAppointmentHistory } from "@/services/api";

export default {
    name: "AdminPatientHistory",
    props: ['patientId'],
    data() {
        return {
            loading: true,
            history: [],
            patientName: ""
        };
    },
    async mounted() {
        this.loading = true;
        try {
            const res = await fetchAdminAppointmentHistory();
            
            const allHistory = res.appointments || []; 
            
            this.history = allHistory.filter(a => a.patient && a.patient.id == this.patientId);
            
            if (this.history.length > 0) {
                this.patientName = this.history[0].patient.name;
            }
        } catch (err) {
            console.error("Error loading history:", err);
        } finally {
            this.loading = false;
        }
    }
};
</script>

<template>
    <div class="container mt-4">
        <div class="d-flex justify-content-between mb-4 align-items-center">
            <div>
                <h3>Patient History</h3>
                <h6 v-if="patientName" class="text-muted">For: {{ patientName }}</h6>
            </div>
            <button class="btn btn-outline-primary" @click="$router.go(-1)">Back</button>
        </div>

        <div v-if="loading" class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p>Loading records...</p>
        </div>

        <div v-else class="card border-dark rounded-0 p-0">
             <table class="table table-bordered mb-0 border-dark">
                <thead class="bg-light">
                    <tr>
                        <th>Visit No.</th>
                        <th>Date & Time</th>
                        <th>Doctor</th>
                        <th>Visit Type</th>
                        <th>Diagnosis</th>
                        <th>Prescription</th>
                        <th>Tests Done</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(appt, i) in history" :key="appt.id || appt.appointment_id">
                        <td>{{ i + 1 }}.</td>
                        <td>
                            <strong>{{ appt.date }}</strong><br>
                            <small class="text-muted">{{ appt.time }}</small>
                        </td>
                        <td>Dr. {{ appt.doctor_name || 'N/A' }}</td>
                        <td>{{ appt.visit_type || '-' }}</td>
                        <td>{{ appt.diagnosis || '-' }}</td>
                        <td>
                            <span style="white-space: pre-wrap;">{{ appt.prescription || '-' }}</span>
                        </td>
                        <td>{{ appt.tests_done || '-' }}</td>
                        <td>{{ appt.notes || '-' }}</td>
                    </tr>
        
                    <tr v-if="history.length === 0">
                        <td colspan="8" class="text-center p-4">
                            No medical history found for this patient.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>