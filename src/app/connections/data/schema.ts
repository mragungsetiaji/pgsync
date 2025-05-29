import { z } from 'zod'

export const connectionStatusValues = ['active', 'inactive'] as const
export const scheduleTypeValues = ['manual', 'cron'] as const

export const connectionStatusSchema = z.enum(connectionStatusValues)
export const scheduleTypeSchema = z.enum(scheduleTypeValues)

export const connectionSchema = z.object({
  id: z.string().or(z.number()).transform(val => String(val)),
  name: z.string(),
  source_id: z.number().or(z.string()).transform(val => Number(val)),
  source_db_name: z.string().optional(),
  destination_id: z.number().or(z.string()).transform(val => Number(val)),
  destination_name: z.string().optional(),
  schedule_type: scheduleTypeSchema,
  cron_expression: z.string().nullable().optional(),
  timezone: z.string().default("UTC"),
  is_active: z.boolean(),
  connection_state: z.record(z.any()).nullable().optional(),
  last_run_at: z.string().or(z.date()).nullable().optional(),
  next_run_at: z.string().or(z.date()).nullable().optional(),
  created_at: z.string().or(z.date()).optional(),
  updated_at: z.string().or(z.date()).optional()
})

export type Connection = z.infer<typeof connectionSchema>

export const connectionCreateSchema = z.object({
  name: z.string().min(1, { message: 'Name is required' }),
  source_db_id: z.number().positive({ message: 'Source is required' }),
  destination_id: z.number().positive({ message: 'Destination is required' }),
  schedule_type: scheduleTypeSchema.default('manual'),
  cron_expression: z.string().nullable().optional(),
  timezone: z.string().default("UTC"),
  is_active: z.boolean().default(true),
  connection_state: z.record(z.any()).nullable().optional(),
})

export type ConnectionCreate = z.infer<typeof connectionCreateSchema>

export const connectionUpdateSchema = connectionCreateSchema.partial()
export type ConnectionUpdate = z.infer<typeof connectionUpdateSchema>