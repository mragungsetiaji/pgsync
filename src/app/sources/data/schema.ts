import { z } from 'zod'

// source schema definitions
const sourceStatusSchema = z.union([
  z.literal('active'),
  z.literal('inactive'),
  z.literal('suspended'),
])
export type SourceStatus = z.infer<typeof sourceStatusSchema>

const connectorTypeSchema = z.union([
  z.literal('bigquery'),
  z.literal('snowflake'),
  z.literal('redshift'),
  z.literal('postgres'),
])
export type ConnectorType = z.infer<typeof connectorTypeSchema>

const sourceSchema = z.object({
  id: z.string(),
  name: z.string(),
  connector: connectorTypeSchema,
  dataset: z.string(),
  lastSync: z.coerce.date(),
  status: sourceStatusSchema,
})
export type Source = z.infer<typeof sourceSchema>

export const sourceListSchema = z.array(sourceSchema)