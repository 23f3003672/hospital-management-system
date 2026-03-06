<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

:root {
    --primary-color: #0f766e;
    --primary-hover: #115e59;
    --success-color: #059669;
    --danger-color: #dc2626;
    --text-main: #334155;
    --bg-main: #f8fafc;
    --border-light: #e2e8f0;
}

#app {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-main); 
    color: var(--text-main); 
    min-height: 100vh;
}

.btn, .form-control {
    transition: all 0.2s ease-in-out !important;
}

.card, .form-control {
    border: 1px solid var(--border-light) !important;
    border-radius: 8px !important; 
}

.card {
    box-shadow: 0 10px 25px -5px rgba(15, 118, 110, 0.15), 0 8px 10px -6px rgba(15, 118, 110, 0.1) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 12px !important; 
}

.form-control:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 0.25rem rgba(15, 118, 110, 0.25) !important;
}

.btn-primary {
    background-color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.btn-primary:hover, .btn-primary:focus {
    background-color: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
    transform: translateY(-1px);
}
.btn-outline-primary {
    color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
}
.btn-outline-primary:hover, .btn-outline-primary:focus, .btn-outline-primary:active {
    background-color: var(--primary-color) !important;
    color: #ffffff !important;
}

.btn-success {
    background-color: var(--success-color) !important;
    border-color: var(--success-color) !important;
    color: #ffffff !important;
}
.btn-outline-success {
    color: var(--success-color) !important;
    border-color: var(--success-color) !important;
}
.btn-outline-success:hover, .btn-outline-success:focus, .btn-outline-success:active {
    background-color: var(--success-color) !important;
    color: #ffffff !important;
}

.btn-danger {
    background-color: var(--danger-color) !important;
    border-color: var(--danger-color) !important;
    color: #ffffff !important;
}
.btn-outline-danger {
    color: var(--danger-color) !important;
    border-color: var(--danger-color) !important;
}
.btn-outline-danger:hover, .btn-outline-danger:focus, .btn-outline-danger:active {
    background-color: var(--danger-color) !important;
    color: #ffffff !important;
}
</style>