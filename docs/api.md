# 汽车维修系统 API 文档

## 概述

汽车维修系统(Automobile Maintenance System) API 提供了一套完整的RESTful接口，用于管理汽车维修业务流程。系统支持用户认证、客户车辆管理、订单处理、技师工作分配与工资管理等功能。

**基础URL**: `http://localhost:8000/api/v1`

## 认证

API使用OAuth2密码流进行认证。所有保护的端点都需要提供一个有效的JWT令牌。

### 获取令牌

```
POST /login
```

**请求体**:

```json
{
  "username": "用户ID", 
  "password": "密码"
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 测试令牌

```
POST /login/test-token
```

**响应**:

```json
{
  "user_id": "用户ID",
  "user_type": "用户类型"
}
```

## 用户管理

### 客户注册

```
POST /users/register/customer
```

**请求体**:

```json
{
  "user_name": "客户姓名",
  "password": "密码",
  "phone": "电话号码",
  "address": "地址"
}
```

**响应**: 返回新创建的用户信息

### 工人注册 (需要管理员权限)

```
POST /users/register/worker
```

**请求体**:

```json
{
  "user_id": "技师ID",
  "worker_type": 1,
  "user_name": "技师姓名",
  "password": "密码",
  "phone": "电话号码"
}
```

**响应**: 返回新创建的工人信息

### 管理员注册 (需要管理员权限)

```
POST /users/register/admin
```

**请求体**:

```json
{
  "user_id": "管理员ID",
  "user_name": "管理员姓名",
  "password": "密码"
}
```

**响应**: 返回新创建的管理员信息

### 获取当前用户信息

```
GET /users/me
```

**响应**: 返回当前登录用户的完整信息

### 更新个人信息

```
PUT /users/me
```

**请求体**:

```json
{
  "user_name": "新用户名",
  "phone": "新电话号码",
  "address": "新地址"
}
```

**响应**: 返回更新后的用户信息

### 获取指定用户信息 (需要管理员权限)

```
GET /users/{user_id}
```

**响应**: 返回指定用户的完整信息

### 获取所有用户 (需要管理员权限)

```
GET /users/?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 返回用户列表

## 车辆管理

### 添加车辆 (客户)

```
POST /cars/
```

**请求体**:

```json
{
  "car_id": "车牌号",
  "car_type": "车型",
  "brand": "品牌",
  "color": "颜色",
  "purchase_date": "购买日期"
}
```

**响应**: 返回新添加的车辆信息

### 获取车辆列表

```
GET /cars/?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 
- 客户: 返回该客户的所有车辆
- 管理员: 返回系统中的所有车辆

### 获取指定车辆信息

```
GET /cars/{car_id}
```

**响应**: 返回指定车辆的详细信息

### 更新车辆信息

```
PUT /cars/{car_id}
```

**请求体**:

```json
{
  "car_type": "新车型",
  "brand": "新品牌",
  "color": "新颜色"
}
```

**响应**: 返回更新后的车辆信息

### 获取车辆维修历史

```
GET /cars/{car_id}/maintenance-history
```

**响应**: 返回指定车辆的维修历史记录

## 订单管理

### 创建维修订单 (客户)

```
POST /orders/
```

**请求体**:

```json
{
  "car_id": "车牌号",
  "description": "故障描述",
  "urgency": 1
}
```

**响应**: 返回新创建的订单信息

### 获取订单列表

```
GET /orders/?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 
- 客户: 返回该客户的所有订单
- 管理员: 返回系统中的所有订单

### 获取指定订单信息

```
GET /orders/{order_id}
```

**响应**: 返回指定订单的详细信息

### 获取订单维修流程

```
GET /orders/{order_id}/procedures
```

**响应**: 返回指定订单的所有维修流程

### 更新订单状态 (技师/管理员)

```
PUT /orders/status
```

**请求体**:

```json
{
  "order_id": "订单ID",
  "new_status": 1
}
```

**状态码**:
- 0: 待处理
- 1: 处理中
- 2: 已完成

