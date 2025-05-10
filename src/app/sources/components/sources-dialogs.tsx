'use client'

import { useSourcesContext } from '../context/sources-context'
import { SourcesActionDialog } from './sources-action-dialog'
import { SourcesDeleteDialog } from './sources-delete-dialog'

export function SourcesDialogs() {
  const {
    selectedSource,
    setSelectedSource,
    isAddDialogOpen, 
    setIsAddDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    isDeleteDialogOpen,
    setIsDeleteDialogOpen,
    refreshSources
  } = useSourcesContext()
  
  return (
    <>
      {/* Add Dialog */}
      <SourcesActionDialog
        open={isAddDialogOpen}
        onOpenChange={(open) => {
          setIsAddDialogOpen(open)
          if (!open) setSelectedSource(null)
        }}
        onSubmitSuccess={() => {
          refreshSources()
        }}
      />
      
      {/* Edit Dialog */}
      <SourcesActionDialog
        currentRow={selectedSource!}
        open={isEditDialogOpen}
        onOpenChange={(open) => {
          setIsEditDialogOpen(open)
          if (!open) setSelectedSource(null)
        }}
        onSubmitSuccess={() => {
          refreshSources()
        }}
      />
      
      {/* Delete Dialog */}
      <SourcesDeleteDialog 
        source={selectedSource}
        open={isDeleteDialogOpen}
        onOpenChange={(open) => {
          setIsDeleteDialogOpen(open)
          if (!open) setSelectedSource(null)
        }}
        onDelete={async () => {
          if (!selectedSource) return
          
          try {
            const response = await fetch(`/api/sources/${selectedSource.id}`, {
              method: 'DELETE',
            })
            
            if (!response.ok) {
              throw new Error('Failed to delete source')
            }
            
            await refreshSources()
            setIsDeleteDialogOpen(false)
            setSelectedSource(null)
          } catch (error) {
            console.error('Error deleting source:', error)
          }
        }}
      />
    </>
  )
}