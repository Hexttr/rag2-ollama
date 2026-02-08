import React from 'react'
import ReactMarkdown from 'react-markdown'
import type { Message } from '../../types'
import SourceReferences from './SourceReferences'

interface MessageListProps {
  messages: Message[]
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p className="text-lg mb-2">Начните диалог</p>
          <p className="text-sm">Задайте вопрос о документе</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-3xl rounded-lg px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }`}
          >
            {message.role === 'assistant' ? (
              <div className="prose dark:prose-invert max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            ) : (
              <p className="whitespace-pre-wrap">{message.content}</p>
            )}
            
            {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                <SourceReferences sources={message.sources} />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default MessageList



