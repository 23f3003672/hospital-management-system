<script>
import { fetchDoctorAppointmentHistory } from '@/services/api';

export default {
    name: "DoctorHistory",
    data() {
        return {
            loading: true,
            appointments: []
        };
    },
    async mounted() {
        try {
            const res = await fetchDoctorAppointmentHistory(); 
            this.appointments = res.appointments || [];
        } catch (err) {
            console.error(err);
        } finally {
            this.loading = false;
        }
    },
    methods: {
        formatDate(dateStr) {
            if (!dateStr) return '-';
            return new Date(dateStr).toLocaleDateString('en-GB');
        },

        isPast(dateStr) {
            if (!dateStr) return false;
            const apptDate = new Date(dateStr);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            apptDate.setHours(0, 0, 0, 0);
            return apptDate < today;
        }
    }
};
</script>

<template>
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>My Appointment History</h3>
            <button class="btn btn-secondary" @click="$router.push('/doctor')">Back</button>
        </div>
        <div v-if="loading" class="text-center">Loading...</div>

        <div v-else class="card border-dark rounded-0">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Date & Time</th>
                        <th>Patient</th>
                        <th>Status</th>
                        <th>Diagnosis</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="appt in appointments" :key="appt.id || appt.appointment_id">
                        <td>
                            <strong>{{ appt.date }}</strong><br>
                            <small class="text-muted">{{ appt.time }}</small>
                        </td>
        
                        <td>{{ appt.patient_name || (appt.patient ? appt.patient.name : 'Unknown') }}</td>
        
                        <td>
                            <span v-if="appt.status === 'COMPLETED'" class="badge bg-success">COMPLETED</span>
                            <span v-else-if="appt.status === 'CANCELLED'" class="badge bg-danger">CANCELLED</span>
    
                            <span v-else-if="appt.status === 'BOOKED' && isPast(appt.date)" class="badge bg-secondary">MISSED</span>
    
                            <span v-else class="badge bg-warning text-dark">{{ appt.status }}</span>
                        </td>
        
                        <td>{{ appt.diagnosis || (appt.treatment ? appt.treatment.diagnosis : '-') }}</td>
                    </tr>
                </tbody>
            </table>
            <div v-if="appointments.length === 0" class="p-3 text-center text-muted">No history found.</div>
        </div>
    </div>
</template>