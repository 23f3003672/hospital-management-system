<script>
import { fetchPatientHistoryByDoctor } from "@/services/api";

export default {
    name: "DoctorPatientHistory",
    props: ['patientId'],
    data() {
        return {
            loading: true,
            error: null,
            patientName: "Loading...",
            history: []
        };
    },
    async mounted() {
        await this.loadData();
    },
    methods: {
        async loadData() {
            this.loading = true;
            try {
                const res = await fetchPatientHistoryByDoctor(this.patientId);
                
                this.patientName = res.patient_name;
                this.history = res.history || [];
                
            } catch (err) {
                console.error(err);
                this.error = "Failed to load history.";
                this.patientName = "Unknown Patient";
            } finally {
                this.loading = false;
            }
        },
        goBack() { 
            this.$router.push("/doctor");
        }
    }
};
</script>

<template>
    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
            <div>
                <h3>Patient Medical History</h3>
                <div class="text-muted">
                    Patient: <strong>{{ patientName }}</strong>
                </div>
            </div>
            <button class="btn btn-outline-primary px-4" @click="goBack">Back</button>
        </div>

        <div v-if="loading" class="text-center text-muted">
            <div class="spinner-border text-primary" role="status"></div>
            <p>Loading records...</p>
        </div>
        
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="!loading">
            <div v-if="history.length === 0" class="alert alert-warning text-center">
                No past medical history found for this patient.
            </div>

            <div class="card border-dark rounded-0" v-else>
                <div class="card-body p-0">
                    <table class="table table-bordered mb-0 border-dark">
                        <thead class="bg-light">
                            <tr>
                                <th>Visit No.</th>
                                <th>Date & Time</th>
                                <th>Doctor</th>
                                <th>Visit Type</th>
                                <th>Diagnosis</th>
                                <th>Prescription / Medicines</th>
                                <th>Tests Done</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(appt, index) in history" :key="appt.id || appt.appointment_id">
                                <td>{{ index + 1 }}.</td>
                                <td>
                                    <strong>{{ appt.date }}</strong><br>
                                    <small class="text-muted">{{ appt.time }}</small>
                                </td>
                                <td>Dr. {{ appt.doctor_name || 'N/A' }}</td>
                                <td>{{ appt.visit_type || '-' }}</td>
                                <td>{{ appt.diagnosis || '-' }}</td>
                                <td style="white-space: pre-wrap;">{{ appt.prescription || '-' }}</td>
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
        </div>
    </div>
</template>

<style scoped>
.border-dark { border-color: #333 !important; }
.rounded-0 { border-radius: 0 !important; }
</style>