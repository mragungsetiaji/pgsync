'use client'

import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { destcolumns } from './components/destinations-columns'
import { DestinationsDialogs } from './components/destinations-dialogs'
import { DestinationsPrimaryButtons } from './components/destinations-primary-buttons'
import { DestinationsTable } from './components/destinations-table'
import DestinationsProvider from './context/destinations-context'
import { destinationListSchema } from './data/schema'
import { destinations } from './data/destinations'

export default function Destinations() {
  const destinationList = destinationListSchema.parse(destinations)

  return (
    <DestinationsProvider>
      <Header fixed>
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

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
          {/* <UsersTable data={userList} columns={columns} /> */}
          <DestinationsTable data={destinationList} columns={destcolumns} />
        </div>
      </Main>

      <DestinationsDialogs />
    </DestinationsProvider>
  )
}
