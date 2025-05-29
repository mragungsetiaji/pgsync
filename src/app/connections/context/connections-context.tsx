'use client'

import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { Connection } from '../data/schema'

type ConnectionsContextType = {
  connections: Connection[]
  isLoading: boolean
  error: string | null
  selectedConnection: Connection | null
  setSelectedConnection: (connection: Connection | null) => void
  isAddDialogOpen: boolean
  setIsAddDialogOpen: (isOpen: boolean) => void
  isEditDialogOpen: boolean
  setIsEditDialogOpen: (isOpen: boolean) => void
  isDeleteDialogOpen: boolean
  setIsDeleteDialogOpen: (isOpen: boolean) => void
  refreshConnections: () => Promise<void>
}

const ConnectionsContext = createContext<ConnectionsContextType | undefined>(undefined)

export function ConnectionsProvider({ children }: { children: ReactNode }) {
  const [connections, setConnections] = useState<Connection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const fetchConnections = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/connections')
      
      if (!response.ok) {
        throw new Error('Failed to fetch connections')
      }
      
      const data = await response.json()
      console.log('Fetched connections:', data)
      
      const formattedConnections = data.map((item: any) => ({
        id: String(item.id),
        name: item.name,
        source_id: Number(item.source_id),
        source_db_name: item.source_db_name,
        destination_id: Number(item.destination_id),
        destination_name: item.destination_name,
        schedule_type: item.schedule_type,
        cron_expression: item.cron_expression,
        timezone: item.timezone || 'UTC',
        is_active: !!item.is_active,
        connection_state: item.connection_state,
        last_run_at: item.last_run_at,
        next_run_at: item.next_run_at,
        created_at: item.created_at,
        updated_at: item.updated_at,
      }))

      setConnections(formattedConnections)
    } catch (err) {
      console.error('Error fetching connections:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
  }, [])

  return (
    <ConnectionsContext.Provider
      value={{
        connections,
        isLoading,
        error,
        selectedConnection,
        setSelectedConnection,
        isAddDialogOpen,
        setIsAddDialogOpen,
        isEditDialogOpen,
        setIsEditDialogOpen,
        isDeleteDialogOpen,
        setIsDeleteDialogOpen,
        refreshConnections: fetchConnections
      }}
    >
      {children}
    </ConnectionsContext.Provider>
  )
}

export function useConnectionsContext() {
  const context = useContext(ConnectionsContext)
  
  if (context === undefined) {
    throw new Error('useConnectionsContext must be used within a ConnectionsProvider')
  }
  
  return context
}