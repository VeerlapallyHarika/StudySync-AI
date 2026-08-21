export const API_ENDPOINTS = {
  // Student
  studentRegister: '/api/student/register/',
  studentLogin: '/api/student/login/',
  studentLogout: '/api/student/logout/',
  studentProfile: '/api/student/profile/',
  studentDashboard: '/api/student/dashboard/',
  studentInsights: '/api/student/insights/',
  studentChangePassword: '/api/student/change-password/',
  studentGroup: '/api/student/groups/',
  studentGroupStatus: '/api/student/groups/status/',
  studentGroupGenerate: '/api/student/groups/generate/',
  studentGroupChat: '/api/student/groups/chat/',
  studentGroupResources: '/api/student/groups/resources/',
  studentResources: '/api/student/resources/',
  // Notifications & activity
  notifications: '/api/notifications/',
  notificationRead: (id: number) => `/api/notifications/${id}/read/`,
  notificationReadAll: '/api/notifications/read-all/',
}
