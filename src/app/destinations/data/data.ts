'use client'

import {
  IconCash,
  IconShield,
  IconUsersGroup,
  IconUserShield,
} from '@tabler/icons-react'
import { DestinationStatus, DestinationType } from './schema'

export const destinationStatusStyles = new Map<DestinationStatus, string>([
  ['active', 'bg-teal-100/30 text-teal-900 dark:text-teal-200 border-teal-200'],
  ['inactive', 'bg-neutral-300/40 border-neutral-300'],
  ['suspended', 'bg-destructive/10 dark:bg-destructive/50 text-destructive dark:text-primary border-destructive/10'],
])

export const destinationTypes = [
  { label: 'BigQuery', value: 'bigquery' as DestinationType },
  { label: 'Snowflake', value: 'snowflake' as DestinationType },
  { label: 'Redshift', value: 'redshift' as DestinationType },
]
