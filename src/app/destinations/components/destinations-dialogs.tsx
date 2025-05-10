'use client'

import { useDestinationsContext } from '../context/destinations-context'
import { DestinationsActionDialog } from './destinations-action-dialog'
import { DestinationsDeleteDialog } from './destinations-delete-dialog'

export function DestinationsDialogs() {
  const {
    selectedDestination,
    setSelectedDestination,
    isAddDialogOpen, 
    setIsAddDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    isDeleteDialogOpen,
    setIsDeleteDialogOpen,
    refreshDestinations
  } = useDestinationsContext()
  
  return (
    <>
      {/* Add Dialog */}
      <DestinationsActionDialog
        open={isAddDialogOpen}
        onOpenChange={(open) => {
          setIsAddDialogOpen(open)
          if (!open) setSelectedDestination(null)
        }}
        onSubmitSuccess={() => {
          refreshDestinations()
        }}
      />
      
      {/* Edit Dialog */}
      <DestinationsActionDialog
        currentRow={selectedDestination!}
        open={isEditDialogOpen}
        onOpenChange={(open) => {
          setIsEditDialogOpen(open)
          if (!open) setSelectedDestination(null)
        }}
        onSubmitSuccess={() => {
          refreshDestinations()
        }}
      />
      
      {/* Delete Dialog */}
      <DestinationsDeleteDialog 
        destination={selectedDestination}
        open={isDeleteDialogOpen}
        onOpenChange={(open) => {
          setIsDeleteDialogOpen(open)
          if (!open) setSelectedDestination(null)
        }}
        onDelete={async () => {
          if (!selectedDestination) return
          
          try {
            const response = await fetch(`/api/destinations/${selectedDestination.id}`, {
              method: 'DELETE',
            })
            
            if (!response.ok) {
              throw new Error('Failed to delete destination')
            }
            
            await refreshDestinations()
            setIsDeleteDialogOpen(false)
            setSelectedDestination(null)
          } catch (error) {
            console.error('Error deleting destination:', error)
          }
        }}
      />
    </>
  )
}