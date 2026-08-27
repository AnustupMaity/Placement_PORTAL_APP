<template>
  <div>
    <Navbar v-if="!isAuthPage && !isLandingPage" />
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- Global Toast Container -->
    <div class="ppa-toast-container" id="ppa-toast-container"></div>
    
    <!-- AI Support Bot (Global) -->
    <SupportBot v-if="!isAuthPage && !isLandingPage" />
  </div>
</template>

<script>
const load = window.PPA.loadComponent;
import { computed, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'App',
  components: {
    Navbar: defineAsyncComponent(() => load('Navbar.vue')),
    SupportBot: defineAsyncComponent(() => load('SupportBot.vue'))
  },
  setup() {
    const route = useRoute();
    const isAuthPage = computed(() => {
      return route.path === '/login' || route.path === '/register';
    });
    const isLandingPage = computed(() => {
      return route.path === '/';
    });

    // Global toast logic
    window._ppaToast = (message, type = 'info') => {
      const container = document.getElementById('ppa-toast-container');
      if (!container) return;
      
      const toast = document.createElement('div');
      toast.className = `ppa-toast toast-${type}`;
      
      let icon = 'info-circle';
      if(type === 'success') icon = 'check-circle';
      if(type === 'error') icon = 'exclamation-circle';
      if(type === 'warning') icon = 'exclamation-triangle';
      
      toast.innerHTML = `<i class="bi bi-${icon}"></i> <span>${message}</span>`;
      container.appendChild(toast);
      
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    };

    return { isAuthPage, isLandingPage };
  }
};
</script>

<style scoped>
/* TOAST NOTIFICATION CONTAINER */

/* Container that holds all popups (positioned bottom-right) */
.ppa-toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: .75rem;
  pointer-events: none;
}

/* INDIVIDUAL TOAST MESSAGE BOX */

/* Base styling for each notification popup */
.ppa-toast {
  background: var(--ppa-surface);
  border: 1px solid var(--ppa-border);
  border-radius: var(--ppa-radius-sm);
  padding: .85rem 1.25rem;
  box-shadow: var(--ppa-shadow);
  min-width: 280px;
  max-width: 380px;
  color: var(--ppa-text);
  font-size: .875rem;
  display: flex;
  align-items: center;
  gap: .75rem;
  pointer-events: all;
  animation: toast-in .3s cubic-bezier(.4, 0, .2, 1);
}

/* TOAST COLORS BY TYPE */

/* Green border for success */
.ppa-toast.toast-success {
  border-left: 3px solid var(--ppa-success);
}

/* Red border for errors */
.ppa-toast.toast-error {
  border-left: 3px solid var(--ppa-danger);
}

/* Blue border for general info */
.ppa-toast.toast-info {
  border-left: 3px solid var(--ppa-info);
}

/* Yellow border for warnings */
.ppa-toast.toast-warning {
  border-left: 3px solid var(--ppa-warning);
}

/* TOAST ANIMATION */

/* Slide-in from the right side of the screen */
@keyframes toast-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
