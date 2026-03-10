<script>
import {
    fetchDoctorAvailability,
    setDoctorAvailability
} from "@/services/api";

export default {
    name: "DoctorAvailability", 
    data() {
        return {
            loading: true,
            saving: false,
            error: null,
            days: []
        };
    },
    async mounted() {
        this.generateWeek();
        await this.loadExistingSlots();
        this.loading = false;
    },
    methods: {
        generateWeek() {
            const today = new Date();
            const tempDays = [];

            const genslots = (startHour, endHour) => {
                let slots =[];
                for (let h = startHour; h < endHour; h++) {
                    slots.push({ time: `${h.toString().padStart(2, '0')}:00`, selected: false });
                    slots.push({ time: `${h.toString().padStart(2, '0')}:30`, selected: false });
                }
                return slots;
            };

            for (let i= 0; i < 7; i++) {
                const d = new Date(today);
                d.setDate(today.getDate() + i);
                tempDays.push({
                    date: d.toISOString().split('T')[0],
                    displayDate: d.toLocaleDateString('en-GB'),
                    morningSlots: genslots(8,12),
                    eveningSlots: genslots(16,21)
                });
            }
            this.days = tempDays;
        },

        async loadExistingSlots() {
            try {
                const res = await fetchDoctorAvailability();
                const existing = res.availability || [];

                this.days.forEach(day => {
                    const dayDB = existing.filter(s => s.date === day.date);

                    day.morningSlots.forEach(slot => {
                        if (dayDB.some(d => d.start_time.startsWith(slot.time))) {
                            slot.selected = true;
                        }
                    });

                    day.eveningSlots.forEach(slot => {
                        if (dayDB.some(d => d.start_time.startsWith(slot.time))) {
                            slot.selected = true;
                        }
                    });
                });
            } catch (err) {
                console.warn("No slots loaded", err);
            }
        },

        toggleSlot(slot) {
            slot.selected = !slot.selected;
        },

        async saveAvailability() {
            this.saving = true;
            try {
                for (const day of this.days) {
                    const selectedTimes = [
                        ...day.morningSlots.filter(s => s.selected).map(s => s.time),
                        ...day.eveningSlots.filter(s => s.selected).map(s => s.time)
                    ];

                    await setDoctorAvailability({
                        date: day.date,
                        slots: selectedTimes
                    });
                }
                alert("Availability Time Slots saved successfully!!");
                this.$router.push("/doctor");
            } catch (err) {
                alert("Error saving: " + (err.message || "Unknown error"));
            } finally {
                this.saving = false;
            }
        }
    }
};

</script>

<template>
    <div class="container mt-4 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h3>Doctor's Availability (30 Min Slots)</h3>
            <button class="btn btn-outline-secondary" @click="$router.push('/doctor')">Back</button>
        </div>
        <div v-if="loading" class="text-center">Loading...</div>

        <div class="card border-dark rounded-0 p-4" v-if="!loading">
            <div class="row mb-2 fw-bold text-center bg-light border-bottom py-2">
                <div class="col-md-2">Date</div>
                <div class="col-md-5">Morning (08:00 AM - 12:00 PM)</div>
                <div class="col-md-5">Evening (16:00 PM - 21:00 PM)</div>
            </div>

            <div v-for="(day, index)  in days" :key="index" class="row mb-4 align-items-center border-bottom pb-3">
                <div class="col-md-2 text-center">
                    <div class="fw-bold">{{ day.displayDate }}</div>
                    <small class="text-muted">{{ day.date }}</small>
                </div>

                <div class="col-md-5">
                    <div class="d-flex flex-wrap gap-2 justify-content-center">
                        <button v-for="slot in day.morningSlots" :key="slot.time" @click="toggleSlot(slot)" class="btn btn-sm" :class="slot.selected ? 'btn-success text-white' : 'btn-outline-secondary'" style="width: 60px;">
                            {{ slot.time }}
                        </button>
                    </div>
                </div>

                <div class="col-md-5">
                    <div class="d-flex flex-wrap gap-2 justify-content-center">
                        <button v-for="slot in day.eveningSlots" :key="slot.time" @click="toggleSlot(slot)" class="btn btn-sm" :class="slot.selected ? 'btn-success text-white' : 'btn-outline-secondary'" style="width: 60px;">
                            {{ slot.time }}
                        </button>
                    </div>
                </div>
            </div>

            <div class="text-end mt-4">
                <button class="btn btn-success px-5 rounded-pill" @click="saveAvailability" :disabled="saving">
                    {{ saving ? 'Saving...' : 'Save All Changes' }}
                </button>
            </div>
        </div>
    </div>
</template>