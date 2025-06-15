<!-- @/components/shared/AppNavbar.vue -->
<template>
  <nav class="app-navbar">
    <div class="navbar-brand">
      <span class="system-text">系统</span>
    </div>
  </nav>
</template>

<style scoped lang="scss">
.app-navbar {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  .navbar-brand {
    .system-text {
      font-size: 1.2rem;
      font-weight: 600;
      color: #2c3e50;
    }
  }
}
</style>