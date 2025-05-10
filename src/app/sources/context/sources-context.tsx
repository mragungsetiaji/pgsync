'use client'

import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { Source } from '../data/schema'

type SourcesContextType = {
  sources: Source[]
  isLoading: boolean
  error: string | null
  selectedSource: Source | null
  setSelectedSource: (source: Source | null) => void
  isAddDialogOpen: boolean
  setIsAddDialogOpen: (isOpen: boolean) => void
  isEditDialogOpen: boolean
  setIsEditDialogOpen: (isOpen: boolean) => void
  isDeleteDialogOpen: boolean
  setIsDeleteDialogOpen: (isOpen: boolean) => void
  refreshSources: () => Promise<void>
}

const SourcesContext = createContext<SourcesContextType | undefined>(undefined)

export function SourcesProvider({ children }: { children: ReactNode }) {
  const [sources, setSources] = useState<Source[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const fetchSources = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/sources')
      
      if (!response.ok) {
        throw new Error('Failed to fetch sources')
      }
      
      const data = await response.json()
      console.log('Fetched sources:', data)
      
      const formattedSources = data.map((item: any) => ({
        id: item.id.toString(),
        name: item.name,
        host: item.host,
        port: item.port,
        database: item.database,
        user: item.user,
        status: item.is_active ? 'active' : 'inactive',
        created_at: item.created_at ? new Date(item.created_at) : undefined,
        updated_at: item.updated_at ? new Date(item.updated_at) : undefined,
      }))

      setSources(formattedSources)
    } catch (err) {
      console.error('Error fetching sources:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSources()
  }, [])

  return (
    <SourcesContext.Provider
      value={{
        sources,
        isLoading,
        error,
        selectedSource,
        setSelectedSource,
        isAddDialogOpen,
        setIsAddDialogOpen,
        isEditDialogOpen,
        setIsEditDialogOpen,
        isDeleteDialogOpen,
        setIsDeleteDialogOpen,
        refreshSources: fetchSources
      }}
    >
      {children}
    </SourcesContext.Provider>
  )
}

export default SourcesProvider

export function useSourcesContext() {
  const context = useContext(SourcesContext)
  
  if (context === undefined) {
    throw new Error('useSourcesContext must be used within a SourcesProvider')
  }
  
  return context
}