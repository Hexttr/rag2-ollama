import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              📑 PageIndex Chat
            </h1>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Reasoning-based RAG с Ollama
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Powered by Ollama
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

