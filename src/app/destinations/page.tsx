'use client'

import { Main } from '@/components/layout/main'
import { DestinationsPrimaryButtons } from './components/destinations-primary-buttons'
import { DestinationsTable } from './components/destinations-table'
import { destcolumns } from './components/destinations-columns'
import { DestinationsProvider } from './context/destinations-context'
import { DestinationsDialogs } from './components/destinations-dialogs'
import { useDestinationsContext } from './context/destinations-context'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

export default function DestinationsPage() {
  return (
    <DestinationsProvider>
      <DestinationsContent />
    </DestinationsProvider>
  )
}

function DestinationsContent() {
  const { destinations, isLoading, error } = useDestinationsContext()

  return (
    <Main>
      <div className='mb-2 flex items-center justify-between space-y-2 flex-wrap'>
        <div>
          <h2 className='text-2xl font-bold tracking-tight'>Destination List</h2>
          <p className='text-muted-foreground'>
            Manage destinations.
          </p>
        </div>
        <DestinationsPrimaryButtons />
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
          <DestinationsTable data={destinations} columns={destcolumns} />
        )}
      </div>

      <DestinationsDialogs />
    </Main>
  )
}