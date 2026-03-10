<script>
import { fetchPatientMe, request } from '@/services/api';

export default {
    name: "PatientEditProfile",
    data() {
        return {
            loading: true,
            saving: false,
            error: null,
            success: null,
            form: {
                name: "",
                phone: "",
                address: "",
                password: ""
            }
        };
    },
    async mounted() {
        try {
            const user = await fetchPatientMe();
            this.form.name = user.name;
            this.form.phone = user.phone || "";
            this.form.address =  user.address || "";
        } catch (err) {
            this.error = "Failed to load your details.";
        } finally {
            this.loading = false;
        }
    },
    methods: {
        async saveProfile() {
            this.saving = true;
            this.error = null;
            this.success = null;

            try {
                await request("/patient/me", {
                    method: "PUT",
                    body: JSON.stringify(this.form)
                });
                this.success = "Profile updated successfully!";
                this.form.password = "";
            } catch (err) {
                this.error = err.message || "Failed to update your profile";
            } finally {
                this.saving = false;
            }
        }
    }
};
</script>

<template>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card border-dark rounded-0">
                    <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
                        <span>Edit Profile</span>
                        <button class="btn btn-sm btn-outline-secondary" @click="$router.push('/patient/dashboard')">Back</button>
                    </div>
                    <div class="card-body">
                        <div v-if="loading" class="text-center">Loading...</div>
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="success" class="alert alert-success">{{ success }}</div>

                        <form v-if="!loading" @submit.prevent="saveProfile">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Full Name</label>
                                <input v-model="form.name" type="text" class="form-control" required />
                            </div>

                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">Phone Number</label>
                                    <input v-model="form.phone" type="text" class="form-control" placeholder="e.g. 9000000001" />
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">City / Address</label>
                                    <input v-model="form.address" type="text" class="form-control" placeholder="e.g. Bareilly" />
                                </div>
                            </div>

                            <div class="mb-4">
                                <label class="form-label fw-bold">New Password</label>
                                <input v-model="form.password" type="password" class="form-control" placeholder="Leave Blank to keep the current password" />
                                <div class="form-text">Min 8 characters.</div>
                            </div>

                            <button class="btn btn-success w-100" :disabled="saving">{{ saving ? 'Saving...' : 'Update Profile' }}</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>