import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi, chatsApi } from '../../services/api'
import DocumentList from '../Documents/DocumentList'
import DocumentUpload from '../Documents/DocumentUpload'
import type { Document, Chat } from '../../types'

interface SidebarProps {
  selectedDocumentId: number | null
  onDocumentSelect: (id: number | null) => void
  selectedChatId: number | null
  onChatSelect: (id: number | null) => void
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedDocumentId,
  onDocumentSelect,
  selectedChatId,
  onChatSelect,
}) => {
  const [activeTab, setActiveTab] = useState<'documents' | 'chats'>('documents')

  const { data: documents, refetch: refetchDocuments } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsApi.getAll().then(res => res.data),
    refetchOnWindowFocus: true,
    refetchInterval: 2000, // Refetch every 2 seconds to see status updates
  })

  const { data: chats } = useQuery({
    queryKey: ['chats', selectedDocumentId],
    queryFn: () => chatsApi.getAll(selectedDocumentId || undefined).then(res => res.data),
    enabled: !!selectedDocumentId,
  })

  const queryClient = useQueryClient()
  
  const deleteDocument = useMutation({
    mutationFn: (id: number) => documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      // If deleted document was selected, clear selection
      if (selectedDocumentId) {
        onDocumentSelect(null)
      }
    },
  })

  const handleDeleteDocument = async (id: number) => {
    try {
      await deleteDocument.mutateAsync(id)
    } catch (error) {
      console.error('Error deleting document:', error)
      alert('Ошибка при удалении документа')
    }
  }

  return (
    <aside className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('documents')}
          className={`flex-1 px-4 py-3 text-sm font-medium ${
            activeTab === 'documents'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
        >
          📄 Документы
        </button>
        {selectedDocumentId && (
          <button
            onClick={() => setActiveTab('chats')}
            className={`flex-1 px-4 py-3 text-sm font-medium ${
              activeTab === 'chats'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            💬 Чаты
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'documents' ? (
          <div className="p-4 space-y-4">
            <DocumentUpload />
            <DocumentList
              documents={documents || []}
              selectedId={selectedDocumentId}
              onSelect={onDocumentSelect}
              onDelete={handleDeleteDocument}
            />
          </div>
        ) : (
          <div className="p-4">
            {chats && chats.length > 0 ? (
              <div className="space-y-2">
                {chats.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => onChatSelect(chat.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      selectedChatId === chat.id
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                        : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    <div className="font-medium truncate">
                      {chat.title || `Chat ${chat.id}`}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                Нет чатов для этого документа
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar

