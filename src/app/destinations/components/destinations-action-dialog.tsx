'use client'

import { z } from 'zod'
import { useState } from 'react'
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
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { SelectDropdown } from '@/components/select-dropdown'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import { destinationTypes } from '../data/data'
import { Destination, destinationCreateSchema } from '../data/schema'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

type DestinationForm = z.infer<typeof destinationCreateSchema> & { isEdit: boolean }

interface Props {
  currentRow?: Destination
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: (data: any) => void
  dialogHeight?: string
}

export function DestinationsActionDialog({ 
  currentRow, 
  open, 
  onOpenChange,
  onSubmitSuccess,
  dialogHeight = "95vh"  
}: Props) {
  const isEdit = !!currentRow
  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<{
    success: boolean; 
    message: string;
  } | null>(null)

  const form = useForm<DestinationForm>({
    resolver: zodResolver(destinationCreateSchema.extend({ isEdit: z.boolean() })),
    defaultValues: isEdit
      ? {
          name: currentRow.name,
          type: 'bigquery', // Currently only supporting BigQuery
          project_id: currentRow.project_id || '',
          dataset: currentRow.dataset || '',
          credentials: '', // For security, don't fill in credentials
          bucket_name: currentRow.bucket_name || '',
          folder_path: currentRow.folder_path || '',
          hmac_key: '',  // For security, don't fill in HMAC key
          hmac_secret: '', // For security, don't fill in HMAC secret
          isEdit,
        }
      : {
          name: '',
          type: 'bigquery',
          project_id: '',
          dataset: '',
          credentials: '',
          bucket_name: '',
          folder_path: '',
          hmac_key: '',
          hmac_secret: '',
          isEdit,
        },
  })

  const onSubmit = async (values: DestinationForm) => {
    try {
      const endpoint = isEdit 
        ? `/api/destinations/${currentRow?.id}` 
        : '/api/destinations'

      const method = isEdit ? 'PUT' : 'POST'
      
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: values.name,
          type: values.type,
          project_id: values.project_id,
          dataset: values.dataset,
          credentials: values.credentials,
          bucket_name: values.bucket_name,
          folder_path: values.folder_path,
          hmac_key: values.hmac_key,
          hmac_secret: values.hmac_secret,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save destination')
      }

      const data = await response.json()
      
      toast({
        title: isEdit ? 'Destination updated' : 'Destination created',
        description: `${values.name} has been ${isEdit ? 'updated' : 'created'} successfully`,
      })
      
      form.reset()
      onOpenChange(false)
      
      if (onSubmitSuccess) {
        onSubmitSuccess(data)
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'An error occurred while saving the destination',
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
      
      const requiredFields = ['project_id', 'dataset', 'credentials', 'bucket_name']
      const missingFields = requiredFields.filter(field => !values[field as keyof typeof values])
      
      if (missingFields.length > 0) {
        throw new Error(`Please fill in all required fields: ${missingFields.join(', ')}`)
      }
      
      const response = await fetch('/api/destinations/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: values.project_id,
          dataset: values.dataset,
          credentials: values.credentials,
          bucket_name: values.bucket_name,
          folder_path: values.folder_path,
          hmac_key: values.hmac_key,
          hmac_secret: values.hmac_secret,
        }),
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'Connection test failed')
      }
      
      setConnectionStatus({
        success: data.status === 'success',
        message: data.message,
      })
    } catch (error: any) {
      setConnectionStatus({
        success: false,
        message: error.message || 'Connection test failed',
      })
    } finally {
      setTestingConnection(false)
    }
  }

  // Calculate the content height based on dialog height
  const contentHeight = "calc(100% - 70px)" // Height minus header and footer space

  return (
    <Dialog
      open={open}
      onOpenChange={(state) => {
        if (!state) {
          form.reset()
          setConnectionStatus(null)
        }
        onOpenChange(state)
      }}
    >
      <DialogContent className="sm:max-w-2xl" style={{ maxHeight: dialogHeight, height: dialogHeight }}>
        <DialogHeader className="text-left">
          <DialogTitle>{isEdit ? 'Edit Destination' : 'Add New Destination'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update destination settings here. ' : 'Configure your BigQuery destination. '}
            Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="h-[460px] w-full pr-4 -mr-4 py-1" style={{ height: contentHeight }}>
          <Form {...form}>
            <form
              id="destination-form"
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4 p-0.5"
            >
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Name *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="My BigQuery Destination"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="type"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Type *
                    </FormLabel>
                    <SelectDropdown
                      defaultValue={field.value}
                      onValueChange={field.onChange}
                      placeholder="Select a destination type"
                      disabled={true} // Currently only supporting BigQuery
                      className="col-span-4"
                      items={destinationTypes.map(({ label, value }) => ({
                        label,
                        value,
                      }))}
                    />
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="project_id"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Project ID *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="my-gcp-project-id"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="dataset"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Dataset *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="my_dataset"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="credentials"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-start gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right pt-2">
                      Service Account *
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Paste your JSON service account credentials here"
                        className="col-span-4 min-h-[150px]"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="bucket_name"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      GCS Bucket Name *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="my-storage-bucket"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="folder_path"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      GCS Folder Path
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="staging/data"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                    <p className="text-sm text-muted-foreground col-span-4 col-start-3">
                      Optional: Folder path within the bucket to store temporary files
                    </p>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="hmac_key"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      HMAC Access Key
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="GOOG1EXAMPLE..."
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                    <p className="text-sm text-muted-foreground col-span-4 col-start-3">
                      Optional: Used for authenticated GCS access
                    </p>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="hmac_secret"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      HMAC Secret
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="••••••••"
                        className="col-span-4"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                    <p className="text-sm text-muted-foreground col-span-4 col-start-3">
                      Optional: Used with HMAC Access Key for authentication
                    </p>
                  </FormItem>
                )}
              />
              
              {connectionStatus && (
                <div className="col-span-4 col-start-3 mt-2">
                  <Alert variant={connectionStatus.success ? "default" : "destructive"}>
                    <div className="flex items-start gap-2">
                      {connectionStatus.success ? (
                        <CheckCircle2 className="h-4 w-4 mt-0.5" />
                      ) : (
                        <AlertCircle className="h-4 w-4 mt-0.5" />
                      )}
                      <div>
                        <AlertTitle>
                          {connectionStatus.success ? "Connection successful" : "Connection failed"}
                        </AlertTitle>
                        <AlertDescription>
                          {connectionStatus.message}
                        </AlertDescription>
                      </div>
                    </div>
                  </Alert>
                </div>
              )}
              
            </form>
          </Form>
        </ScrollArea>
        
        <DialogFooter className="flex items-center gap-2">
          <Button 
            type="button" 
            variant="outline" 
            onClick={testConnection}
            disabled={testingConnection}
          >
            {testingConnection ? "Testing..." : "Test connection"}
          </Button>
          <Button type="submit" form="destination-form">
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}