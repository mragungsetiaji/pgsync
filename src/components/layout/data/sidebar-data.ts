'use client'

import {
  IconBarrierBlock,
  IconBrowserCheck,
  IconBug,
  IconChecklist,
  IconError404,
  IconHelp,
  IconLayoutDashboard,
  IconLock,
  IconLockAccess,
  IconMessages,
  IconNotification,
  IconPackages,
  IconPalette,
  IconServerOff,
  IconSettings,
  IconTool,
  IconUserCog,
  IconUserOff,
  IconUsers,
} from '@tabler/icons-react'
import { AudioWaveform, Command, GalleryVerticalEnd } from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: SidebarData = {
  user: {
    name: 'admin',
    email: 'admin@gmail.com',
    avatar: '/avatars/01.png',
  },
  teams: [
    {
      name: 'PGSync Admin',
      logo: Command,
      plan: 'Pro',
    },
  ],
  navGroups: [
    {
      title: 'General',
      items: [
        {
          title: 'Connections',
          url: '/',
          icon: IconLayoutDashboard,
        },
        {
          title: 'Sources',
          url: '/sources',
          icon: IconChecklist,
        },
        {
          title: 'Destinations',
          url: '/destinations',
          icon: IconUsers,
        },
      ],
    },
    {
      title: 'Other',
      items: [
        {
          title: 'Settings',
          icon: IconSettings,
          items: [
            {
              title: 'Notifications',
              url: '/settings/notifications',
              icon: IconNotification,
            },
          ],
        },
      ],
    },
  ],
}
