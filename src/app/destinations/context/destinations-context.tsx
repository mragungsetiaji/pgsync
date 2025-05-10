'use client'

import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { Destination } from '../data/schema'

type DestinationsContextType = {
  destinations: Destination[]
  isLoading: boolean
  error: string | null
  selectedDestination: Destination | null
  setSelectedDestination: (destination: Destination | null) => void
  isAddDialogOpen: boolean
  setIsAddDialogOpen: (isOpen: boolean) => void
  isEditDialogOpen: boolean
  setIsEditDialogOpen: (isOpen: boolean) => void
  isDeleteDialogOpen: boolean
  setIsDeleteDialogOpen: (isOpen: boolean) => void
  refreshDestinations: () => Promise<void>
}

const DestinationsContext = createContext<DestinationsContextType | undefined>(undefined)

export function DestinationsProvider({ children }: { children: ReactNode }) {
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const fetchDestinations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/destinations')
      
      if (!response.ok) {
        throw new Error('Failed to fetch destinations')
      }
      
      const data = await response.json()
      console.log('Fetched destinations:', data) // Add this for debugging
      
      const formattedDestinations = data.map((item: any) => ({
        id: item.id.toString(),
        name: item.name,
        type: 'bigquery',
        project_id: item.project_id,
        dataset: item.dataset,
        bucket_name: item.bucket_name,
        folder_path: item.folder_path,
        last_synced_at: item.last_synced_at ? new Date(item.last_synced_at) : null,
        status: item.is_active ? 'active' : 'inactive',
        created_at: item.created_at ? new Date(item.created_at) : undefined,
        updated_at: item.updated_at ? new Date(item.updated_at) : undefined,
      }))

      setDestinations(formattedDestinations)
    } catch (err) {
      console.error('Error fetching destinations:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDestinations()
  }, [])

  return (
    <DestinationsContext.Provider
      value={{
        destinations,
        isLoading,
        error,
        selectedDestination,
        setSelectedDestination,
        isAddDialogOpen,
        setIsAddDialogOpen,
        isEditDialogOpen,
        setIsEditDialogOpen,
        isDeleteDialogOpen,
        setIsDeleteDialogOpen,
        refreshDestinations: fetchDestinations
      }}
    >
      {children}
    </DestinationsContext.Provider>
  )
}

export function useDestinationsContext() {
  const context = useContext(DestinationsContext)
  
  if (context === undefined) {
    throw new Error('useDestinationsContext must be used within a DestinationsProvider')
  }
  
  return context
}