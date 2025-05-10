'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Source } from '../data/schema'
import { DataTableColumnHeader } from './data-table-column-header'
import { DataTableRowActions } from './data-table-row-actions'
// import { sourceStatusStyles } from '../data/data'
import { formatDistanceToNow, isValid, parseISO } from 'date-fns'

export const columns: ColumnDef<Source>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
    cell: ({ row }) => <div className="font-medium">{row.getValue('name')}</div>,
  },
  {
    accessorKey: 'host',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Host" />
    ),
    cell: ({ row }) => <div>{row.getValue('host')}</div>,
  },
  {
    accessorKey: 'port',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Port" />
    ),
    cell: ({ row }) => <div>{row.getValue('port')}</div>,
  },
  {
    accessorKey: 'database',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Database" />
    ),
    cell: ({ row }) => <div>{row.getValue('database')}</div>,
  },
  {
    accessorKey: 'user',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="User" />
    ),
    cell: ({ row }) => <div>{row.getValue('user')}</div>,
  },
  {
    accessorKey: 'status',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      const styles = sourceStatusStyles.get(status as any) || ''
      
      return (
        <Badge variant="outline" className={`${styles} px-2 py-0.5`}>
          {status}
        </Badge>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'created_at',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Created" />
    ),
    cell: ({ row }) => {
      const date = row.getValue('created_at')
      
      // Handle the date safely
      if (!date) return <div>-</div>
      
      try {
        // Format the date safely
        let formattedDate
        if (typeof date === 'string') {
          const parsedDate = parseISO(date)
          formattedDate = isValid(parsedDate) 
            ? new Date(parsedDate).toLocaleDateString() 
            : '-'
        } else {
          formattedDate = date instanceof Date && isValid(date) 
            ? date.toLocaleDateString() 
            : '-'
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
      const source = row.original
      return <DataTableRowActions source={source} />
    },
  },
]

export const sourceStatusStyles = new Map([
  ['active', 'bg-green-50 text-green-700 border-green-300'],
  ['inactive', 'bg-gray-50 text-gray-700 border-gray-300'],
])