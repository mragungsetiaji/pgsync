import { z } from 'zod'

// Destination schema definitions
export const destinationStatusSchema = z.union([
  z.literal('active'),
  z.literal('inactive'),
  z.literal('suspended'),
])
export type DestinationStatus = z.infer<typeof destinationStatusSchema>
export const destinationTypeSchema = z.union([
  z.literal('bigquery'),
  z.literal('snowflake'),
  z.literal('redshift'),
  z.literal('postgres'),
])
export type DestinationType = z.infer<typeof destinationTypeSchema>
export const destinationSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: destinationTypeSchema,
  project_id: z.string().optional(),
  dataset: z.string().optional(),
  bucket_name: z.string().optional(),
  folder_path: z.string().optional(),
  is_active: z.boolean().default(true),
  created_at: z.coerce.date().optional(),
  updated_at: z.coerce.date().optional()
})
export type Destination = z.infer<typeof destinationSchema>

export const destinationListSchema = z.array(destinationSchema)
export const destinationCreateSchema = z.object({
  name: z.string().min(1, { message: 'Name is required' }),
  type: z.literal('bigquery'),
  project_id: z.string().min(1, { message: 'Project ID is required' }),
  dataset: z.string().min(1, { message: 'Dataset is required' }),
  credentials: z.string().min(1, { message: 'Service account credentials are required' }),
  bucket_name: z.string().min(1, { message: 'GCS bucket name is required' }),
  folder_path: z.string().optional(),
  hmac_key: z.string().optional(),
  hmac_secret: z.string().optional(),
  is_active: z.boolean().default(true)
})
export type DestinationCreate = z.infer<typeof destinationCreateSchema>
export const destinationUpdateSchema = destinationCreateSchema.partial()
export type DestinationUpdate = z.infer<typeof destinationUpdateSchema>

export const testBigQueryConnectionSchema = z.object({
  project_id: z.string().min(1, { message: 'Project ID is required' }),
  dataset: z.string().min(1, { message: 'Dataset is required' }),
  credentials: z.string().min(1, { message: 'Service account credentials are required' }),
  bucket_name: z.string().min(1, { message: 'GCS bucket name is required' }),
  folder_path: z.string().optional(),
  hmac_key: z.string().optional(),
  hmac_secret: z.string().optional()
})
export type TestBigQueryConnection = z.infer<typeof testBigQueryConnectionSchema>