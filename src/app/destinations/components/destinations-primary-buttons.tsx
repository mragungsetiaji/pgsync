import { PlusIcon } from 'lucide-react' // Using Lucide icons for consistency
import { Button } from '@/components/ui/button'
import { useDestinationsContext } from '../context/destinations-context'

export function DestinationsPrimaryButtons() {
  const { setIsAddDialogOpen } = useDestinationsContext()
  
  return (
    <div className='flex gap-2'>
      <Button 
        className='space-x-2' 
        onClick={() => setIsAddDialogOpen(true)}
      >
        <span>Add Destination</span>
        <PlusIcon size={16} />
      </Button>
    </div>
  )
}