**响应**: 返回更新后的订单信息

### 添加订单反馈 (客户)

```
POST /orders/feedback
```

**请求体**:

```json
{
  "order_id": "订单ID",
  "rating": 5,
  "comment": "服务评价"
}
```

**响应**: 返回更新后的订单信息

## 技师操作

### 记录维修日志

```
POST /workers/logs
```

**请求体**:

```json
{
  "order_id": "订单ID",
  "consumption": "零件消耗",
  "cost": 100.5,
  "duration": 2.5
}
```

**响应**: 返回新创建的维修日志

### 获取技师日志

```
GET /workers/logs?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 返回当前技师的维修日志列表

### 获取工资率

```
GET /workers/wage/rate
```

**响应**: 返回当前技师类型的小时工资率

### 计算技师收入

```
GET /workers/wage/income
```

**响应**: 返回当前技师的收入统计

### 获取技师订单

```
GET /workers/orders/owned?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 返回分配给当前技师的订单列表

### 获取待处理订单

```
GET /workers/orders/pending?skip=0&limit=100
```

**查询参数**:
- `skip`: 跳过的记录数，默认为0
- `limit`: 返回的最大记录数，默认为100

**响应**: 返回系统中待处理的订单列表

### 接受订单并创建维修流程

```
POST /workers/order/accept
```

**请求体**:

```json
{
  "order_id": "订单ID",
  "procedures": ["检查机油", "更换滤芯", "调整刹车"]
}
```

**响应**: 返回创建的维修流程信息

### 获取订单维修流程

```
GET /workers/order/procedures?order_id=订单ID
```

**查询参数**:
- `order_id`: 订单ID

**响应**: 返回订单的所有维修流程

### 更新维修流程状态

```
PUT /workers/order/procedures
```

**请求体**:

```json
[
  {"procedure_id": 1, "status": 2},
  {"procedure_id": 2, "status": 1}
]
```

**状态码**:
- 0: 待处理
- 1: 处理中
- 2: 已完成

**响应**: 返回处理结果

## 管理员功能

### 计算订单成本

```
POST /admin/cost
```

**请求体**:

```json
{
  "order_id": "订单ID"
}
```

**响应**: 返回订单成本详情

### 创建工资率

```
POST /admin/wage/rate
```

**请求体**:

```json
{
  "worker_type": 1,
  "wage_per_hour": 50
}
```

**响应**: 返回创建的工资率信息

### 获取所有工资率

```
GET /admin/wage/rate
```

**响应**: 返回所有工资率信息

### 更新工资率

```
PUT /admin/wage/rate/{worker_type}
```

**请求体**:

```json
{
  "new_wage": 60
}
```

**响应**: 返回更新后的工资率信息

### 获取所有工资发放记录

```
GET /admin/wage/distribute
```

**响应**: 返回所有工资发放记录

### 记录工资发放

```
POST /admin/wage/distribute
```

**请求体**:

```json
{
  "worker_id": "技师ID",
  "amount": 1000.5
}
```

**响应**: 返回工资发放记录

### 获取车型统计

```
GET /admin/statistics/car-types
```

**响应**: 返回车型、维修和成本的统计信息

### 获取工人统计

```
GET /admin/statistics/worker-types
```

**请求参数**:
- `start_time`: 起始时间
- `end_time`: 结束时间

**响应**: 返回技师类型、任务和生产力的统计信息

### 获取未完成订单

```
GET /admin/statistics/orders/incomplete
```

**响应**: 返回所有未完成订单的详细信息

## 状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数有误或操作不允许
- `401 Unauthorized`: 未提供认证信息或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 请求的资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 数据模型

### 用户类型
- `customer`: 客户
- `worker`: 技师
- `administrator`: 管理员

### 技师类型
- `1`: 机械师
- `2`: 电气技师
- `3`: 钣金技师
- `4`: 喷漆技师

### 订单状态
- `0`: 待处理
- `1`: 处理中
- `2`: 已完成

### 流程状态
- `0`: 待处理
- `1`: 处理中
- `2`: 已完成
