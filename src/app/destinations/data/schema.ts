import { z } from 'zod'

const userStatusSchema = z.union([
  z.literal('active'),
  z.literal('inactive'),
  z.literal('invited'),
  z.literal('suspended'),
])
export type UserStatus = z.infer<typeof userStatusSchema>

const userRoleSchema = z.union([
  z.literal('superadmin'),
  z.literal('admin'),
  z.literal('cashier'),
  z.literal('manager'),
])

const userSchema = z.object({
  id: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  username: z.string(),
  email: z.string(),
  phoneNumber: z.string(),
  status: userStatusSchema,
  role: userRoleSchema,
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
})
export type User = z.infer<typeof userSchema>

export const userListSchema = z.array(userSchema)

// Destination schema definitions
const destinationStatusSchema = z.union([
  z.literal('active'),
  z.literal('inactive'),
  z.literal('suspended'),
])
export type DestinationStatus = z.infer<typeof destinationStatusSchema>

const connectorTypeSchema = z.union([
  z.literal('bigquery'),
  z.literal('snowflake'),
  z.literal('redshift'),
  z.literal('postgres'),
])
export type ConnectorType = z.infer<typeof connectorTypeSchema>

const destinationSchema = z.object({
  id: z.string(),
  name: z.string(),
  connector: connectorTypeSchema,
  dataset: z.string(),
  lastSync: z.coerce.date(),
  status: destinationStatusSchema,
})
export type Destination = z.infer<typeof destinationSchema>

export const destinationListSchema = z.array(destinationSchema)