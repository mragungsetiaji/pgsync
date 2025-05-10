'use client'

import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { SourcesPrimaryButtons } from './components/sources-primary-buttons'
import { SourcesTable } from './components/sources-table'
import { columns } from './components/sources-columns'
import { SourcesProvider } from './context/sources-context'
import { SourcesDialogs } from './components/sources-dialogs'
import { useSourcesContext } from './context/sources-context'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

export default function SourcesPage() {
  return (
    <SourcesProvider>
      <SourcesContent />
    </SourcesProvider>
  )
}

function SourcesContent() {
  const { sources, isLoading, error } = useSourcesContext()

  return (
    <Main>
      <div className='mb-2 flex items-center justify-between space-y-2 flex-wrap'>
        <div>
          <h2 className='text-2xl font-bold tracking-tight'>Source List</h2>
          <p className='text-muted-foreground'>
            Manage database sources.
          </p>
        </div>
        <SourcesPrimaryButtons />
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
          <SourcesTable data={sources} columns={columns} />
        )}
      </div>

      <SourcesDialogs />
    </Main>
  )
}