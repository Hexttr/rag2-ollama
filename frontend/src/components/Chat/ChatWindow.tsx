import React, { useEffect, useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatsApi } from '../../services/api'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import SourceReferences from './SourceReferences'
import type { Message } from '../../types'

interface ChatWindowProps {
  documentId: number
  chatId: number | null
  onChatSelect: (id: number | null) => void
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  documentId,
  chatId,
  onChatSelect,
}) => {
  const queryClient = useQueryClient()
  const [currentChatId, setCurrentChatId] = useState<number | null>(chatId)

  // Create or get chat
  const { data: chat } = useQuery({
    queryKey: ['chat', currentChatId],
    queryFn: () => currentChatId ? chatsApi.getById(currentChatId).then(res => res.data) : null,
    enabled: !!currentChatId,
  })

  // Get messages
  const { data: messages } = useQuery({
    queryKey: ['messages', currentChatId],
    queryFn: () => currentChatId ? chatsApi.getMessages(currentChatId).then(res => res.data) : Promise.resolve([]),
    enabled: !!currentChatId,
  })

  // Create chat mutation
  const createChatMutation = useMutation({
    mutationFn: () => chatsApi.create(documentId, `Chat ${new Date().toLocaleDateString()}`).then(res => res.data),
    onSuccess: (data) => {
      setCurrentChatId(data.id)
      onChatSelect(data.id)
      queryClient.invalidateQueries({ queryKey: ['chats'] })
    },
  })

  useEffect(() => {
    if (!currentChatId && !createChatMutation.isPending) {
      createChatMutation.mutate()
    }
  }, [currentChatId])

  const handleSendMessage = async (query: string) => {
    if (!currentChatId) return

    try {
      await chatsApi.query(currentChatId, query, documentId)
      queryClient.invalidateQueries({ queryKey: ['messages', currentChatId] })
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  if (!currentChatId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          {chat?.title || `Chat ${currentChatId}`}
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages || []} />
      </div>

      {/* Message Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <MessageInput onSend={handleSendMessage} />
      </div>
    </div>
  )
}

export default ChatWindow



