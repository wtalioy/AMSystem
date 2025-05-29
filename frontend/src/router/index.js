import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const routes = [
    //重定向
    { path: '/', redirect: '/login' },

    // 认证相关
    { 
      path: '/login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/register/customer',
      component: () => import('@/views/auth/RegisterCustomer.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/register/worker',
      component: () => import('@/views/auth/RegisterWorker.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/register/admin',
      component: () => import('@/views/auth/RegisterAdmin.vue'),
      meta: { requiresAdmin: true }
    },
  
    // 仪表盘路由组
    {
      path: '/dashboard',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        // 客户专属路由
        {
          path: 'customer',
          component: () => import('@/views/dashboard/Customer.vue'),
          meta: { role: 'customer' },
          children: [
            { path: 'cars', component: () => import('@/views/cars/CarList.vue') },
            { path: 'cars/:id', component: () => import('@/views/cars/CarDetail.vue') },
            { path: 'orders/create', component: () => import('@/views/orders/CreateOrder.vue') }
          ]
        },
        
        // 技师专属路由
        {
          path: 'worker',
          component: () => import('@/views/dashboard/Worker.vue'),
          meta: { role: 'worker' },
        //   children: [
        //     { path: 'orders', component: () => import('@/views/worker/MyOrders.vue') },
        //     { path: 'orders/pending', component: () => import('@/views/worker/PendingOrders.vue') },
        //     { path: 'logs', component: () => import('@/views/worker/WorkLogs.vue') }
        //   ]
        },
        
        // 管理员专属路由
        {
          path: 'admin',
          component: () => import('@/views/dashboard/Admin.vue'),
          meta: { role: 'admin' },
        //   children: [
        //     { path: 'users', component: () => import('@/views/admin/UserManagement.vue') },
        //     { path: 'wages', component: () => import('@/views/admin/WageManagement.vue') },
        //     { path: 'stats/cars', component: () => import('@/views/admin/CarStatistics.vue') }
        //   ]
        }
      ]
    },
    
    // 公共页面
    //{ path: '/unauthorized', component: () => import('@/views/errors/Unauthorized.vue') },
    //{ path: '/:pathMatch(.*)*', component: () => import('@/views/errors/NotFound.vue') }
  ]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from) => {
    const authStore = useAuthStore()
    
    // 初始化用户状态
    if (!authStore.initialized) {
      await authStore.initialize()
    }
  
    // 认证检查
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      return {
        path: '/login',
        query: { redirect: to.fullPath }
      }
    }
  
    // 角色验证
    if (to.meta.role && authStore.userType !== to.meta.role) {
      return '/unauthorized'
    }
  
    // 游客专属路由
    if (to.meta.guestOnly && authStore.isAuthenticated) {
      return '/dashboard'
    }
  })

export default router