import { z } from 'zod'

export const sourceStatusValues = ['active', 'inactive'] as const

export const sourceStatusSchema = z.enum(sourceStatusValues)

export const sourceSchema = z.object({
  id: z.string(),
  name: z.string(),
  host: z.string(),
  port: z.number().int().positive(),
  database: z.string(),
  user: z.string(),
  status: sourceStatusSchema,
  created_at: z.coerce.date().optional(),
  updated_at: z.coerce.date().optional()
})

export type Source = z.infer<typeof sourceSchema>

export const sourceListSchema = z.array(sourceSchema)

export const sourceCreateSchema = z.object({
  name: z.string().min(1, { message: 'Name is required' }),
  host: z.string().min(1, { message: 'Host is required' }),
  port: z.number().int().positive().default(5432),
  database: z.string().min(1, { message: 'Database name is required' }),
  user: z.string().min(1, { message: 'Username is required' }),
  password: z.string().min(1, { message: 'Password is required' }),
})

export type SourceCreate = z.infer<typeof sourceCreateSchema>

export const sourceUpdateSchema = sourceCreateSchema.partial()
export type SourceUpdate = z.infer<typeof sourceUpdateSchema>

export const testDbConnectionSchema = z.object({
  host: z.string().min(1, { message: 'Host is required' }),
  port: z.number().int().positive(),
  database: z.string().min(1, { message: 'Database name is required' }),
  user: z.string().min(1, { message: 'Username is required' }),
  password: z.string().min(1, { message: 'Password is required' }),
})