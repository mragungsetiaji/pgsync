import { z } from 'zod'

export const connectionStatusSchema = z.union([
  z.literal('active'),
  z.literal('inactive'),
  z.literal('suspended'),
])
export type ConnectionStatus = z.infer<typeof connectionStatusSchema>

export const connectorTypeSchema = z.union([
  z.literal('bigquery'),
  z.literal('snowflake'),
  z.literal('redshift'),
  z.literal('postgres'),
])
export type ConnectorType = z.infer<typeof connectorTypeSchema>

export const sourceSchema = z.object({
  id: z.string(),
  name: z.string(),
  connector: connectorTypeSchema,
  host: z.string().optional(),
  port: z.number().optional(),
  database: z.string().optional(),
  user: z.string().optional(),
  // We don't include password in the response schema for security
  dataset: z.string().optional(),
  lastSync: z.coerce.date().optional(),
  status: sourceStatusSchema.optional().default('inactive'),
})
export type Source = z.infer<typeof sourceSchema>

export const sourceListSchema = z.array(sourceSchema)

// Schema for creating a new source
export const sourceCreateSchema = z.object({
  name: z.string().min(1),
  connector: connectorTypeSchema,
  host: z.string().min(1),
  port: z.number().int().positive().max(65535),
  database: z.string().min(1),
  user: z.string().min(1),
  password: z.string().min(1),
})
export type SourceCreate = z.infer<typeof sourceCreateSchema>