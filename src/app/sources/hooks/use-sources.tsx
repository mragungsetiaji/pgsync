import { useState, useEffect } from 'react'
import { Source } from '../data/schema'

export function useSources() {
  const [sources, setSources] = useState<Source[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

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
      
      // Transform the API response to match your frontend schema
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
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
      console.error('Error fetching sources:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSources()
  }, [])

  return { sources, isLoading, error, refetch: fetchSources }
}