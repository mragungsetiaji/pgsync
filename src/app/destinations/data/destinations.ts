import { Destination, DestinationType } from './schema'

export const destinations: Destination[] = [
  {
    id: 'bd67f8d2-c12a-4925-9f1c-943512a8d2f0',
    name: 'Production Analytics',
    type: 'bigquery' as DestinationType,
    project_id: 'analytics-prod-123456',
    dataset: 'raw_data',
    bucket_name: 'analytics-staging-bucket',
    folder_path: 'ingestion/postgres',
    is_active: true,
    created_at: new Date('2024-02-20T09:00:00Z'),
    updated_at: new Date('2024-02-25T09:12:33Z')
  },
  {
    id: 'e3a4c15d-b7f9-4d83-a692-58e74c16b021',
    name: 'Marketing Data Warehouse',
    type: 'bigquery' as DestinationType,
    project_id: 'marketing-data-456789',
    dataset: 'marketing_raw',
    bucket_name: 'marketing-etl-bucket',
    folder_path: 'raw/postgres',
    is_active: false,
    created_at: new Date('2024-01-15T14:30:00Z'),
    updated_at: new Date('2024-03-01T14:25:17Z')
  },
  {
    id: 'f9c2e8a1-3d5b-47f6-9082-6471c9d3e254',
    name: 'Customer Analytics',
    type: 'bigquery' as DestinationType,
    project_id: 'customer-insights-789012',
    dataset: 'customer_data',
    bucket_name: 'customer-data-lake',
    folder_path: 'customer/source',
    is_active: false,
    created_at: new Date('2024-01-05T11:20:00Z'),
    updated_at: new Date('2024-02-10T08:45:09Z')
  },
  {
    id: '2a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d',
    name: 'Finance Data Warehouse',
    type: 'bigquery' as DestinationType,
    project_id: 'finance-reporting-234567',
    dataset: 'finance_raw',
    bucket_name: 'finance-etl-storage',
    folder_path: 'finance/postgres',
    is_active: true,
    created_at: new Date('2024-02-28T10:15:00Z'),
    updated_at: new Date('2024-03-07T17:38:22Z')
  },
  {
    id: '7d9e1f2g-3h4i-5j6k-7l8m-9n0o1p2q3r4s',
    name: 'Product Analytics',
    type: 'bigquery' as DestinationType,
    project_id: 'product-analytics-345678',
    dataset: 'product_data',
    bucket_name: 'product-metrics-storage',
    folder_path: 'metrics/raw',
    is_active: true,
    created_at: new Date('2023-12-10T09:30:00Z'),
    updated_at: new Date('2024-01-15T11:05:41Z')
  },
  {
    id: '5s4r3q2p-1o0n-9m8l-7k6j-5i4h3g2f1e0d',
    name: 'Development Environment',
    type: 'bigquery' as DestinationType,
    project_id: 'dev-environment-901234',
    dataset: 'dev_data',
    bucket_name: 'dev-testing-bucket',
    folder_path: 'development/test',
    is_active: true,
    created_at: new Date('2024-03-01T08:00:00Z'),
    updated_at: new Date('2024-03-08T16:20:15Z')
  }
]