<script>
import { loginUser, registerPatient } from '@/services/api';

export default {
    name:"UserLogin",
    data() {
        return {
            isRegister: false,
            email: "",
            name: "",
            password: "",
            loading: false,
            error: null,
        };
    },
    methods: {
        toggleMode() {
            this.isRegister = !this.isRegister;
            this.error = null;
        },
        async handleSubmit() {
            this.loading = true;
            this.error = null;

            try {
                let data;
                if (this.isRegister) {
                    await registerPatient({
                        email: this.email,
                        password: this.password,
                        name: this.name,
                        role: "patient",
                    });
                    alert("Registration successful! Kindly Log In.");
                    this.isRegister = false;
                } else {
                    data = await loginUser({
                        email: this.email,
                        password: this.password
                    });

                    localStorage.setItem("token", data.token);
                    localStorage.setItem("role", data.role);

                    if (data.role === "admin") this.$router.push("/admin");
                    else if (data.role === "doctor") this.$router.push("/doctor");
                    else this.$router.push("/patient/dashboard");
                }
            } catch (err) {
                this.error = err.message || "Authentication failed";
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>

<template>
    <div class="d-flex flex-column justify-content-center align-items-center min-vh-100 px-3">
        
        <div class="text-center mb-4" style="max-width: 500px;">
            <h1 class="display-4 fw-bold brand-text mb-0 d-flex justify-content-center align-items-center gap-2">
                <i class="bi bi-heart-pulse-fill"></i> HMS
            </h1>
            <p class="lead text-muted mb-4">Hospital Management System</p>

            <div v-if="!isRegister" class="text-muted">
                <p class="mb-1 fw-medium" style="color: #334155;">Welcome to the Central Healthcare Portal.</p>
                <p class="small">
                    Secure access for <strong class="brand-text">Admins</strong>, 
                    <strong class="brand-text">Doctors</strong>, and <strong class="brand-text">Patients</strong>. 
                </p>
            </div>

            <div v-else class="text-muted">
                <p class="mb-1 fw-medium" style="color: #334155;">Welcome to our Healthcare Family!</p>
                <p class="small">
                    New patients can register below to easily book appointments with India's leading Medical Experts across cities and view their medical records.
                </p>
            </div>
        </div>

        <div class="card p-4 p-md-5 border-0 bg-white" style="max-width: 420px; width: 100%;">
            <h4 class="text-center mb-4 brand-text" style="font-weight: 600;">
                {{ isRegister ? 'Patient Registration' : 'Account Login' }}
            </h4>

            <form @submit.prevent="handleSubmit">
                
                <div class="mb-4" v-if="isRegister">
                    <label class="form-label small fw-bold text-uppercase d-flex align-items-center gap-2" style="color: #64748b;">
                        <i class="bi bi-person-fill"></i> Full Name
                    </label>
                    <input v-model="name" type="text" class="form-control form-control-lg fs-6 bg-light" placeholder="e.g. Devansh Malhotra" required />
                </div>

                <div class="mb-4">
                    <label class="form-label small fw-bold text-uppercase d-flex align-items-center gap-2" style="color: #64748b;">
                        <i class="bi bi-envelope-fill"></i> Email ID
                    </label>
                    <input v-model="email" type="email" class="form-control form-control-lg fs-6 bg-light" placeholder="name@example.com" required />
                </div>

                <div class="mb-4">
                    <label class="form-label small fw-bold text-uppercase d-flex align-items-center gap-2" style="color: #64748b;">
                        <i class="bi bi-lock-fill"></i> Password
                    </label>
                    <input v-model="password" type="password" class="form-control form-control-lg fs-6 bg-light" placeholder="********" required />
                </div>

                <div v-if="error" class="alert alert-danger small py-2 d-flex align-items-center gap-2">
                    <i class="bi bi-exclamation-triangle-fill"></i> {{ error }}
                </div>

                <button class="btn btn-primary btn-lg w-100 mt-2 fw-bold" :disabled="loading">
                    {{ loading ? 'Processing...' : (isRegister ? 'Create Account' : 'Login') }}
                </button>
            </form>

            <div class="mt-4 text-center">
                <button class="btn btn-link btn-sm text-decoration-none brand-text fw-medium" @click="toggleMode">
                    {{ isRegister ? 'Already have an account? Log In' : 'New Patient? Register Here' }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.brand-text {
    color: #0f766e !important;
}

h1.brand-text {
    letter-spacing: -2px;
}
</style>