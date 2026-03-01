<script>
import {
    fetchDoctorAvailability,
    bookAppointment,
    fetchDoctors
} from "@/services/api";

export default {
    name: "PatientBookAppointment",
    props: ['doctorId'],
    data() {
        return {
            loading: true,
            booking: false,
            error: null,
            success: null,
            doctorName: "Doctor",

            availability: [],
            days: [],
            selectedSlot: null
        };
    },
    async mounted() {
        await this.loadData();
    },
    methods: {
        async loadData() {
            this.loading = true;
        try {
            const docs = await fetchDoctors();
            const doc = docs.find(d => d.id == this.doctorId);
            if(doc) this.doctorName = doc.name;

            const res = await fetchDoctorAvailability(this.doctorId);

            if (Array.isArray(res)) {
                this.availability = res;
            } else {
                this.availability = res.availability || [];
            }

            this.generateWeek();
        } catch (err) {
            console.error(err);
            this.error = "Failed to load schedule.";
        } finally {
            this.loading = false;
        }
    },

    generateWeek() {
        const today = new Date();
        const tempDays = [];

        for (let i = 0; i<7; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2,'0');
            const dateStr = `${year}-${month}-${day}`;

            const daySlots = this.availability.filter(s => s.date === dateStr).map(s => ({
                time: s.start_time.substring(0,5),
                display: this.formatTime12(s.start_time),
                is_past: s.is_past,
                is_booked: s.is_booked
            })).sort((a,b) => a.time.localeCompare(b.time));

            tempDays.push({
                date: dateStr,
                displayDate: d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }),
                slots: daySlots
            });
        }
        this.days = tempDays;
    },

    selectSlot(day, slot) {
        if (slot.is_past || slot.is_booked) return; 

        if (this.selectedSlot && this.selectedSlot.date === day.date && this.selectedSlot.time === slot.time) {
            this.selectedSlot = null;
            return;
        }

        this.selectedSlot = {
            date: day.date,
            time: slot.time,
            display: `${day.displayDate} at ${slot.display}`
        };
    },

    getSlotClass(day, slot) {
        if (this.selectedSlot && this.selectedSlot.date === day.date && this.selectedSlot.time === slot.time) {
            return 'slot-selected';
        }
        if (slot.is_past) return 'slot-past';
        if (slot.is_booked) return 'slot-booked';
        return 'slot-available';
    },

    formatTime12(time24) {
        const [hours, minutes] = time24.split(':');
        let h = parseInt(hours, 10);
        const m = minutes.substring(0,2);
        const ampm = h >= 12 ? 'PM' : 'AM';

        h = h % 12;
        h = h ? h : 12;
        return `${h}:${m} ${ampm}`;
    },

    async confirmBooking() {
        if (!this.selectedSlot) return;
        if (!confirm(`Book appointment with Dr. ${this.doctorName} on ${this.selectedSlot.display}?`)) return;

        this.booking = true;
        this.error = null;

        try {
            await bookAppointment({
                doctor_id: this.doctorId,
                date: this.selectedSlot.date,
                time_slot: this.selectedSlot.time
            });
            this.success = "Appointment Booked Successfully!!";
            setTimeout(() => this.$router.push('/patient/dashboard'), 1500);
        } catch (err) {
            this.error = err.message || "Booking failed.";
        } finally {
            this.booking = false;
        }
    }

        
    }
};
</script>

<template>
    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Dr. {{ doctorName }} - Select a Slot</h3>
            <button class="btn btn-outline-secondary" @click="$router.go(-1)">Back</button>
        </div>

        <div v-if="loading" class="text-center">Loading schedule...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div v-if="!loading" class="card border-dark rounded-0 p-4">
            <div class="text-muted small mb-3">
                <i class="bi bi-info-circle"></i> Select a green slot to book your appointment
            </div>

            <div v-for="day in days" :key="day.date" class="row mb-3 border-bottom pb-3">
                <div class="col-md-2 text-center pt-2">
                    <div class="fw-bold fs-5">{{ day.displayDate.split(',')[0] }}</div>
                    <div class="text-muted">{{ day.displayDate.split(',')[1] }}</div>
                </div>

                <div class="col-md-10">
                    <div v-if="day.slots.length === 0" class="text-muted pt-2 fst-italic">
                        No Slots Available
                    </div>
                    <div v-else class="d-flex flex-wrap gap-2">
                        <button v-for="slot in day.slots" :key="slot.time" class="btn btn-sm slot-btn" :class="getSlotClass(day, slot)" :disabled="slot.is_past || slot.is_booked" @click="selectSlot(day, slot)" style ="width: 100px; display: flex; flex-direction: column; align-items: center;">
                            <span class="fw-bold">{{ slot.display }}</span>
                            <span style="font-size: 10px; margin-top: 2px;">
                                <span v-if="slot.is_past">Passed</span>
                                <span v-else-if="slot.is_booked">Booked</span>
                                <span v-else>Available</span>
                            </span>
                        </button>
                    </div>
                </div>
            </div>
            <div class="text-end mt-4 pt-2">
                <span class="text-muted me-3 fs-5" v-if="selectedSlot">
                    Selected: <strong>{{ selectedSlot.display }}</strong>
                </span>
                <button class="btn btn-success px-5 btn-lg" :disabled="!selectedSlot || booking" @click="confirmBooking">
                    {{ booking ? 'Booking...' : "Confirm Booking" }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.slot-btn {
    transition: all 0.2s;
    border: 1.5px solid #ccc;
    background: white;
}

.slot-available {
    border-color: #198754;
    color: #198754;
    background: #f8fff9;
}
.slot-available:hover {
    background: #198754;
    color: white;
}

.slot-selected {
    background: #198754 !important;
    color: white !important;
    border-color: #198754 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.slot-booked {
    border-color: #ced4da;
    color: #6c757d;
    background: #e9ecef;
    cursor: not-allowed;
    opacity: 0.8;
}

.slot-past {
    border-color: #f5c2c7;
    color: #dc3545;
    background: #fdf3f4;
    cursor: not-allowed;
    opacity: 0.7;
}
</style>