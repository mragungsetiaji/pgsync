'use client'

import { useConnectionsContext } from '../context/connections-context'
import { ConnectionsActionDialog } from './connections-action-dialog'
import { ConnectionsDeleteDialog } from './connections-delete-dialog'

export function ConnectionsDialogs() {
  const {
    selectedConnection,
    setSelectedConnection,
    isAddDialogOpen, 
    setIsAddDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    isDeleteDialogOpen,
    setIsDeleteDialogOpen,
    refreshConnections
  } = useConnectionsContext()
  
  return (
    <>
      {/* Add Dialog */}
      <ConnectionsActionDialog
        open={isAddDialogOpen}
        onOpenChange={(open) => {
          setIsAddDialogOpen(open)
          if (!open) setSelectedConnection(null)
        }}
        onSubmitSuccess={() => {
          refreshConnections()
        }}
      />
      
      {/* Edit Dialog */}
      <ConnectionsActionDialog
        currentRow={selectedConnection!}
        open={isEditDialogOpen}
        onOpenChange={(open) => {
          setIsEditDialogOpen(open)
          if (!open) setSelectedConnection(null)
        }}
        onSubmitSuccess={() => {
          refreshConnections()
        }}
      />
      
      {/* Delete Dialog */}
      <ConnectionsDeleteDialog 
        connection={selectedConnection}
        open={isDeleteDialogOpen}
        onOpenChange={(open) => {
          setIsDeleteDialogOpen(open)
          if (!open) setSelectedConnection(null)
        }}
        onDelete={async () => {
          if (!selectedConnection) return
          
          try {
            const response = await fetch(`/api/connections/${selectedConnection.id}`, {
              method: 'DELETE',
            })
            
            if (!response.ok) {
              throw new Error('Failed to delete connection')
            }
            
            await refreshConnections()
            setIsDeleteDialogOpen(false)
            setSelectedConnection(null)
          } catch (error) {
            console.error('Error deleting connection:', error)
          }
        }}
      />
    </>
  )
}