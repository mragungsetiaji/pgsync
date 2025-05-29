'use client'

import { Header } from '@/components/layout/header'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'

// Import ConnectionsPage component and required context
import { ConnectionsProvider } from './connections/context/connections-context'
import ConnectionsContent from './connections/page'

export default function Dashboard() {
  return (
    <>
      {/* ===== Top Heading ===== */}
      <Header>
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      {/* Use the ConnectionsProvider and ConnectionsContent */}
      <ConnectionsProvider>
        <ConnectionsContent />
      </ConnectionsProvider>
    </>
  )
}