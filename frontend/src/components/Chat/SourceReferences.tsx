import React from 'react'
import type { Source } from '../../types'

interface SourceReferencesProps {
  sources: Source[]
}

const SourceReferences: React.FC<SourceReferencesProps> = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <div className="mt-2">
      <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
        📍 Источники:
      </div>
      <div className="space-y-1">
        {sources.map((source, index) => (
          <div
            key={index}
            className="text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-2"
          >
            <span className="font-medium">{source.title}</span>
            <span className="text-gray-400 dark:text-gray-500">
              (стр. {source.pages})
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SourceReferences



