import React, { useState } from 'react'
import useDialogState from '@/hooks/use-dialog-state'
import { Destination } from '../data/schema'

type DestinationsDialogType = 'add' | 'edit' | 'delete'

interface DestinationsContextType {
  open: DestinationsDialogType | null
  setOpen: (str: DestinationsDialogType | null) => void
  currentRow: Destination | null
  setCurrentRow: React.Dispatch<React.SetStateAction<Destination | null>>
}

const DestinationsContext = React.createContext<DestinationsContextType | null>(null)

interface Props {
  children: React.ReactNode
}

export default function DestinationsProvider({ children }: Props) {
  const [open, setOpen] = useDialogState<DestinationsDialogType>(null)
  const [currentRow, setCurrentRow] = useState<Destination | null>(null)

  return (
    <DestinationsContext value={{ open, setOpen, currentRow, setCurrentRow }}>
      {children}
    </DestinationsContext>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useDestinations = () => {
  const destinationsContext = React.useContext(DestinationsContext)

  if (!destinationsContext) {
    throw new Error('useDestinations has to be used within <DestinationsContext>')
  }

  return destinationsContext
}
