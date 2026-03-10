<script>
import {
    fetchDoctorAppointments,
    addTreatment,
    fetchDoctorMe,
    fetchDoctorAppointmentHistory
} from "@/services/api";

export default {
    name: "DoctorTreatment",
    props: ['id'],
    data() {
        return {
            loading: true,
            error: null,
            saving: false,
            appointment: null,
            doctor: null,

            visitType: "In-person",
            testsDone: "",
            diagnosis: "",
            newMedicine: {name: "", dosage: "" },
            medicinesList: [],
            prescriptionNotes: ""
        };
    },

    async mounted() {
        await this.loadData();
    },

    methods: {
        async loadData() {
            this.loading = true;
            try {
                const [doctorRes, apptRes, historyRes] = await Promise.all([
                    fetchDoctorMe(),
                    fetchDoctorAppointments("week"),
                    fetchDoctorAppointmentHistory()
                ]);

            this.doctor = doctorRes;

            const upcomingAppts = apptRes.appointments || [];
            let foundAppt = upcomingAppts.find(a => (a.id == this.id) || (a.appointment_id == this.id));

            if (!foundAppt) {
                const pastAppts = historyRes.appointments || historyRes || [];
                foundAppt = pastAppts.find(a => (a.id == this.id) || (a.appointment_id == this.id));
            }

            this.appointment = foundAppt;

            if (!this.appointment) {
                this.error = "Appointment not found.";
            }
            } catch (err) {
                this.error = "Failed to load data.";
                console.error(err);
            } finally {
                this.loading = false;
            }
        },

        addMedicine() {
            if(!this.newMedicine.name || !this.newMedicine.dosage) {
                alert("Enter Name and Dosage"); return;
            }
            this.medicinesList.push({ ...this.newMedicine });
            this.newMedicine = { name: "", dosage: "" };
        },

        removeMedicine(index) { this.medicinesList.splice(index, 1); },

        async saveTreatment() {
            if (!this.diagnosis) { alert("Diagnosis is required."); return; }
            this.saving = true;

            let formattedPrescription = "";
            if (this.medicinesList.length > 0) {
                formattedPrescription = "MEDICINES:\n" + this.medicinesList.map(m => `-${m.name} (${m.dosage})`).join("\n");
            }

            try {
                await addTreatment(this.id, {
                    diagnosis: this.diagnosis,
                    prescription: formattedPrescription,
                    notes: this.prescriptionNotes || "", 
                    visit_type: this.visitType || "In-person",
                    tests_done: this.testsDone || ""
                });

                alert("Treatment saved successflly!");
                this.$router.push("/doctor");
            } catch (err) {
                alert(err.message);
            } finally {
                this.saving = false;
            }
        },

        goBack() { this.$router.push("/doctor"); }
    }
};
</script>

<template>
    <div class="container mt-4 mb-5">
        <div v-if="loading" class="text-center">Loading...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="appointment && !loading">
            <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
                <h3>Update Patient History</h3>
                <button class="btn btn-link text-secondary text-decoration-none" @click="goBack">Back</button>
            </div>

            <div class="card mb-4 border-dark rounded-0">
                <div class="card-body">
                    <h5 class="card-title">Patient: {{ appointment.patient ? appointment.patient.name : 'Unknown' }}</h5>
                </div>
            </div>

            <div class="card border-dark rounded-0">
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Visit Type</label>
                            <select v-model="visitType" class="form-select border-dark">
                                <option>In-person</option><option>Online</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Tests Done</label>
                            <input v-model="testsDone" type="text" class="form-control border-dark" placeholder="e.g. Blood Test">
                        </div>
                    </div>

                    <div class="row mb-3">
                        <div class="col-md-7">
                            <label class="form-label fw-bold">Diagnosis</label>
                            <textarea v-model="diagnosis" class="form-control border-dark" rows="5" placeholder="Enter Diagnosis..."></textarea>
                        </div>
                        <div class="col-md-5">
                            <label class="form-label fw-bold">Medicines</label>
                            <div class="border border-dark p-2 mb-2 bg-light" style="max-height: 150px; overflow-y: auto;">
                                <div v-if="medicinesList.length === 0" class="text-muted small">No medicines added.</div>
                                <div v-for="(med, index) in medicinesList" :key="index" class="d-flex justify-content-between align-items-center mb-1 small">
                                    <span>{{ med.name }} <span class="badge bg-secondary">{{ med.dosage }}</span></span>
                                    <button @click="removeMedicine(index)" class="btn btn-sm text-danger fw-bold">x</button>
                                </div>
                            </div>
                            <div class="input-group input-group-sm">
                                <input v-model="newMedicine.name" type="text" class="form-control border-dark" placeholder="Medicine">
                                <input v-model="newMedicine.dosage" type="text" class="form-control border-dark" placeholder="1-0-1" style="max-width: 80px;">
                                <button @click="addMedicine" class="btn btn-dark">Add</button>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold">Prescription / Notes</label>
                        <textarea v-model="prescriptionNotes" class="form-control border-dark" rows="2" placeholder="Notes..."></textarea>
                    </div>

                    <div class="text-end">
                        <button class="btn btn-success px-4" @click="saveTreatment" :disabled="saving">
                            {{ saving ? 'Saving...' : 'Save' }}
                        </button>
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