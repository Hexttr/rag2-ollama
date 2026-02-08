import { useState } from 'react'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'
import DocumentList from './components/Documents/DocumentList'
import ChatWindow from './components/Chat/ChatWindow'

function App() {
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null)
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null)

  return (
    <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          selectedDocumentId={selectedDocumentId}
          onDocumentSelect={setSelectedDocumentId}
          selectedChatId={selectedChatId}
          onChatSelect={setSelectedChatId}
        />
        <main className="flex-1 flex flex-col overflow-hidden">
          {selectedDocumentId ? (
            <ChatWindow
              documentId={selectedDocumentId}
              chatId={selectedChatId}
              onChatSelect={setSelectedChatId}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-2">
                  Добро пожаловать в PageIndex Chat
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                  Выберите документ для начала работы
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

