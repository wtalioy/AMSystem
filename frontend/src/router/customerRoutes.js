// 客户专属路由配置
export default [
  { 
    path: 'customer',
    component: () => import('@/views/dashboard/Customer.vue'),
    meta: { role: 'customer' },
    children: [
      { path: 'cars', component: () => import('@/views/cars/CarList.vue') },
      { path: 'cars/:id', component: () => import('@/views/cars/CarDetail.vue') },
      { path: 'orders/create', component: () => import('@/views/orders/CreateOrder.vue') }
    ]
  }
]