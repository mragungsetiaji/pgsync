'use client'

import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { columns } from './components/sources-columns'
import { SourcesDialogs } from './components/sources-dialogs'
import { SourcesPrimaryButtons } from './components/sources-primary-buttons'
import { SourcesTable } from './components/sources-table'
import SourcesProvider from './context/sources-context'
import { sourceListSchema } from './data/schema'
import { sources } from './data/sources'

export default function Sources() {
  const sourceList = sourceListSchema.parse(sources)

  return (
    <SourcesProvider>
      <Header fixed>
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className='mb-2 flex items-center justify-between space-y-2 flex-wrap'>
          <div>
            <h2 className='text-2xl font-bold tracking-tight'>Source List</h2>
            <p className='text-muted-foreground'>
              Manage Sources.
            </p>
          </div>
          <SourcesPrimaryButtons />
        </div>
        <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
          <SourcesTable data={sourceList} columns={columns} />
        </div>
      </Main>

      <SourcesDialogs />
    </SourcesProvider>
  )
}
