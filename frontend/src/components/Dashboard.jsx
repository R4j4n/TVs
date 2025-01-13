import { Suspense } from 'react'
import { PiGrid } from './PiGrid'
import { DashboardHeader } from './DashboardHeader'

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <DashboardHeader />
        <Suspense fallback={<div>Loading...</div>}>
          <PiGrid />
        </Suspense>
      </div>
    </div>
  )
}