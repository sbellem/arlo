import React, { useState, useLayoutEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import styled from 'styled-components'
import { Table, Column, Cell } from '@blueprintjs/table'
import H2Title from '../../Atoms/H2Title'
import useJurisdictions, { JurisdictionRoundStatus } from '../useJurisdictions'

const PaddedCell = styled(Cell)`
  padding: 5px 5px 4px 5px;
`

const useElementWidth = (): [
  React.RefObject<HTMLDivElement>,
  number | undefined
] => {
  const ref = useRef<HTMLDivElement>(null)
  const [elementWidth, setElementWidth] = useState<number | undefined>()
  useLayoutEffect(() => {
    if (ref.current) {
      setElementWidth(ref.current.clientWidth)
    }
  }, [])
  return [ref, elementWidth]
}

const Progress: React.FC = () => {
  const { electionId } = useParams<{ electionId: string }>()
  const jurisdictions = useJurisdictions(electionId)
  const [tableContainerRef, tableContainerWidth] = useElementWidth()

  const columns = [
    <Column
      key="name"
      name="Jurisdiction Name"
      cellRenderer={(row: number) => (
        <PaddedCell>{jurisdictions[row].name}</PaddedCell>
      )}
    />,
    <Column
      key="status"
      name="Status"
      cellRenderer={(row: number) => {
        const { ballotManifest, currentRoundStatus } = jurisdictions[row]
        if (!currentRoundStatus) {
          const { processing } = ballotManifest
          switch (processing && processing.status) {
            case 'ERRORED':
              return <PaddedCell>Manifest upload failed</PaddedCell>
            case 'PROCESSED':
              return <PaddedCell>Manifest received</PaddedCell>
            default:
              return <PaddedCell>No manifest uploaded</PaddedCell>
          }
        } else {
          const prettyStatus = {
            [JurisdictionRoundStatus.NOT_STARTED]: 'Not started',
            [JurisdictionRoundStatus.IN_PROGRESS]: 'In progress',
            [JurisdictionRoundStatus.COMPLETE]: 'Complete',
          }
          return (
            <PaddedCell>{prettyStatus[currentRoundStatus.status]}</PaddedCell>
          )
        }
      }}
    />,
    <Column
      key="audited"
      name="Total Audited"
      cellRenderer={(row: number) => {
        const { currentRoundStatus } = jurisdictions[row]
        return (
          <PaddedCell>
            {currentRoundStatus && currentRoundStatus.numBallotsAudited}
          </PaddedCell>
        )
      }}
    />,
    <Column
      key="remaining"
      name="Remaining in Round"
      cellRenderer={(row: number) => {
        const { currentRoundStatus } = jurisdictions[row]
        return (
          <PaddedCell>
            {currentRoundStatus &&
              currentRoundStatus.numBallotsSampled -
                currentRoundStatus.numBallotsAudited}
          </PaddedCell>
        )
      }}
    />,
  ]

  const columnWidths = tableContainerWidth
    ? Array(columns.length).fill(tableContainerWidth / columns.length)
    : undefined

  return (
    <div>
      <H2Title>Audit Progress by Jurisdiction</H2Title>
      <div ref={tableContainerRef}>
        <Table
          numRows={jurisdictions.length}
          defaultRowHeight={30}
          columnWidths={columnWidths}
          enableRowHeader={false}
          enableColumnResizing={false}
        >
          {columns}
        </Table>
      </div>
    </div>
  )
}

export default Progress
