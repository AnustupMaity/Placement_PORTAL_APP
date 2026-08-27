/* vue router configuration */

if (!window.PPA) {
  window.PPA = {};
}
(function () {
  const createRouter = VueRouter.createRouter;
  const createWebHistory = VueRouter.createWebHistory;
  const load = window.PPA.loadComponent;

  const routes = [
    // public 
    { path: '/', component: () => load('Landing.vue'), name: 'Landing' },
    { path: '/login', component: () => load('Login.vue'), name: 'Login' },
    { path: '/register', component: () => load('Register.vue'), name: 'Register' },

    // admin 
    { path: '/admin', component: () => load('AdminDashboard.vue'), name: 'AdminDashboard', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/companies', component: () => load('AdminCompanies.vue'), name: 'AdminCompanies', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/students', component: () => load('AdminStudents.vue'), name: 'AdminStudents', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/drives', component: () => load('AdminDrives.vue'), name: 'AdminDrives', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/applications', component: () => load('AdminApplications.vue'), name: 'AdminApplications', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/placements', component: () => load('AdminPlacements.vue'), name: 'AdminPlacements', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/community', component: () => load('CommunityBoard.vue'), name: 'AdminCommunity', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/messages', component: () => load('Messages.vue'), name: 'AdminMessages', meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/profile', component: () => load('AdminProfile.vue'), name: 'AdminProfile', meta: { requiresAuth: true, role: 'admin' } },

    // company 
    { path: '/company', component: () => load('CompanyDashboard.vue'), name: 'CompanyDashboard', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/drives', component: () => load('CompanyDrives.vue'), name: 'CompanyDrives', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/drives/create', component: () => load('CreateDrive.vue'), name: 'CreateDrive', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/drives/:id/applications', component: () => load('CompanyApplications.vue'), name: 'CompanyApplications', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/applications', component: () => load('CompanyApplications.vue'), name: 'CompanyApplicationsGeneral', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/profile', component: () => load('CompanyProfile.vue'), name: 'CompanyProfile', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/placements', component: () => load('CompanyPlacements.vue'), name: 'CompanyPlacements', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/community', component: () => load('CommunityBoard.vue'), name: 'CompanyCommunity', meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/messages', component: () => load('Messages.vue'), name: 'CompanyMessages', meta: { requiresAuth: true, role: 'company' } },

    // student
    { path: '/student', component: () => load('StudentDashboard.vue'), name: 'StudentDashboard', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/companies', component: () => load('StudentCompanies.vue'), name: 'StudentCompanies', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/drives', component: () => load('StudentDrives.vue'), name: 'StudentDrives', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/drives/:id', component: () => load('DriveDetail.vue'), name: 'DriveDetail', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/applications', component: () => load('StudentApplications.vue'), name: 'StudentApplications', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/profile', component: () => load('StudentProfile.vue'), name: 'StudentProfile', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/mock-interview', component: () => load('MockInterview.vue'), name: 'MockInterview', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/history', component: () => load('StudentHistory.vue'), name: 'StudentHistory', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/community', component: () => load('CommunityBoard.vue'), name: 'StudentCommunity', meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/messages', component: () => load('Messages.vue'), name: 'StudentMessages', meta: { requiresAuth: true, role: 'student' } },

    // if any other go to login
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ];

  const router = createRouter({ //html5 type history
    history: createWebHistory(),
    routes,
    scrollBehavior() { return { top: 0 }; },
  });

  // frontend checker login? and user type?
  router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('ppa_token');
    const user = JSON.parse(localStorage.getItem('ppa_user') || 'null');

    // user type goes to which page 
    const homePages = { admin: '/admin', company: '/company', student: '/student' };

    //need login...no token...redirect to login
    if (to.meta.requiresAuth && !token) {
      return next('/login');
    }

    //if loggedin
    if (token && user) {
      //if loggedin...dont allow show login/register page 
      if (to.path === '/login' || to.path === '/register') {
        return next(homePages[user.role] || '/');
      }

      //stop to go to others role page
      if (to.meta.role && user.role !== to.meta.role) {
        return next(homePages[user.role] || '/login');
      }
    }

    // all ok..proceed
    next();
  });

  window.PPA.router = router;//show part that not need login/role

  // int app
  const tryInit = () => {
    if (window.PPA.initApp) {
      window.PPA.initApp(router);
    } else {
      setTimeout(tryInit, 50);
    }
  };
  tryInit();
})();

