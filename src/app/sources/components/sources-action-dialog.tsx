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
import { ScrollArea } from '@/components/ui/scroll-area'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import { Source, sourceCreateSchema } from '../data/schema'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

type SourceForm = z.infer<typeof sourceCreateSchema> & { isEdit: boolean }

interface Props {
  currentRow?: Source
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: (data: any) => void
  dialogHeight?: string
}

export function SourcesActionDialog({ 
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

  const form = useForm<SourceForm>({
    resolver: zodResolver(sourceCreateSchema.extend({ isEdit: z.boolean() })),
    defaultValues: isEdit
      ? {
          name: currentRow.name,
          host: currentRow.host || '',
          port: currentRow.port || 5432,
          database: currentRow.database || '',
          user: currentRow.user || '',
          password: '', // For security, don't fill in password
          isEdit,
        }
      : {
          name: '',
          host: '',
          port: 5432,
          database: '',
          user: '',
          password: '',
          isEdit,
        },
  })

  const onSubmit = async (values: SourceForm) => {
    try {
      const endpoint = isEdit 
        ? `/api/sources/${currentRow?.id}` 
        : '/api/sources'
      
      const payload = {
        name: values.name,
        host: values.host,
        port: values.port,
        database: values.database,
        user: values.user,
        password: values.password,
        is_active: true // Default to active
      }
  
      const response = await fetch(endpoint, {
        method: isEdit ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save source')
      }

      const data = await response.json()
      
      toast({
        title: isEdit ? 'Source updated' : 'Source created',
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
        description: error.message || 'An error occurred while saving the source',
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
      
      const requiredFields = ['host', 'port', 'database', 'user', 'password']
      const missingFields = requiredFields.filter(field => !values[field as keyof typeof values])
      
      if (missingFields.length > 0) {
        throw new Error(`Please fill in all required fields: ${missingFields.join(', ')}`)
      }
      
      const response = await fetch('/api/sources/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          host: values.host,
          port: values.port,
          database: values.database,
          user: values.user,
          password: values.password,
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
          <DialogTitle>{isEdit ? 'Edit Source' : 'Add New Source'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update source settings here. ' : 'Configure your PostgreSQL source. '}
            Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="h-[460px] w-full pr-4 -mr-4 py-1" style={{ height: contentHeight }}>
          <Form {...form}>
            <form
              id="source-form"
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
                        placeholder="My PostgreSQL Source"
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
                name="host"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Host *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="localhost"
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
                name="port"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Port *
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="5432"
                        className="col-span-4"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="database"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Database *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="postgres"
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
                name="user"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Username *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="postgres"
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
                name="password"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Password *
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
          <Button type="submit" form="source-form">
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}