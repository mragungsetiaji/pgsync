'use client'

import { useState } from 'react'
import { MoreHorizontal, Pencil, Trash } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
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
import { Source } from '../data/schema'
import { useSourcesContext } from '../context/sources-context'

interface DataTableRowActionsProps {
  source: Source
}

export function DataTableRowActions({ source }: DataTableRowActionsProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const { 
    setSelectedSource, 
    setIsEditDialogOpen,
    setIsDeleteDialogOpen 
  } = useSourcesContext()

  // Safety check - ensure source exists and has required properties
  if (!source || typeof source !== 'object') {
    console.error("Invalid source object:", source)
    return null;
  }

  const handleEdit = () => {
    setSelectedSource(source)
    setIsEditDialogOpen(true)
  }

  const handleDeleteClick = () => {
    setSelectedSource(source)
    setIsDeleteDialogOpen(true)
  }

  return (
    <>
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
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleDeleteClick} className="text-red-600">
            <Trash className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  )
}