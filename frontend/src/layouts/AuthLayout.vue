<template>
    <div class="auth-layout">
      <!-- 添加品牌LOGO区域 -->
      <div class="branding">
        <img src="@/assets/images/logo.svg" alt="汽修系统LOGO">
        <h1>汽车维修管理系统</h1>
      </div>
  
      <!-- 表单容器增加动效 -->
      <transition name="fade" mode="out-in">
        <div class="form-container">
          <router-view />
        </div>
      </transition>
    </div>
  </template>
  
  <style scoped lang="scss">
  @import "@/assets/styles/variables";
  
  .auth-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: $color-background;
    padding: 2rem;
  
    .branding {
      text-align: center;
      margin-bottom: 3rem;
      
      img {
        height: 80px;
        margin-bottom: 1rem;
      }
  
      h1 {
        color: $color-primary;
        font-size: 1.5rem;
        font-weight: 600;
      }
    }
  }
  
  .form-container {
    width: 100%;
    max-width: 420px;
    padding: 2.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: $shadow-md;
    transition: all 0.3s ease;
  
    &:hover {
      box-shadow: $shadow-lg;
    }
  }
  
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  </style>