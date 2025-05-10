'use client'

import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { PasswordInput } from '@/components/password-input'
import { SelectDropdown } from '@/components/select-dropdown'
import { connectorTypeSchema, Source } from '../data/schema'

// Form validation schema
const formSchema = z.object({
  name: z.string().min(1, { message: 'Source name is required.' }),
  connector: connectorTypeSchema,
  host: z.string().min(1, { message: 'Host is required.' }),
  port: z.coerce.number()
    .int()
    .min(1, { message: 'Port must be a positive number.' })
    .max(65535, { message: 'Port must be less than or equal to 65535.' }),
  database: z.string().min(1, { message: 'Database name is required.' }),
  user: z.string().min(1, { message: 'Username is required.' }),
  password: z.string().min(1, { message: 'Password is required.' }),
  isEdit: z.boolean()
})

type SourceForm = z.infer<typeof formSchema>

interface Props {
  currentSource?: Source
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: (data: SourceForm) => void
}

export function SourcesActionDialog({ 
  currentSource,
  open, 
  onOpenChange,
  onSubmitSuccess 
}: Props) {
  const isEdit = !!currentSource
  const form = useForm<SourceForm>({
    resolver: zodResolver(formSchema),
    defaultValues: isEdit
      ? {
          name: currentSource.name,
          connector: currentSource.connector,
          host: currentSource.host || '',
          port: currentSource.port || 5432,
          database: currentSource.database || '',
          user: currentSource.user || '',
          password: '', // For security, don't fill in the password
          isEdit: true,
        }
      : {
          name: '',
          connector: 'postgres',
          host: '',
          port: 5432,
          database: '',
          user: '',
          password: '',
          isEdit: false,
        },
  })

  const onSubmit = async (values: SourceForm) => {
    try {
      // Prepare payload for API (remove isEdit field which is just for form logic)
      const payload = {
        name: values.name,
        connector: values.connector,
        host: values.host,
        port: values.port,
        database: values.database,
        user: values.user,
        password: values.password,
      }

      // Determine whether to create or update
      const url = isEdit ? `/api/sources/${currentSource?.id}` : '/api/sources'
      const method = isEdit ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save data source')
      }

      const result = await response.json()

      // Reset form and close dialog
      form.reset()
      onOpenChange(false)
      
      // Notify success
      toast({
        title: isEdit ? 'Data source updated' : 'Data source created',
        description: `${values.name} has been ${isEdit ? 'updated' : 'created'} successfully.`,
      })
      
      // Callback if provided
      if (onSubmitSuccess) {
        onSubmitSuccess(values)
      }
    } catch (error) {
      console.error('Error saving data source:', error)
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to save data source',
        variant: 'destructive',
      })
    }
  }

  const testConnection = async () => {
    try {
      setTestingConnection(true)
      setConnectionStatus(null)
      
      // Get current form values
      const values = form.getValues()
      
      // Convert credentials to base64
      const credentials_json_base64 = btoa(values.credentials)
      
      const response = await fetch('/api/destinations/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: values.project_id,
          dataset: values.dataset,
          credentials_json_base64: credentials_json_base64,
          bucket_name: values.bucket_name,
          folder_path: values.folder_path || null,
          hmac_key: values.hmac_key || null,
          hmac_secret: values.hmac_secret || null,
        }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Connection test failed')
      }
      
      toast({
        title: 'Connection successful',
        description: 'Successfully connected to the database.',
      })
    } catch (error) {
      console.error('Connection test error:', error)
      toast({
        title: 'Connection failed',
        description: error instanceof Error ? error.message : 'Failed to connect to the database',
        variant: 'destructive',
      })
    }
  }

  const connectorOptions = [
    { label: 'PostgreSQL', value: 'postgres' },
  ]

  return (
    <Dialog
      open={open}
      onOpenChange={(state) => {
        form.reset()
        onOpenChange(state)
      }}
    >
      <DialogContent className='sm:max-w-lg'>
        <DialogHeader className='text-left'>
          <DialogTitle>{isEdit ? 'Edit Data Source' : 'Add New Data Source'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update the data source connection details. ' : 'Create a new data source connection. '}
            Click save when you&apos;re done.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className='h-[26.25rem] w-full pr-4 -mr-4 py-1'>
          <Form {...form}>
            <form
              id='source-form'
              onSubmit={form.handleSubmit(onSubmit)}
              className='space-y-4 p-0.5'
            >
              <FormField
                control={form.control}
                name='name'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Source Name
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder='Production Database'
                        className='col-span-4'
                        autoComplete='off'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='connector'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Connector Type
                    </FormLabel>
                    <SelectDropdown
                      defaultValue={field.value}
                      onValueChange={field.onChange}
                      placeholder='Select connector type'
                      className='col-span-4'
                      items={connectorOptions}
                    />
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='host'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Host
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder='localhost or 127.0.0.1'
                        className='col-span-4'
                        autoComplete='off'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='port'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Port
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder='5432'
                        className='col-span-4'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='database'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Database Name
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder='postgres'
                        className='col-span-4'
                        autoComplete='off'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='user'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Username
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder='postgres'
                        className='col-span-4'
                        autoComplete='off'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name='password'
                render={({ field }) => (
                  <FormItem className='grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0'>
                    <FormLabel className='col-span-2 text-right'>
                      Password
                    </FormLabel>
                    <FormControl>
                      <PasswordInput
                        placeholder={isEdit ? 'Enter to change password' : 'Enter password'}
                        className='col-span-4'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className='col-span-4 col-start-3' />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </ScrollArea>
        <DialogFooter>
          <Button 
            type="button" 
            variant="outline" 
            onClick={testConnection}
          >
            Test Connection
          </Button>
          <Button type='submit' form='source-form'>
            {isEdit ? 'Update Source' : 'Create Source'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}