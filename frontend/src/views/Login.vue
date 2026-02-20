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
                    alert("Registration successful! Please log in.");
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
    <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
        <div class="card shadow p-4" style="max-width: 400px; width: 100%;">
            <h3 class="text-center mb-3">{{ isRegister ? 'Patient Register' : 'Login' }}</h3>

            <form @submit.prevent="handleSubmit">
                <div class="mb-3" v-if="isRegister">
                    <label>Full Name</label>
                    <input v-model="name" type="text" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label>Email</label>
                    <input v-model="email" type="email" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label>Password</label>
                    <input v-model="password" type="password" class="form-control" required />
                </div>

                <div v-if="error" class="alert alert-danger small">{{ error }}</div>

                <button class="btn btn-primary w-100" :disabled="loading">{{ loading ? 'Processing...' : (isRegister ? 'Register' : 'Login') }}</button>
            </form>

            <div class="mt-3 text-center">
                <button class="btn btn-link btn-sm" @click="toggleMode">
                    {{ isRegister ? 'Already have an account? Login' : 'New Patient? Register' }}
                </button>
            </div>
        </div>
    </div>
</template>