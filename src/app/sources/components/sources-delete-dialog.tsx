'use client'

import { Source } from '../data/schema'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

interface SourcesDeleteDialogProps {
  source: Source | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onDelete: () => Promise<void>
}

export function SourcesDeleteDialog({
  source,
  open,
  onOpenChange,
  onDelete
}: SourcesDeleteDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  
  const handleDelete = async () => {
    if (!source) return
    
    setIsDeleting(true)
    try {
      await onDelete()
    } catch (error) {
      console.error('Error in delete handler:', error)
    } finally {
      setIsDeleting(false)
    }
  }
  
  if (!source) return null
  
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete the source <strong>{source.name}</strong>.
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
          <Button 
            variant="destructive" 
            onClick={handleDelete} 
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}