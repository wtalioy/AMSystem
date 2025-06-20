import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const routes = [
    //重定向
    { path: '/', redirect: '/login' },

    // 认证相关
    { 
      path: '/login',
      component: () => import('@/views/auth/Login.vue'),
      meta: {  }
    },
    {
      path: '/register/customer',
      component: () => import('@/views/auth/RegisterCustomer.vue'),
      meta: {  }
    },
    {
      path: '/register/worker',
      component: () => import('@/views/auth/RegisterWorker.vue'),
      meta: {  }
    },
    {
      path: '/register/admin',
      component: () => import('@/views/auth/RegisterAdmin.vue'),
      meta: {  }
    },
  
    // 仪表盘路由组
{
  path: '/dashboard',
  component: () => import('@/layouts/DashboardLayout.vue'),
  meta: { requiresAuth: true },
  
  // ✅ 新增重定向逻辑：根据用户角色重定向
  redirect: (to) => {
    const userType = localStorage.getItem('userType')  // 👈 或从 Pinia/SessionStorage 中获取
    switch (userType) {
      case 'customer':
        return '/dashboard/customer'
      case 'worker':
        return '/dashboard/worker'
      case 'administrator':
        return '/dashboard/admin'
      default:
        return '/unauthorized'  // 🚫 未知角色，跳转至错误页
    }
  },

  children: [
    // 客户专属路由
    {
      path: 'customer',
      component: () => import('@/views/dashboard/Customer.vue'),
      meta: { role: 'customer' },
      children: [
        // 👇 默认子路由：欢迎页
        { path: '', component: () => import('@/views/dashboard/CustomerWelcome.vue') },
        
        // 其他功能页
        { path: 'cars', component: () => import('@/views/cars/CarList.vue') },
        { path: 'cars/add', component: () => import('@/views/cars/CarAdd.vue') },
        { path: 'cars/:id', component: () => import('@/views/cars/CarDetail.vue') },
        { path: 'cars/:id/maintenance-history', component: () => import('@/views/cars/CarMaintenanceHistory.vue') },
        { path: 'orders/create', component: () => import('@/views/orders/CreateOrder.vue') },
        { path: 'orders', component: () => import('@/views/orders/OrderList.vue') }, // 记得这个组件加上
        {
          path: 'orders/:order_id/procedures',
          component: () => import('@/views/orders/OrderProcedures.vue'), // 👈 创建这个新页面
          meta: { role: 'customer' }
        },

        // 订单反馈路由
        { 
          path: 'orders/:order_id/feedback', 
          component: () => import('@/views/orders/Feedback.vue'),
          meta: { role: 'customer', title: '订单反馈' }
        },
        // 个人信息
        { 
          path: 'myinfo', 
          component: () => import('@/views/auth/Myinfo.vue'),
          meta: { title: '个人信息' }
        }
      ]
    },

    {
      path: 'worker',
      component: () => import('@/views/dashboard/Worker.vue'),
      meta: { role: 'worker' },
      children: [
        // 👇 默认子路由：工人欢迎页
        { 
          path: '', 
          component: () => import('@/views/dashboard/WorkerWelcome.vue'),
          name: 'WorkerDashboard'
        },
        
        // 订单相关
        { 
          path: 'orders', 
          component: () => import('@/views/worker/MyOrders.vue'),
          name: 'WorkerOrders'
        },
        { 
          path: 'orders/pending', 
          component: () => import('@/views/worker/PendingOrders.vue'),
          name: 'PendingOrders'
        },
        {
          path: 'orders/:order_id/procedures',
          component: () => import('@/views/orders/OrderProcedures.vue'),
          meta: { role: 'worker' },
          name: 'OrderProcedures',
          props: true
        },
        {
          path: 'orders/:order_id/logs',
          component: () => import('@/views/worker/WorkLogs.vue'),
          name: 'Orderlogs',
          props: true
        },
        
        // 收入相关
        { 
          path: 'earnings', 
          component: () => import('@/views/worker/EarningsHistory.vue'),
          name: 'EarningsHistory'
        },
        { 
          path: 'earnings/monthly', 
          component: () => import('@/views/worker/MonthlyEarnings.vue'),
          name: 'MonthlyEarnings'
        },
        
        // 工作日志
        { 
          path: 'logs', 
          component: () => import('@/views/worker/WorkerLogs.vue'),
          name: 'WorkLogs'
        },

        { 
          path: 'myinfo', 
          component: () => import('@/views/auth/Myinfo.vue'),
          meta: { title: '个人信息' }
        }
      ]
    },

    // 管理员专属路由
    {
      path: 'admin',
      component: () => import('@/views/dashboard/Admin.vue'),
      meta: { role: 'administrator' },
      children: [
        { path: '', component: () => import('@/views/dashboard/AdminWelcome.vue') },
    
        // 用户与工资管理
        { path: 'users', component: () => import('@/views/admin/UserManagement.vue') },
        { path: 'wages', component: () => import('@/views/admin/WageManagement.vue') },
    
        // 各类统计页面
        { path: 'stats/orders', component: () => import('@/views/admin/OrderStatistics.vue') },
        { path: 'stats/cars', component: () => import('@/views/admin/CarStatistics.vue') },
        { path: 'stats/costs', component: () => import('@/views/admin/CostAnalysis.vue') },
        { path: 'stats/feedback', component: () => import('@/views/admin/NegativeFeedback.vue') },
        { path: 'stats/productivity', component: () => import('@/views/admin/WorkerProductivity.vue') },
        { path: 'stats/workers', component: () => import('@/views/admin/WorkerStatistics.vue') },
        { path: 'stats/incomplete-orders', component: () => import('@/views/admin/IncompleteOrders.vue') },
        { 
          path: 'myinfo', 
          component: () => import('@/views/auth/Myinfo.vue'),
          meta: { title: '个人信息' }
        }
      ]
    }
  ]
},

    
    // 公共页面
    { path: '/unauthorized', component: () => import('@/views/errors/Unauthorized.vue') },
    { path: '/:pathMatch(.*)*', component: () => import('@/views/errors/NotFound.vue') }
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