import React, { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '../../hooks/useWebSocket'
import type { Document } from '../../types'

interface DocumentListProps {
  documents: Document[]
  selectedId: number | null
  onSelect: (id: number | null) => void
  onDelete?: (id: number) => void
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  selectedId,
  onSelect,
  onDelete,
}) => {
  const queryClient = useQueryClient()
  
  // Subscribe to WebSocket updates for indexing documents
  const indexingDocs = documents.filter(doc => doc.status === 'indexing')
  
  useEffect(() => {
    // Poll for status updates on indexing documents
    if (indexingDocs.length > 0) {
      const interval = setInterval(() => {
        indexingDocs.forEach(doc => {
          queryClient.invalidateQueries({ queryKey: ['documents'] })
        })
      }, 2000) // Poll every 2 seconds
      
      return () => clearInterval(interval)
    }
  }, [indexingDocs.length, queryClient])
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'indexing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ready':
        return 'Готов'
      case 'indexing':
        return 'Индексация...'
      case 'error':
        return 'Ошибка'
      case 'uploading':
        return 'Загрузка...'
      default:
        return status || 'Неизвестно'
    }
  }

  if (documents.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        Нет документов. Загрузите первый документ.
      </div>
    )
  }

  const handleDelete = (e: React.MouseEvent, id: number) => {
    e.stopPropagation() // Prevent document selection
    if (window.confirm('Вы уверены, что хотите удалить этот документ?')) {
      onDelete?.(id)
    }
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className={`relative w-full text-left p-4 rounded-lg border transition-colors ${
            selectedId === doc.id
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
          }`}
        >
          <button
            onClick={() => onSelect(doc.id)}
            className="w-full text-left"
          >
            <div className="flex items-start justify-between pr-6">
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 dark:text-gray-100 truncate">
                  {doc.filename}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(doc.created_at).toLocaleDateString()}
                </div>
              </div>
              <span
                className={`ml-2 px-2 py-1 text-xs font-medium rounded ${getStatusColor(doc.status)}`}
              >
                {getStatusText(doc.status)}
              </span>
            </div>
          </button>
          {onDelete && (
            <button
              onClick={(e) => handleDelete(e, doc.id)}
              className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
              title="Удалить документ"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>
      ))}
    </div>
  )
}

export default DocumentList

