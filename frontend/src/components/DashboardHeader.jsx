'use client'

import { RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

export function DashboardHeader() {
  const router = useRouter()
  
  return (
    <div className="flex items-center justify-between">
      <h1 className="text-4xl font-bold">Media Controller</h1>
      <Button onClick={() => router.refresh()}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Refresh All
      </Button>
    </div>
  )
}