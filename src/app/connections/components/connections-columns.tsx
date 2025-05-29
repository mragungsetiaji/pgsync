'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Connection } from '../data/schema'
import { DataTableColumnHeader } from './data-table-column-header'
import { DataTableRowActions } from './data-table-row-actions'
import { formatDistanceToNow, isValid, parseISO } from 'date-fns'

export const columns: ColumnDef<Connection>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
    cell: ({ row }) => <div className="font-medium">{row.getValue('name')}</div>,
  },
  {
    accessorKey: 'source_db_name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Source" />
    ),
    cell: ({ row }) => <div>{row.getValue('source_db_name')}</div>,
  },
  {
    accessorKey: 'destination_name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Destination" />
    ),
    cell: ({ row }) => <div>{row.getValue('destination_name')}</div>,
  },
  {
    accessorKey: 'schedule_type',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Schedule" />
    ),
    cell: ({ row }) => {
      const type = row.getValue('schedule_type') as string
      const cronExp = row.original.cron_expression
      
      return (
        <div>
          <Badge variant="outline" className="capitalize">
            {type}
          </Badge>
          {type === 'cron' && cronExp && (
            <span className="ml-2 text-xs text-muted-foreground">{cronExp}</span>
          )}
        </div>
      )
    }
  },
  {
    accessorKey: 'is_active',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => {
      const isActive = row.getValue('is_active') as boolean
      
      return (
        <Badge 
          variant={isActive ? "default" : "secondary"} 
          className="capitalize"
        >
          {isActive ? 'Active' : 'Inactive'}
        </Badge>
      )
    },
  },
  {
    accessorKey: 'last_run_at',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Last Run" />
    ),
    cell: ({ row }) => {
      const date = row.getValue('last_run_at')
      
      if (!date) return <div>Never</div>
      
      try {
        let formattedDate
        if (typeof date === 'string') {
          const parsedDate = parseISO(date)
          formattedDate = isValid(parsedDate) 
            ? formatDistanceToNow(parsedDate, { addSuffix: true }) 
            : 'Invalid date'
        } else {
          formattedDate = date instanceof Date && isValid(date) 
            ? formatDistanceToNow(date, { addSuffix: true }) 
            : 'Invalid date'
        }
        
        return <div className='text-sm'>{formattedDate}</div>
      } catch (error) {
        console.error('Error formatting date:', error, date)
        return <div>Invalid date</div>
      }
    },
  },
  {
    accessorKey: 'next_run_at',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Next Run" />
    ),
    cell: ({ row }) => {
      const date = row.getValue('next_run_at')
      const scheduleType = row.getValue('schedule_type')
      
      if (scheduleType === 'manual' || !date) return <div>-</div>
      
      try {
        let formattedDate
        if (typeof date === 'string') {
          const parsedDate = parseISO(date)
          formattedDate = isValid(parsedDate) 
            ? formatDistanceToNow(parsedDate, { addSuffix: true }) 
            : 'Invalid date'
        } else {
          formattedDate = date instanceof Date && isValid(date) 
            ? formatDistanceToNow(date, { addSuffix: true }) 
            : 'Invalid date'
        }
        
        return <div className='text-sm'>{formattedDate}</div>
      } catch (error) {
        console.error('Error formatting date:', error, date)
        return <div>Invalid date</div>
      }
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const connection = row.original
      return <DataTableRowActions connection={connection} />
    },
  },
]