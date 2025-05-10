import { z } from 'zod'

export const sourceStatusValues = ['active', 'inactive', 'suspended'] as const

export const sourceStatusSchema = z.enum(sourceStatusValues)

export const sourceSchema = z.object({
  id: z.string().or(z.number()).transform(val => String(val)),
  name: z.string(),
  // Make these fields optional to handle missing data
  host: z.string().optional(),
  port: z.number().int().positive().optional(),
  database: z.string().optional(),
  user: z.string().optional(),
  // Handle status
  status: z.string().optional().transform(val => 
    val && sourceStatusValues.includes(val as any) ? val : 'inactive'
  ),
  is_active: z.boolean().optional(),
  created_at: z.string().or(z.date()).optional(),
  updated_at: z.string().or(z.date()).optional()
})

export type Source = {
  id: string;
  name: string;
  host?: string;
  port?: number;
  database?: string;
  user?: string;
  status: string;
  created_at?: Date | string;
  updated_at?: Date | string;
}

export const sourceListSchema = z.array(
  // More flexible schema for incoming data
  z.object({
    id: z.union([z.string(), z.number()]),
    name: z.string(),
    host: z.string().optional(),
    port: z.number().optional(),
    database: z.string().optional(),
    user: z.string().optional(),
    status: z.string().optional(),
    is_active: z.boolean().optional(),
    created_at: z.string().or(z.date()).optional(),
    updated_at: z.string().or(z.date()).optional()
  })
)

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