'use client'

import { useState } from 'react'
import { MoreHorizontal, Pencil, Trash, Power } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Connection } from '../data/schema'
import { useConnectionsContext } from '../context/connections-context'
import { toast } from '@/hooks/use-toast'

interface DataTableRowActionsProps {
  connection: Connection
}

export function DataTableRowActions({ connection }: DataTableRowActionsProps) {
  const {
    setSelectedConnection,
    setIsEditDialogOpen,
    setIsDeleteDialogOpen,
    refreshConnections
  } = useConnectionsContext()

  const [isToggling, setIsToggling] = useState(false)

  // Safety check - ensure connection exists and has required properties
  if (!connection || typeof connection !== 'object') {
    console.error("Invalid connection object:", connection)
    return null;
  }

  const handleEdit = () => {
    setSelectedConnection(connection)
    setIsEditDialogOpen(true)
  }

  const handleDeleteClick = () => {
    setSelectedConnection(connection)
    setIsDeleteDialogOpen(true)
  }

  const handleToggleActive = async () => {
    setIsToggling(true)
    try {
      const response = await fetch(`/api/connections/${connection.id}/toggle`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to toggle connection status')
      }

      toast({
        title: 'Connection status updated',
        description: `Connection ${connection.name} has been ${connection.is_active ? 'disabled' : 'enabled'}`
      })

      await refreshConnections()
    } catch (error) {
      console.error('Error toggling connection status:', error)
      toast({
        title: 'Error',
        description: 'Failed to update connection status',
        variant: 'destructive'
      })
    } finally {
      setIsToggling(false)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={handleEdit}>
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={handleToggleActive}
          disabled={isToggling}
        >
          <Power className="mr-2 h-4 w-4" />
          {connection.is_active ? 'Disable' : 'Enable'}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleDeleteClick} className="text-red-600">
          <Trash className="mr-2 h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}