'use client'

import { z } from 'zod'
import { useState, useEffect } from 'react'
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
import { Checkbox } from '@/components/ui/checkbox'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Connection, connectionCreateSchema } from '../data/schema'
import { Source } from '../../sources/data/schema'
import { Destination } from '../../destinations/data/schema'

type ConnectionForm = z.infer<typeof connectionCreateSchema> & { isEdit: boolean }

interface Props {
  currentRow?: Connection
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: (data: any) => void
}

export function ConnectionsActionDialog({ 
  currentRow, 
  open, 
  onOpenChange,
  onSubmitSuccess,
}: Props) {
  const isEdit = !!currentRow
  const [sources, setSources] = useState<Source[]>([])
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [loadingSources, setLoadingSources] = useState(false)
  const [loadingDestinations, setLoadingDestinations] = useState(false)
  const [isManual, setIsManual] = useState(true)

  // Fetch sources and destinations
  useEffect(() => {
    async function fetchSources() {
      setLoadingSources(true)
      try {
        const response = await fetch('/api/sources')
        if (!response.ok) throw new Error('Failed to fetch sources')
        const data = await response.json()
        setSources(data)
      } catch (error) {
        console.error('Error fetching sources:', error)
        toast({
          title: 'Error',
          description: 'Failed to fetch sources',
          variant: 'destructive',
        })
      } finally {
        setLoadingSources(false)
      }
    }

    async function fetchDestinations() {
      setLoadingDestinations(true)
      try {
        const response = await fetch('/api/destinations')
        if (!response.ok) throw new Error('Failed to fetch destinations')
        const data = await response.json()
        setDestinations(data)
      } catch (error) {
        console.error('Error fetching destinations:', error)
        toast({
          title: 'Error',
          description: 'Failed to fetch destinations',
          variant: 'destructive',
        })
      } finally {
        setLoadingDestinations(false)
      }
    }

    fetchSources()
    fetchDestinations()
  }, [])

  // Update isManual state based on schedule_type
  useEffect(() => {
    if (currentRow) {
      setIsManual(currentRow.schedule_type === 'manual')
    }
  }, [currentRow])

  const form = useForm<ConnectionForm>({
    resolver: zodResolver(connectionCreateSchema.extend({ isEdit: z.boolean() })),
    defaultValues: isEdit
      ? {
          name: currentRow.name,
          source_db_id: Number(currentRow.source_id),
          destination_id: Number(currentRow.destination_id),
          schedule_type: currentRow.schedule_type,
          cron_expression: currentRow.cron_expression || null,
          timezone: currentRow.timezone || 'UTC',
          is_active: currentRow.is_active,
          connection_state: currentRow.connection_state,
          isEdit,
        }
      : {
          name: '',
          source_db_id: 0,
          destination_id: 0,
          schedule_type: 'manual',
          cron_expression: null,
          timezone: 'UTC',
          is_active: true,
          connection_state: null,
          isEdit,
        },
  })

  // Watch for schedule_type changes
  const scheduleType = form.watch('schedule_type')
  useEffect(() => {
    setIsManual(scheduleType === 'manual')
  }, [scheduleType])

  const onSubmit = async (values: ConnectionForm) => {
    try {
      const endpoint = isEdit 
        ? `/api/connections/${currentRow?.id}` 
        : '/api/connections'
      
      const payload = {
        name: values.name,
        source_db_id: values.source_db_id,
        destination_id: values.destination_id,
        schedule_type: values.schedule_type,
        cron_expression: values.schedule_type === 'cron' ? values.cron_expression : null,
        timezone: values.timezone,
        is_active: values.is_active,
        connection_state: values.connection_state,
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
        throw new Error(errorData.detail || JSON.stringify(errorData) || 'Failed to save connection')
      }

      const data = await response.json()
      
      toast({
        title: isEdit ? 'Connection updated' : 'Connection created',
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
        description: error.message || 'An error occurred while saving the connection',
        variant: 'destructive',
      })
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(state) => {
        if (!state) {
          form.reset()
        }
        onOpenChange(state)
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="text-left">
          <DialogTitle>{isEdit ? 'Edit Connection' : 'Add New Connection'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update connection settings. ' : 'Create a new connection between a source and destination. '}
            Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="h-[460px] w-full pr-4 -mr-4 py-1">
          <Form {...form}>
            <form
              id="connection-form"
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
                        placeholder="Connection Name"
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
                name="source_db_id"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Source *
                    </FormLabel>
                    <Select
                      value={field.value ? String(field.value) : undefined}
                      onValueChange={(value) => field.onChange(Number(value))}
                      disabled={loadingSources}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a source" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {sources.map((source) => (
                          <SelectItem key={source.id} value={String(source.id)}>
                            {source.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="destination_id"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Destination *
                    </FormLabel>
                    <Select
                      value={field.value ? String(field.value) : undefined}
                      onValueChange={(value) => field.onChange(Number(value))}
                      disabled={loadingDestinations}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a destination" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {destinations.map((dest) => (
                          <SelectItem key={dest.id} value={String(dest.id)}>
                            {dest.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="schedule_type"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Schedule Type
                    </FormLabel>
                    <Select
                      value={field.value}
                      onValueChange={(value: 'manual' | 'cron') => field.onChange(value)}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select schedule type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="manual">Manual</SelectItem>
                        <SelectItem value="cron">Cron</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
              {!isManual && (
                <>
                  <FormField
                    control={form.control}
                    name="cron_expression"
                    render={({ field }) => (
                      <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                        <FormLabel className="col-span-2 text-right">
                          Cron Expression *
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="*/5 * * * *"
                            className="col-span-4"
                            {...field}
                            value={field.value || ''}
                          />
                        </FormControl>
                        <FormMessage className="col-span-4 col-start-3" />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="timezone"
                    render={({ field }) => (
                      <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                        <FormLabel className="col-span-2 text-right">
                          Timezone
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="UTC"
                            className="col-span-4"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage className="col-span-4 col-start-3" />
                      </FormItem>
                    )}
                  />
                </>
              )}
              
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="grid grid-cols-6 items-center gap-x-4 gap-y-1 space-y-0">
                    <FormLabel className="col-span-2 text-right">
                      Active
                    </FormLabel>
                    <FormControl>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                        <span className="text-sm font-medium">
                          Enable this connection
                        </span>
                      </div>
                    </FormControl>
                    <FormMessage className="col-span-4 col-start-3" />
                  </FormItem>
                )}
              />
              
            </form>
          </Form>
        </ScrollArea>
        
        <DialogFooter>
          <Button type="submit" form="connection-form">
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}