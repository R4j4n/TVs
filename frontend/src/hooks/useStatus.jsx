import { useState, useEffect } from 'react'
import { fetchPiStatus } from '@/lib/api'

export function useStatus(host) {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const refreshStatus = async () => {
    try {
      const data = await fetchPiStatus(host)
      setStatus(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch status')
    }
  }

  useEffect(() => {
    refreshStatus()
    const interval = setInterval(refreshStatus, 30000)
    return () => clearInterval(interval)
  }, [host])

  return { status, error, refreshStatus }
}