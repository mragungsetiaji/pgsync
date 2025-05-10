import { useState, useEffect } from 'react'
import { Destination } from '../data/schema'

export function useDestinations() {
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDestinations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/destinations')
      
      if (!response.ok) {
        throw new Error('Failed to fetch destinations')
      }
      
      const data = await response.json()
      
      // Transform the API response to match your frontend schema
      const formattedDestinations = data.map((item: any) => ({
        id: item.id.toString(),
        name: item.name,
        type: 'bigquery', // Since we're only supporting BigQuery for now
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
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
      console.error('Error fetching destinations:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDestinations()
  }, [])

  return { destinations, isLoading, error, refetch: fetchDestinations }
}