import { IconMailPlus, IconUserPlus } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { useDestinations } from '../context/destinations-context'

export function DestinationsPrimaryButtons() {
  const { setOpen } = useDestinations()
  return (
    <div className='flex gap-2'>
      <Button className='space-x-1' onClick={() => setOpen('add')}>
        <span>Add Destination</span> <IconUserPlus size={18} />
      </Button>
    </div>
  )
}
