import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import { api } from '../utilities'
import { IJurisdiction } from '../../types'

const useJurisdictions = (electionId: string) => {
  const [jurisdictions, setJurisdictions] = useState<IJurisdiction[]>([])
  useEffect(() => {
    ;(async () => {
      try {
        const response: { jurisdictions: IJurisdiction[] } = await api(
          `/election/${electionId}/jurisdiction`
        )
        setJurisdictions(response.jurisdictions)
      } catch (err) {
        toast.error(err.message)
      }
    })()
  }, [electionId])
  return jurisdictions
}

export default useJurisdictions
