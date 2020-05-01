import React, { useState, useLayoutEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import styled from 'styled-components'
import { Table, Column, IColumnProps, Cell } from '@blueprintjs/table'
import H2Title from '../../Atoms/H2Title'
import useJurisdictions from '../useJurisdictions'
import { IJurisdiction } from '../../../types'

const PaddedCell = styled(Cell)`
  padding: 5px 5px 4px 5px;
`

enum SortOrder {
  ASCENDING,
  DESCENDING,
}

const sort = <T,>(
  xs: Array<T>,
  compare: (x1: T, x2: T) => number,
  order: SortOrder
): Array<T> => {
  const sorted = [...xs].sort(compare)
  if (order === SortOrder.DESCENDING) {
    sorted.reverse()
  }
  return sorted
}

const compareStrings = (str1: string, str2: string) => {
  if (str1 < str2) return -1
  else if (str1 > str2) return 1
  else return 0
}

const compareRanks = <T,>(x1: T, x2: T, rank: (x: T) => number) =>
  rank(x1) - rank(x2)

interface ISortableColumnProps extends IColumnProps {
  onSortToggle: () => void
  sortOrder: SortOrder | null
  compare: (x1: any, x2: any) => number
}

const SortableColumn: React.FC<ISortableColumnProps> = props => {
  return <Column {...props} />
}

const Progress: React.FC = () => {
  const { electionId } = useParams()
  const jurisdictions = useJurisdictions(electionId!)
  const [sorting, setSorting] = useState<{
    column: string
    order: SortOrder
  } | null>(null)

  const toggleSorting = (column: string) => {
    if (!sorting || sorting.column !== column) {
      return setSorting({ column, order: SortOrder.ASCENDING })
    }
    switch (sorting.order) {
      case null:
        return setSorting({ column, order: SortOrder.ASCENDING })
      case SortOrder.ASCENDING:
        return setSorting({ column, order: SortOrder.DESCENDING })
      case SortOrder.DESCENDING:
        return setSorting(null)
    }
  }

  const columns = [
    <SortableColumn
      key="name"
      name="Jurisdiction Name"
      cellRenderer={(r: number) => (
        <PaddedCell>{sortedJurisdictions[r].name}</PaddedCell>
      )}
      sortOrder={sorting && sorting.column === 'name' ? sorting.order : null}
      onSortToggle={() => toggleSorting('name')}
      compare={(j1: IJurisdiction, j2: IJurisdiction) =>
        compareStrings(j1.name, j2.name)
      }
    />,
    <SortableColumn
      key="status"
      name="Status"
      cellRenderer={(r: number) => {
        const { processing } = sortedJurisdictions[r].ballotManifest!
        switch (processing && processing.status) {
          case 'ERRORED':
            return <PaddedCell>Ballot manifest upload failed</PaddedCell>
          case 'PROCESSED':
            return <PaddedCell>Ballot manifest received</PaddedCell>
          default:
            return <PaddedCell>No ballot manifest uploaded</PaddedCell>
        }
      }}
      sortOrder={sorting && sorting.column === 'status' ? sorting.order : null}
      onSortToggle={() => toggleSorting('status')}
      compare={(j1: IJurisdiction, j2: IJurisdiction) =>
        compareRanks(j1, j2, j => {
          const { processing } = j.ballotManifest!
          switch (processing && processing.status) {
            case 'ERRORED':
              return 1
            case 'PROCESSED':
              return 2
            default:
              return 0
          }
        })
      }
    />,
    <Column
      key="audited"
      name="Total Audited"
      cellRenderer={(r: number) => <PaddedCell />}
    />,
    <Column
      key="remaining"
      name="Remaining in Round"
      cellRenderer={(r: number) => <PaddedCell />}
    />,
  ]

  const sortedJurisdictions = sorting
    ? sort(
        jurisdictions,
        columns.find(c => c.key === sorting.column)!.props.compare,
        sorting.order
      )
    : jurisdictions

  const containerRef = useRef<HTMLDivElement>(null)
  const [tableWidth, setTableWidth] = useState<number | undefined>()
  useLayoutEffect(() => {
    if (containerRef.current) {
      setTableWidth(containerRef.current.clientWidth)
    }
  }, [containerRef.current])
  const columnWidths = tableWidth
    ? Array<number>(columns.length).fill(tableWidth / columns.length)
    : undefined

  return (
    <div>
      <H2Title>Audit Progress by Jurisdiction</H2Title>
      <p>
        Click on a column name to sort by that column&apos;s data. To reverse
        sort, click on the column name again.
      </p>

      <div ref={containerRef}>
        <Table
          numRows={jurisdictions.length}
          defaultRowHeight={30}
          columnWidths={columnWidths}
          enableRowHeader={false}
        >
          {columns}
        </Table>
      </div>
    </div>
  )
}

export default Progress
