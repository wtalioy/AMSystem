<template>
    <div class="feedback-container">
      <el-card class="feedback-card">
        <template #header>
          <div class="card-header">
            <h2>订单反馈</h2>
            <p class="order-id">订单号: {{ orderId }}</p>
          </div>
        </template>
        
        <el-form 
          ref="feedbackFormRef" 
          :model="feedbackForm" 
          :rules="rules" 
          label-width="120px"
        >
          <el-form-item label="服务评分" prop="rating">
            <el-rate
              v-model="feedbackForm.rating"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              :texts="['非常差', '差', '一般', '好', '非常好']"
              show-text
            />
          </el-form-item>
          
          <el-form-item label="服务评价" prop="comment">
            <el-input
              v-model="feedbackForm.comment"
              type="textarea"
              :rows="6"
              placeholder="请分享您的服务体验，帮助我们改进"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="submitFeedback" :loading="submitting">
              提交反馈
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <div class="feedback-tips">
        <h3>反馈说明：</h3>
        <ul>
          <li>您的反馈将帮助我们改进服务质量</li>
          <li>评价内容需真实有效，不得包含不实信息</li>
          <li>提交后评价将显示在服务历史记录中</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import ordersAPI from '@/api/orders'
  
  const route = useRoute()
  const router = useRouter()
  const orderId = route.params.order_id
  
  // 反馈表单数据
  const feedbackForm = ref({
    order_id: orderId,
    rating: null,
    comment: ''
  })
  
  // 表单验证规则
  const rules = ref({
    rating: [
      { required: true, message: '请选择服务评分', trigger: 'blur' }
    ],
    comment: [
      { required: true, message: '请输入评价内容', trigger: 'blur' },
      { min: 10, message: '评价内容至少10个字符', trigger: 'blur' }
    ]
  })
  
  const submitting = ref(false)
  const feedbackFormRef = ref(null)
  
  // 提交反馈
  const submitFeedback = async () => {
    try {
      // 验证表单
      await feedbackFormRef.value.validate()
      
      submitting.value = true
      
      // 调用API提交反馈
      await ordersAPI.addFeedback({
        ...feedbackForm.value,
        rating: Number(feedbackForm.value.rating)
      })
      
      ElMessage.success('反馈提交成功！感谢您的评价')
      
      // 延迟后返回订单列表
      setTimeout(() => {
        router.push('/dashboard/customer/orders')
      }, 1500)
    } catch (error) {
      if (error.response) {
        // 处理API错误
        const errorMsg = error.response.data.detail || '提交反馈失败'
        ElMessage.error(errorMsg)
      } else if (error.message) {
        // 处理验证错误
        ElMessage.warning(error.message)
      } else {
        ElMessage.error('提交反馈失败，请稍后重试')
      }
    } finally {
      submitting.value = false
    }
  }
  
  // 返回上一页
  const goBack = () => {
    router.go(-1)
  }
  
  // 组件挂载时检查订单状态
  onMounted(() => {
    // 在实际应用中，这里可以添加逻辑检查订单是否已完成
    // 如果订单未完成，可以提示用户并返回
  })
  </script>
  
  <style scoped>
  .feedback-container {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
  }
  
  .feedback-card {
    margin-bottom: 30px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .order-id {
    margin: 0;
    font-size: 16px;
    color: #666;
  }
  
  .feedback-tips {
    padding: 15px;
    background-color: #f8f8f8;
    border-radius: 4px;
    border-left: 4px solid #409eff;
  }
  
  .feedback-tips h3 {
    margin-top: 0;
    color: #409eff;
  }
  
  .feedback-tips ul {
    padding-left: 20px;
  }
  
  .feedback-tips li {
    margin-bottom: 8px;
    line-height: 1.6;
  }
  </style>