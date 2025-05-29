'use client'

import { Main } from '@/components/layout/main'
import { ConnectionsPrimaryButtons } from './components/connections-primary-buttons'
import { ConnectionsTable } from './components/connections-table'
import { columns } from './components/connections-columns'
import { ConnectionsProvider } from './context/connections-context'
import { ConnectionsDialogs } from './components/connections-dialogs'
import { useConnectionsContext } from './context/connections-context'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

export default function ConnectionsPage() {
  return (
    <ConnectionsProvider>
      <ConnectionsContent />
    </ConnectionsProvider>
  )
}

// Export ConnectionsContent component so it can be imported directly
export function ConnectionsContent() {
  const { connections, isLoading, error } = useConnectionsContext()

  return (
    <Main>
      <div className='mb-2 flex items-center justify-between space-y-2 flex-wrap'>
        <div>
          <h2 className='text-2xl font-bold tracking-tight'>Connections</h2>
          <p className='text-muted-foreground'>
            Manage connections between sources and destinations.
          </p>
        </div>
        <ConnectionsPrimaryButtons />
      </div>
      <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
        {isLoading ? (
          <div className="space-y-3 p-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : error ? (
          <Alert variant="destructive" className="my-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : (
          <ConnectionsTable data={connections} columns={columns} />
        )}
      </div>
      <ConnectionsDialogs />
    </Main>
  )
}