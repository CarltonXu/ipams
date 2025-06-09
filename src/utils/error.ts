import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  }
}

export function handleApiError(error: any) {
  const { t } = useI18n()
  
  if (error.response?.data?.error) {
    const errorData = error.response.data.error as ErrorResponse['error']
    
    // 处理数据库连接错误
    if (errorData.code === 'DATABASE_ERROR') {
      ElMessage.error({
        message: t('errors.database.connection'),
        duration: 5000,
        showClose: true
      })
      return
    }
    
    // 处理其他错误
    ElMessage.error({
      message: errorData.message || t('errors.unknown'),
      duration: 3000,
      showClose: true
    })
  } else {
    // 处理网络错误等
    ElMessage.error({
      message: t('errors.network'),
      duration: 3000,
      showClose: true
    })
  }
} 