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

#app {
    font-family: 'Inter', sans-serif !important;
    background-color: #f8fafc; 
    color: #334155; 
    min-height: 100vh;
}

.btn-primary {
    background-color: #0f766e !important;
    border-color: #0f766e !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.2s ease-in-out;
}

.btn-primary:hover {
    background-color: #115e59 !important;
    transform: translateY(-1px);
}

.card, .form-control {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important; 
}

.card {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
</style>

