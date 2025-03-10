'use client'

import { useState } from 'react'
import { IconAlertTriangle } from '@tabler/icons-react'
import { toast } from '@/hooks/use-toast'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { Destination } from '../data/schema'

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentDestination: Destination
  onDeleteSuccess?: () => void
}

export function DestinationsDeleteDialog({ 
  open, 
  onOpenChange, 
  currentDestination,
  onDeleteSuccess 
}: Props) {
  const [value, setValue] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    if (value.trim() !== currentDestination.name) return
    
    try {
      setIsDeleting(true)
      
      const response = await fetch(`/api/destinations/${currentDestination.id}`, {
        method: 'DELETE',
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete destination')
      }
      
      onOpenChange(false)
      setValue('')
      
      toast({
        title: 'Destination deleted',
        description: `${currentDestination.name} has been deleted successfully`,
      })
      
      if (onDeleteSuccess) {
        onDeleteSuccess()
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete destination',
        variant: 'destructive',
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={(newOpen) => {
        if (!newOpen) {
          setValue('')
        }
        onOpenChange(newOpen)
      }}
      handleConfirm={handleDelete}
      disabled={value.trim() !== currentDestination.name || isDeleting}
      title={
        <span className='text-destructive'>
          <IconAlertTriangle
            className='mr-1 inline-block stroke-destructive'
            size={18}
          />{' '}
          Delete Destination
        </span>
      }
      desc={
        <div className='space-y-4'>
          <p className='mb-2'>
            Are you sure you want to delete{' '}
            <span className='font-bold'>{currentDestination.name}</span>?
            <br />
            This action will permanently remove this BigQuery destination 
            and all associated configuration. This cannot be undone.
          </p>

          <Label className='my-2'>
            To confirm, type the destination name:
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={`Type "${currentDestination.name}" to confirm`}
              className="mt-1"
            />
          </Label>

          <Alert variant='destructive'>
            <AlertTitle>Warning!</AlertTitle>
            <AlertDescription>
              This will permanently delete the destination and cannot be reversed.
              Any pipelines using this destination may fail.
            </AlertDescription>
          </Alert>
        </div>
      }
      confirmText={isDeleting ? 'Deleting...' : 'Delete'}
      destructive
    />
  )
}