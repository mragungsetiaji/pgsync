import { PlusIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useSourcesContext } from '../context/sources-context'

export function SourcesPrimaryButtons() {
  const { setIsAddDialogOpen } = useSourcesContext()
  
  return (
    <div className='flex gap-2'>
      <Button 
        className='space-x-2' 
        onClick={() => setIsAddDialogOpen(true)}
      >
        <span>Add Source</span>
        <PlusIcon size={16} />
      </Button>
    </div>
  )
}