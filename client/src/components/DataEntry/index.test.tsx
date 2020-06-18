import React from 'react'
import { waitFor, fireEvent, screen } from '@testing-library/react'
import { renderWithRouter } from '../testUtilities'
import DataEntry from './index'
import { dummyBoards, dummyBallots } from './_mocks'
import * as utilities from '../utilities'
import { contestMocks } from '../MultiJurisdictionAudit/_mocks'

const apiMock: jest.SpyInstance<
  ReturnType<typeof utilities.api>,
  Parameters<typeof utilities.api>
> = jest.spyOn(utilities, 'api').mockImplementation()
const checkAndToastMock: jest.SpyInstance<
  ReturnType<typeof utilities.checkAndToast>,
  Parameters<typeof utilities.checkAndToast>
> = jest.spyOn(utilities, 'checkAndToast').mockReturnValue(false)

const ballotingMock = async (endpoint: string) => {
  switch (endpoint) {
    case '/me':
      return {
        type: 'AUDIT_BOARD',
        ...dummyBoards()[0],
      }
    case '/election/1/jurisdiction/jurisdiction-1/round/round-1/audit-board/audit-board-1/contest':
      return { contests: contestMocks.oneTargeted }
    case '/election/1/jurisdiction/jurisdiction-1/round/round-1/audit-board/audit-board-1/ballots':
      return dummyBallots
    case '/election/1/jurisdiction/jurisdiction-1/round/round-1/audit-board/audit-board-1/ballots/ballot-id-1':
      return { status: 'ok' }
    default:
      return null
  }
}

afterEach(() => {
  apiMock.mockClear()
  checkAndToastMock.mockClear()
})

describe('DataEntry', () => {
  beforeEach(() => {
    apiMock.mockImplementation(ballotingMock)
  })

  describe('member form', () => {
    it.only('renders if no audit board members set', async () => {
      apiMock.mockImplementation(async endpoint => {
        switch (endpoint) {
          case '/me':
            return dummyBoards()[1] // No members set
          default:
            return ballotingMock(endpoint)
        }
      })

      const { container } = renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })
      expect(apiMock).toBeCalledTimes(1)
      screen.getByText('Audit Board #2: Member Sign-in')
      expect(container).toMatchSnapshot()
    })

    it('submits and goes to ballot table', async () => {
      let posted = false
      apiMock.mockImplementation(async endpoint => {
        switch (endpoint) {
          case '/me':
            return posted ? dummyBoards()[0] : dummyBoards()[1]
          case '/election/1/jurisdiction/jurisdiction-1/round/round-1/audit-board/audit-board-1/members':
            posted = true
            return { status: 'ok' }
          default:
            return ballotingMock(endpoint)
        }
      })
      const { container } = renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })

      expect(apiMock).toBeCalledTimes(1)
      const nameInputs = screen.getAllByLabelText('Full Name')
      expect(nameInputs).toHaveLength(2)

      nameInputs.forEach((nameInput, i) =>
        fireEvent.change(nameInput, { target: { value: `Name ${i}` } })
      )
      fireEvent.click(screen.getByText('Next'), { bubbles: true })

      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(1 + 4)
        screen.getByText('Audit Board #1: Ballot Cards to Audit')
        expect(container).toMatchSnapshot()
      })
    })
  })

  describe('ballot interaction', () => {
    it('renders board table with no ballots', async () => {
      apiMock.mockImplementation(async (endpoint: string) => {
        switch (endpoint) {
          case '/election/1/jurisdiction/jurisdiction-1/round/round-1/audit-board/audit-board-1/ballots':
            return { ballots: [] }
          default:
            return ballotingMock(endpoint)
        }
      })
      const { container } = renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })
      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(3)
        expect(container).toMatchSnapshot()
      })
    })

    it('renders board table with ballots', async () => {
      const { container } = renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })
      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(3)
        screen.getByText('Audit Board #1: Ballot Cards to Audit')
        expect(screen.getByText('Start Auditing').closest('a')).toBeEnabled()
        expect(
          screen.getByText('Auditing Complete - Submit Results').closest('a')
        ).toHaveAttribute('disabled') // eslint-disable-line jest-dom/prefer-enabled-disabled
        expect(container).toMatchSnapshot()
      })
    })

    it('renders board table with large container size', async () => {
      jest
        .spyOn(window.document, 'getElementsByClassName')
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .mockReturnValue([{ clientWidth: 2000 }] as any)
      const { container } = renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })
      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(3)
        expect(container).toMatchSnapshot()
      })
    })

    it('renders ballot route', async () => {
      const { container } = renderWithRouter(<DataEntry />, {
        route:
          '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/2112',
      })
      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(3)
        screen.getByText('Enter Ballot Information')
        expect(container).toMatchSnapshot()
      })
    })

    it('advances ballot forward and backward', async () => {
      const { history } = renderWithRouter(<DataEntry />, {
        route:
          '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/2112',
      })
      const pushSpy = jest.spyOn(history, 'push').mockImplementation()

      fireEvent.click(
        screen.getByText('Ballot 2112 not found - move to next ballot'),
        {
          bubbles: true,
        }
      )
      await waitFor(() => {
        expect(pushSpy).toBeCalledTimes(1)
      })

      fireEvent.click(screen.getByText('Back'), { bubbles: true })
      await waitFor(() => {
        expect(pushSpy).toBeCalledTimes(2)
      })

      expect(pushSpy.mock.calls[0][0]).toBe(
        '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/1789'
      )
      expect(pushSpy.mock.calls[1][0]).toBe(
        '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/313'
      )
    })

    it('submits ballot', async () => {
      const { history } = renderWithRouter(<DataEntry />, {
        route:
          '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/2112',
      })

      fireEvent.click(screen.getByTestId('choice-id-1'), { bubbles: true })
      await waitFor(() =>
        fireEvent.click(screen.getByTestId('enabled-review'), { bubbles: true })
      )
      await waitFor(() => {
        fireEvent.click(screen.getByText('Submit & Next Ballot'), {
          bubbles: true,
        })
      })

      await waitFor(() => {
        expect(apiMock).toBeCalledTimes(5)
        expect(history.location.pathname).toBe(
          '/election/1/audit-board/audit-board-1/batch/batch-id-1/ballot/1789'
        )
      })
    })

    it('audits ballots', async () => {
      renderWithRouter(<DataEntry />, {
        route: '/election/1/audit-board/audit-board-1',
      })
    })
  })
})
