import { PlusIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useConnectionsContext } from '../context/connections-context'

export function ConnectionsPrimaryButtons() {
  const { setIsAddDialogOpen } = useConnectionsContext()
  
  return (
    <div className='flex gap-2'>
      <Button 
        className='space-x-2' 
        onClick={() => setIsAddDialogOpen(true)}
      >
        <span>Add Connection</span>
        <PlusIcon size={16} />
      </Button>
    </div>
  )
}