import { createRouter, createWebHistory } from 'vue-router';
import Login from "../views/Login.vue";
import DepartmentDetails from '@/views/DepartmentDetails.vue';
import PatientHistory from '@/views/PatientHistory.vue';
import DoctorTreatment from '@/views/DoctorTreatment.vue';
import DoctorAvailability from '@/views/DoctorAvailability.vue';
import DoctorPatientHistory from '@/views/DoctorPatientHistory.vue';
import AdminPatientHistory from '../views/AdminPatientHistory.vue';
import PatientEditProfile from '@/views/PatientEditProfile.vue';
import DoctorDetails from '@/views/DoctorDetails.vue';
import PatientBookAppointment from '@/views/PatientBookAppointment.vue';
import DoctorHistory from '@/views/DoctorHistory.vue';

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/patient/dashboard",
    name: "PatientDashboard",
    component: () => import("../views/PatientDashboard.vue"),
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/doctor",
    name: "DoctorDashboard",
    component: () => import("../views/DoctorDashboard.vue"),
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/admin",
    name: "AdminDashboard",
    component: () => import("../views/AdminDashboard.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/patient/department/:id",
    name: "DepartmentDetails",
    component: DepartmentDetails,
    props: true,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/patient/history",
    name: "PatientHistory",
    component: PatientHistory,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
  {
    path: "/doctor/treatment/:id",
    name: "DoctorTreatment",
    component: DoctorTreatment,
    props: true,
    meta: { requiresAuth: true, role: "doctor" },
  },
   {
    path: "/doctor/availability",
    name: "DoctorAvailability",
    component: DoctorAvailability,
    props: true,
    meta: { requiresAuth: true, role: "doctor" },
  },
   {
    path: "/doctor/patient/:patientId/history",
    name: "DoctorPatientHistory",
    component: DoctorPatientHistory,
    props: true,
    meta: { requiresAuth: true, role: "doctor" },
  },
    {
    path: "/admin/patient/:patientId/history",
    name: "AdminPatientHistory",
    component: AdminPatientHistory,
    props: true,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/patient/profile",
    name: "PatientEditProfile",
    component: PatientEditProfile,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/patient/doctor/:doctorId",
    name: "DoctorDetails",
    component: DoctorDetails,
    props: true,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/patient/book/:doctorId",
    name: "PatientBookAppointment",
    component: PatientBookAppointment,
    props: true,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/doctor/history",
    name: "DoctorHistory",
    component: DoctorHistory,
    meta: { requiresAuth: true, role: "doctor" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register'];
  const authRequired = !publicPages.includes(to.path);
  const token = localStorage.getItem('token');

  if (authRequired && !token) {
    return next('/login');
  }

  if (to.path === '/login' && token) {
    const role = localStorage.getItem('role');
    if(role === 'admin') return next('/admin');
    if(role === 'doctor') return next('/doctor');
    return next('/patient/dashboard');
  }
  next();
});

export default router;
