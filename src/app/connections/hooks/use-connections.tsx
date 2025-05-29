import { useState, useEffect } from 'react'
import { Connection } from '../data/schema'

export function useConnections() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

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
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
      console.error('Error fetching connections:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
  }, [])

  return { connections, isLoading, error, refetch: fetchConnections }
}