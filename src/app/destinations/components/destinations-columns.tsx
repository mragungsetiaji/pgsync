import { ColumnDef } from '@tanstack/react-table'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import LongText from '@/components/long-text'
import { destinationStatusStyles  } from '../data/data'
import { Destination } from '../data/schema'
import { DataTableColumnHeader } from './data-table-column-header'
import { DataTableRowActions } from './data-table-row-actions'
import { formatDistanceToNow } from 'date-fns'
import { Database, Server } from 'lucide-react'

export const destcolumns: ColumnDef<Destination>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate')
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label='Select all'
        className='translate-y-[2px]'
      />
    ),
    meta: {
      className: cn(
        'sticky md:table-cell left-0 z-10 rounded-tl',
        'bg-background transition-colors duration-200 group-hover/row:bg-muted group-data-[state=selected]/row:bg-muted'
      ),
    },
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label='Select row'
        className='translate-y-[2px]'
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Name' />
    ),
    cell: ({ row }) => (
      <LongText className='max-w-36'>{row.getValue('name')}</LongText>
    ),
    meta: {
      className: cn(
        'drop-shadow-[0_1px_2px_rgb(0_0_0_/_0.1)] dark:drop-shadow-[0_1px_2px_rgb(255_255_255_/_0.1)] lg:drop-shadow-none',
        'bg-background transition-colors duration-200 group-hover/row:bg-muted group-data-[state=selected]/row:bg-muted',
        'sticky left-6 md:table-cell'
      ),
    },
    enableHiding: false,
  },
  {
    accessorKey: 'type',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Type' />
    ),
    cell: ({ row }) => {
      const connector = row.getValue('type') as string
      return (
        <div className='flex gap-x-2 items-center'>
          <Server size={16} className='text-muted-foreground' />
          <span className='capitalize text-sm'>{connector}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
    enableSorting: false,
  },
  {
    accessorKey: 'dataset',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Dataset' />
    ),
    cell: ({ row }) => {
      return (
        <div className='flex gap-x-2 items-center'>
          <Database size={16} className='text-muted-foreground' />
          <span className='text-sm'>{row.getValue('dataset')}</span>
        </div>
      )
    },
  },
  {
    accessorKey: 'last_synced_at',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Last Sync' />
    ),
    cell: ({ row }) => {
      const date = row.getValue('last_synced_at') as Date | null

      // If date is null, return an empty div or "Never synced" message
      if (!date) {
        return <div className="text-sm text-muted-foreground">-</div>
      }

      return (
        <div className='text-sm'>
          {formatDistanceToNow(date, { addSuffix: true })}
        </div>
      )
    },
    // Optional: If you want to ensure these rows appear at the bottom when sorting
    sortingFn: (rowA, rowB, columnId) => {
      const dateA = rowA.getValue(columnId) as Date | null
      const dateB = rowB.getValue(columnId) as Date | null

      // Handle null values in sorting
      if (!dateA && !dateB) return 0
      if (!dateA) return 1 // null values at the end
      if (!dateB) return -1

      return dateA.getTime() - dateB.getTime()
    }
  },
  {
    accessorKey: 'status',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Status' />
    ),
    cell: ({ row }) => {
      const { status } = row.original
      const badgeColor = destinationStatusStyles .get(status)
      return (
        <div className='flex space-x-2'>
          <Badge variant='outline' className={cn('capitalize', badgeColor)}>
            {row.getValue('status')}
          </Badge>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
    enableHiding: false,
    enableSorting: false,
  },
  {
    id: 'actions',
    cell: DataTableRowActions,
  },
]