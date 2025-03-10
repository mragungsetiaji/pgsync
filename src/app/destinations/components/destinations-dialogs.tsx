import { useDestinations } from '../context/destinations-context'
import { DestinationsActionDialog } from './destinations-action-dialog'
import { DestinationsDeleteDialog } from './destinations-delete-dialog'

export function DestinationsDialogs() {
  const { open, setOpen, currentRow, setCurrentRow } = useDestinations()
  return (
    <>
      <DestinationsActionDialog
        key='user-add'
        open={open === 'add'}
        onOpenChange={() => setOpen('add')}
      />

      {currentRow && (
        <>
          <DestinationsActionDialog
            key={`user-edit-${currentRow.id}`}
            open={open === 'edit'}
            onOpenChange={() => {
              setOpen('edit')
              setTimeout(() => {
                setCurrentRow(null)
              }, 500)
            }}
            currentRow={currentRow}
          />

          <DestinationsDeleteDialog
            key={`user-delete-${currentRow.id}`}
            open={open === 'delete'}
            onOpenChange={() => {
              setOpen('delete')
              setTimeout(() => {
                setCurrentRow(null)
              }, 500)
            }}
            currentRow={currentRow}
          />
        </>
      )}
    </>
  )
}
