/* vue app init */

if (!window.PPA) {
  window.PPA = {};
}

(async function () {
  const createApp = Vue.createApp;
  const loadModule = window['vue3-sfc-loader'].loadModule;

  // SFC loader
  const options = {
    moduleCache: {
      vue: Vue,
      'vue-router': VueRouter
    },
    async getFile(url) {
      const res = await fetch(url);
      if (!res.ok)
        throw Object.assign(new Error(res.statusText + ' ' + url), { res });
      return {
        getContentData: asBinary => asBinary ? res.arrayBuffer() : res.text(),
      };
    },
    addStyle(textContent) {
      const style = Object.assign(document.createElement('style'), { textContent });
      const ref = document.head.getElementsByTagName('style')[0] || null;
      document.head.insertBefore(style, ref);
    },
  };

  // path of pages, with cache buster
  const appVersion = new Date().getTime(); // Force fresh components on load
  window.PPA.loadComponent = (path) => loadModule('/frontend/src/components/' + path + '?v=' + appVersion, options);

  // API Rules

  //attach token if  user  loggedin
  axios.interceptors.request.use(config => {
    const token = localStorage.getItem('ppa_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  });

  // token expired redirect to login
  axios.interceptors.response.use(
    response => response,
    error => {
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('ppa_token');
        localStorage.removeItem('ppa_user');

        if (window.PPA.router) {
          window.PPA.router.push('/login');
        } else {
          window.location.href = '/';
        }
      }
      return Promise.reject(error);
    }
  );

  // START VUE APP
  try {
    // load main visual container..app.vue
    const AppComponent = await window.PPA.loadComponent('App.vue');
    const app = createApp(AppComponent);

    // register router
    window.PPA.initApp = (router) => {
      app.use(router);

      // notification
      app.config.globalProperties.$toast = function (message, type = 'info') {
        if (window._ppaToast) {
          window._ppaToast(message, type);
        }
      };

      // global date formatter
      app.config.globalProperties.$formatDate = function (dateString) {
        if (!dateString) return '—';
        let ds = dateString;
        if (!ds.endsWith('Z') && !ds.includes('+')) ds += 'Z';
        const d = new Date(ds);
        if (isNaN(d)) return '—';
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      };

      //mount app
      app.mount('#app');
    };
  } catch (e) {
    console.error("Failed to load App.vue", e);
  }
})();
