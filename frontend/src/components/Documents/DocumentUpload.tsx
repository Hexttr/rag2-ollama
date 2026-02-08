import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '../../services/api'

const DocumentUpload: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      console.log('Starting upload mutation for file:', file.name, file.size)
      try {
        const response = await documentsApi.upload(file)
        console.log('Upload response:', response)
        return response.data
      } catch (error: any) {
        console.error('Upload mutation error:', error)
        console.error('Error details:', {
          message: error?.message,
          response: error?.response?.data,
          status: error?.response?.status,
          code: error?.code
        })
        throw error
      }
    },
    onSuccess: (data) => {
      console.log('Document uploaded successfully:', data)
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: (error: any) => {
      console.error('Upload error in onError:', error)
      let errorMessage = 'Ошибка при загрузке файла'
      
      if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
        errorMessage = 'Таймаут запроса. Файл слишком большой или сервер не отвечает.'
      } else if (error?.code === 'ERR_NETWORK' || error?.message?.includes('Network Error')) {
        errorMessage = 'Ошибка сети. Проверьте, что backend запущен на http://localhost:8000'
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error?.message) {
        errorMessage = error.message
      }
      
      alert(`Ошибка: ${errorMessage}`)
    },
  })

  const handleFileSelect = (file: File) => {
    console.log('File selected:', file.name, file.type, file.size)
    
    if (file.type !== 'application/pdf') {
      alert('Пожалуйста, выберите PDF файл')
      return
    }
    
    if (file.size === 0) {
      alert('Файл пустой')
      return
    }
    
    console.log('Starting upload...')
    uploadMutation.mutate(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
        isDragging
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
      }`}
      onDrop={handleDrop}
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
    >
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="hidden"
        id="file-upload"
        disabled={uploadMutation.isPending}
      />
      <label
        htmlFor="file-upload"
        className="cursor-pointer block"
      >
        {uploadMutation.isPending ? (
          <div className="space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Загрузка...
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-4xl">📄</div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Перетащите PDF файл сюда
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              или нажмите для выбора файла
            </p>
          </div>
        )}
      </label>
    </div>
  )
}

export default DocumentUpload

