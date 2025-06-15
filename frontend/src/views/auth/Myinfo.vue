<template>
    <div class="myinfo-container">
      <div class="header">
        <h1><i class="fas fa-user-circle"></i> 个人信息中心</h1>
        <p>在这里管理您的账户信息</p>
      </div>
      
      <div class="user-info-card">
        <div class="card-header">
          <div class="avatar">
            <i :class="userAvatarClass"></i>
          </div>
          <div class="user-summary">
            <h2>{{ userInfo.user_name || '加载中...' }}</h2>
            <div class="user-tags">
              <span class="user-type">{{ userTypeDisplay }}</span>
              <span v-if="userInfo.worker_type" class="worker-type">{{ userInfo.worker_type }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-body">
          <div class="info-section">
            <h3><i class="fas fa-id-card"></i> 基本信息</h3>
            <div v-if="!editing" class="info-display">
              <div class="info-item">
                <label>用户ID：</label>
                <span>{{ userInfo.user_id || '---' }}</span>
              </div>
              <div class="info-item">
                <label>用户名：</label>
                <span>{{ userInfo.user_name || '---' }}</span>
              </div>
              <div class="info-item">
                <label>用户类型：</label>
                <span>{{ userTypeDisplay }}</span>
              </div>
              <div v-if="userInfo.worker_type" class="info-item">
                <label>工人类型：</label>
                <span>{{ userInfo.worker_type || '未设置' }}</span>
              </div>
              <div class="info-item">
                <label>账户状态：</label>
                <span>{{ availabilityStatusDisplay }}</span>
              </div>
            </div>
            
            <div v-else class="edit-form">
              <div class="form-group">
                <label for="username">用户名</label>
                <input 
                  type="text" 
                  id="username" 
                  v-model="editForm.user_name" 
                  placeholder="请输入新用户名"
                >
              </div>
              
              <div class="form-group">
                <label for="password">新密码 (留空则不修改)</label>
                <input 
                  type="password" 
                  id="password" 
                  v-model="editForm.user_pwd" 
                  placeholder="输入新密码"
                >
              </div>
              
              <div v-if="userInfo.user_type === 'worker'" class="form-group">
                <label for="workerType">工人类型</label>
                <select id="workerType" v-model="editForm.worker_type">
                  <option value="" disabled>选择工人类型</option>
                  <option v-for="type in workerTypes" :key="type" :value="type">
                    {{ type }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="action-buttons">
            <button 
              v-if="!editing" 
              class="edit-btn" 
              @click="startEditing"
            >
              <i class="fas fa-edit"></i> 编辑信息
            </button>
            
            <div v-else class="edit-actions">
              <button class="save-btn" @click="saveChanges">
                <i class="fas fa-save"></i> 保存更改
              </button>
              <button class="cancel-btn" @click="cancelEditing">
                <i class="fas fa-times"></i> 取消
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="message" :class="['message', messageType]">
        <i :class="messageIcon"></i> {{ message }}
      </div>
    </div>
  </template>
  
  <script>
  import authAPI from '@/api/auth'
  
  export default {
    name: 'MyInfo',
    data() {
      return {
        userInfo: {
          user_id: '',
          user_name: '',
          user_type: '',
          worker_type: '',
          availability_status: 0
        },
        workerTypes: [],
        editing: false,
        editForm: {
          user_name: '',
          user_pwd: '',
          worker_type: ''
        },
        message: '',
        messageType: 'success',
        isLoading: false
      }
    },
    computed: {
      userTypeDisplay() {
        const types = {
          'customer': '普通客户',
          'worker': '工人用户',
          'administrator': '管理员'
        }
        return types[this.userInfo.user_type] || this.userInfo.user_type || '未知类型';
      },
      availabilityStatusDisplay() {
        return this.userInfo.availability_status === 1 ? '不可用' : '可用';
      },
      userAvatarClass() {
        return {
          'customer': 'fas fa-user',
          'worker': 'fas fa-hard-hat',
          'administrator': 'fas fa-user-shield'
        }[this.userInfo.user_type] || 'fas fa-user';
      },
      messageIcon() {
        return this.messageType === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
      }
    },
    async mounted() {
      await this.fetchUserInfo();
      if (this.userInfo.user_type === 'worker') {
        await this.fetchWorkerTypes();
      }
    },
    methods: {
      async fetchUserInfo() {
        this.isLoading = true;
        try {
          const token = localStorage.getItem('token') || sessionStorage.getItem('token');
          if (!token) {
            this.showMessage('请先登录', 'error');
            return;
          }
          
          const response = await authAPI.getCurrentUser(token);
          this.userInfo = response;
          this.showMessage('用户信息加载成功', 'success');
        } catch (error) {
          console.error('获取用户信息失败:', error);
          this.showMessage(`获取用户信息失败: ${error.response?.data?.detail || error.message}`, 'error');
        } finally {
          this.isLoading = false;
        }
      },
      
      async fetchWorkerTypes() {
        try {
          const response = await authAPI.getWorkerTypes();
          this.workerTypes = response.data;
        } catch (error) {
          console.error('获取工人类型失败:', error);
          this.showMessage(`获取工人类型失败: ${error.message}`, 'error');
        }
      },
      
      startEditing() {
        // 复制当前用户信息到编辑表单
        this.editForm = {
          user_name: this.userInfo.user_name,
          user_pwd: '',
          worker_type: this.userInfo.worker_type || ''
        };
        this.editing = true;
      },
      
      cancelEditing() {
        this.editing = false;
        this.editForm = {
          user_name: '',
          user_pwd: '',
          worker_type: ''
        };
        this.message = '';
      },
      
      async saveChanges() {
        // 表单验证
        if (!this.editForm.user_name) {
          this.showMessage('用户名不能为空', 'error');
          return;
        }
        
        this.isLoading = true;
        try {
          const token = localStorage.getItem('token') || sessionStorage.getItem('token');
          if (!token) {
            this.showMessage('请先登录', 'error');
            return;
          }
          
          // 创建只包含实际修改的字段的对象
          const updateData = { ...this.editForm };
          
          // 如果密码为空，则删除密码字段（不更新密码）
          if (!updateData.user_pwd) {
            delete updateData.user_pwd;
          }
          
          const response = await authAPI.updateCurrentUser(token, updateData);
          this.userInfo = response;
          this.editing = false;
          this.showMessage('个人信息更新成功', 'success');
          
          // 更新本地存储的用户名（如果修改了）
          const userData = JSON.parse(localStorage.getItem('userData') || '{}');
          if (userData && userData.user_name !== this.userInfo.user_name) {
            userData.user_name = this.userInfo.user_name;
            localStorage.setItem('userData', JSON.stringify(userData));
          }
        } catch (error) {
          console.error('更新用户信息失败:', error);
          
          let errorMsg = `更新失败: ${error.message}`;
          if (error.response && error.response.status === 422) {
            const errors = error.response.data.detail;
            errorMsg = errors.map(e => e.msg).join('; ');
          }
          
          this.showMessage(errorMsg, 'error');
        } finally {
          this.isLoading = false;
        }
      },
      
      showMessage(msg, type = 'success') {
        this.message = msg;
        this.messageType = type;
        
        // 3秒后自动清除消息
        setTimeout(() => {
          this.message = '';
        }, 3000);
      }
    }
  }
  </script>
  
  <style scoped>
  .myinfo-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
  }
  
  .header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
  
  .header p {
    color: #7f8c8d;
    font-size: 1.1rem;
  }
  
  .user-info-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    margin-bottom: 30px;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    padding: 25px;
    background: linear-gradient(135deg, #3498db, #8e44ad);
    color: white;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20px;
    font-size: 36px;
  }
  
  .user-summary h2 {
    margin: 0;
    font-size: 24px;
  }
  
  .user-tags {
    display: flex;
    gap: 10px;
    margin-top: 8px;
  }
  
  .user-type, .worker-type {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
  }
  
  .user-type {
    background: rgba(255, 255, 255, 0.3);
  }
  
  .worker-type {
    background: rgba(46, 204, 113, 0.7);
  }
  
  .card-body {
    padding: 25px;
  }
  
  .info-section h3 {
    margin-top: 0;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .info-display .info-item {
    display: flex;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #f5f5f5;
  }
  
  .info-display label {
    font-weight: bold;
    min-width: 100px;
    color: #7f8c8d;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .form-group input, 
  .form-group select {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.3s;
  }
  
  .form-group input:focus, 
  .form-group select:focus {
    border-color: #3498db;
    outline: none;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
  
  .action-buttons {
    margin-top: 30px;
    display: flex;
    justify-content: center;
  }
  
  button {
    padding: 12px 25px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .edit-btn {
    background: #3498db;
    color: white;
  }
  
  .edit-btn:hover {
    background: #2980b9;
  }
  
  .save-btn {
    background: #27ae60;
    color: white;
    margin-right: 10px;
  }
  
  .save-btn:hover {
    background: #219653;
  }
  
  .cancel-btn {
    background: #e74c3c;
    color: white;
  }
  
  .cancel-btn:hover {
    background: #c0392b;
  }
  
  .message {
    padding: 15px;
    border-radius: 8px;
    margin-top: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    animation: fadeIn 0.3s;
  }
  
  .message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  .message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @media (max-width: 600px) {
    .card-header {
      flex-direction: column;
      text-align: center;
    }
    
    .avatar {
      margin-right: 0;
      margin-bottom: 15px;
    }
    
    .info-display .info-item {
      flex-direction: column;
    }
    
    .info-display label {
      margin-bottom: 5px;
    }
    
    .edit-actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .save-btn, .cancel-btn {
      margin-right: 0;
      width: 100%;
    }
  }
  </style>