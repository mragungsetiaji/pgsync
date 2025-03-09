import React, { useState } from 'react'
import useDialogState from '@/hooks/use-dialog-state'
import { Source } from '../data/schema'

type SourcesDialogType = 'invite' | 'add' | 'edit' | 'delete'

interface SourcesContextType {
  open: SourcesDialogType | null
  setOpen: (str: SourcesDialogType | null) => void
  currentRow: Source | null
  setCurrentRow: React.Dispatch<React.SetStateAction<Source | null>>
}

const SourcesContext = React.createContext<SourcesContextType | null>(null)

interface Props {
  children: React.ReactNode
}

export default function SourcesProvider({ children }: Props) {
  const [open, setOpen] = useDialogState<SourcesDialogType>(null)
  const [currentRow, setCurrentRow] = useState<Source | null>(null)

  return (
    <SourcesContext value={{ open, setOpen, currentRow, setCurrentRow }}>
      {children}
    </SourcesContext>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useSources = () => {
  const sourcesContext = React.useContext(SourcesContext)

  if (!sourcesContext) {
    throw new Error('useSources has to be used within <SourcesContext>')
  }

  return sourcesContext
}
