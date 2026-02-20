const BASE_URL = "http://172.24.78.93:5000/api";

/* Helper Function */
export async function request(url, options = {}) {
    const response = await fetch(`${BASE_URL}${url}`,{
        credentials:"include",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    let data = null;
    try {
        data = await response.json();
    } catch (e) {
        data = null;
    }

    if(!response.ok){
        if (response.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        const message = (data && (data.error || data.message)) || `Request failed with status ${response.status}`;

        const error = new Error(message);
        error.status = response.status;
        error.payload = data;
        throw error;
    }
    return data;
}

/* AUTH API */
export function loginUser(payload) {
    return request("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function logoutUser() {
    return request("/auth/logout", {
        method: "POST",
    });
}

export function registerPatient(payload) {
    return request("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}



/* ADMIN APIs */
export function fetchAdminDashboardCounts() {
    return request("/admin/dashboard");
}

export function addDoctor(payload) {
    return request("/admin/doctors", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function updateDoctor(doctorId,payload) {
    return request(`/admin/doctors/${doctorId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
    });
}

export function searchDoctors(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/doctors/search?${query}`);
}

export function searchPatients(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/patients/search?${query}`);
}

export function fetchAllAppointments(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/appointments?${query}`);
}

export function fetchAdminAppointmentHistory() {
    return request("/admin/appointments/history");
}

export function addDepartment(payload) {
    return request("/admin/departments", {
        method: "POST",
        body: JSON.stringify(payload)
    });
}

export function deleteDepartment(id) {
    return request(`/admin/departments/${id}`, { method: "DELETE"});
}

export function deleteDoctor(doctorId) {
    return request(`/admin/doctor/${doctorId}`, { method: "DELETE"});
}

export function updatePatient(patientId,payload) {
    return request(`/admin/patients/${patientId}`, {
        method: "PUT",
        body: JSON.stringify(payload)
    });
}

export function deletePatient(patientId) {
    return request(`/admin/patients/${patientId}`, { method: "DELETE"});
}

export function fetchAdminDepartments() {
    return request("/admin/departments"); 
}



/* PATIENT APIs */
export function fetchPatientMe() {
    return request("/patient/me");
}

export function fetchDepartments() {
    return request("/patient/departments");
}

export function fetchDoctors(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/patient/doctors?${query}`);
}

export function fetchDepartmentDetails(deptId) {
    return request(`/patient/departments/${deptId}`);
}

export function fetchUpcomingAppointments() {
    return request("/patient/appointments/upcoming");
}

export function fetchAppointmentHistory() {
    return request("/patient/appointments/history");
}

export function bookAppointment(payload) {
    return request("/patient/appointments", {
        method:"POST",
        body:JSON.stringify(payload),
    });
}

export function recheduleAppointment(appointmentId,payload) {
    return request(`/patient/appointments/${appointmentId}/reschedule`, {
        method:"PUT",
        body:JSON.stringify(payload),
    });
}

export function cancelAppointment(appointmentId) {
    return request(`/patient/appointments/${appointmentId}/cancel`, {
        method:"POST",
    });
}

export function requestExportCSV() {
    return request("/patient/export-csv", {
        method:"POST",
    });
}



/* DOCTOR APIs */
export function fetchDoctorMe() {
    return request("/doctor/me");
}

export function fetchDoctorAppointments(view) {
    if (!view || (view !=="day" && view !=="week")) {
        throw new Error("view must be 'day' or 'week'");
    }
    return request(`/doctor/appointments?view=${view}`);
}

export function fetchDoctorAvailability(doctorId = null) {
    if (doctorId) {
        return request(`/patient/doctors/${doctorId}/availability`);
    }
    return request(`/doctor/availability`);
}

export function setDoctorAvailability(payload) {
    return request("/doctor/availability", {
        method:"POST",
        body:JSON.stringify(payload),
    });
}

export function completeAppointment(appointmentId) {
    return request(`/doctor/appointments/${appointmentId}/complete`, {
        method:"POST",
    });
}

export function cancelDoctorAppointment(appointmentId) {
    return request(`/doctor/appointments/${appointmentId}/cancel`, {
        method:"POST",
    });
}

export function addTreatment(appointmentId,payload) {
    return request(`/doctor/appointments/${appointmentId}/treatment`, {
        method:"POST",
        body:JSON.stringify(payload),
    });
}

export function fetchDoctorAppointmentHistory() {
    return request("/doctor/appointments/history");
}

export function fetchPatientHistoryByDoctor(patientId) {
    return request(`/doctor/patients/${patientId}/history`);
}

export const triggerDailyReminders = () => request("/admin/trigger-reminders", { method: "POST" });
export const triggerMonthlyReports = () => request("/admin/trigger-reports", { method: "POST" });
