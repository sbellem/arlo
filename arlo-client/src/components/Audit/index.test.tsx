import React from 'react'
import { waitForElement, wait, fireEvent } from '@testing-library/react'
import {
  BrowserRouter as Router,
  useRouteMatch,
  useParams,
} from 'react-router-dom'
import Audit from './index'
import { statusStates, dummyBallots, auditSettings } from './_mocks'
import * as utilities from '../utilities'
import { asyncActRender } from '../testUtilities'
import AuthDataProvider from '../UserContext'
import getJurisdictionFileStatus from './useSetupMenuItems/getJurisdictionFileStatus'
import getRoundStatus from './useSetupMenuItems/getRoundStatus'
import { contestMocks } from './Setup/Contests/_mocks'
import { IAudit, IUserMeta, IRound, IAuditSettings, IBallot } from '../../types'
import { IJurisdictions } from './Setup/useParticipantsApi'
import { IContests } from './Setup/Contests/types'

const getJurisdictionFileStatusMock = getJurisdictionFileStatus as jest.Mock
const getRoundStatusMock = getRoundStatus as jest.Mock

const apiMock: jest.SpyInstance<
  ReturnType<typeof utilities.api>,
  Parameters<typeof utilities.api>
> = jest.spyOn(utilities, 'api').mockImplementation()

const generateApiMock = ({
  statusReturn,
  authReturn,
  roundReturn,
  jurisdictionReturn,
  settingsReturn,
  ballotsReturn,
  contestsReturn,
}: {
  statusReturn?: IAudit | Error | { status: 'ok' }
  authReturn?: IUserMeta | Error
  roundReturn?: { rounds: IRound[] } | Error
  jurisdictionReturn?:
    | { jurisdictions: IJurisdictions }
    | Error
    | { status: 'ok' }
  settingsReturn?: IAuditSettings | Error
  ballotsReturn?: { ballots: IBallot[] } | Error
  contestsReturn?: IContests | Error
}) => async (
  endpoint: string
): Promise<
  | IAudit
  | IUserMeta
  | { rounds: IRound[] }
  | { jurisdictions: IJurisdictions }
  | IAuditSettings
  | { ballots: IBallot[] }
  | IContests
  | Error
  | { status: 'ok' }
> => {
  if (endpoint === '/election/1/audit/status' && statusReturn)
    return statusReturn
  if (endpoint === '/auth/me' && authReturn) return authReturn
  if (endpoint === '/election/1/round' && roundReturn) return roundReturn
  if (endpoint === '/election/1/jurisdiction' && jurisdictionReturn)
    return jurisdictionReturn
  if (endpoint === '/election/1/settings' && settingsReturn)
    return settingsReturn
  if (
    endpoint.match(
      /\/election\/[^/]+\/jurisdiction\/[^/]+\/round\/[^/]+\/ballot-list/
    ) &&
    ballotsReturn
  )
    return ballotsReturn
  if (endpoint === '/election/1/contest' && contestsReturn)
    return contestsReturn
  return new Error(`missing mock for ${endpoint}`)
}

const checkAndToastMock: jest.SpyInstance<
  ReturnType<typeof utilities.checkAndToast>,
  Parameters<typeof utilities.checkAndToast>
> = jest.spyOn(utilities, 'checkAndToast').mockReturnValue(false)

checkAndToastMock.mockReturnValue(false)

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), // use actual for all non-hook parts
  useRouteMatch: jest.fn(),
  useParams: jest.fn(),
}))
const paramsMock = useParams as jest.Mock
paramsMock.mockReturnValue({
  electionId: '1',
  view: 'setup',
})
const routeMock = useRouteMatch as jest.Mock
routeMock.mockReturnValue({
  url: '/election/1/setup',
  params: {
    electionId: '1',
    view: 'setup',
  },
})

jest.mock('./useSetupMenuItems/getJurisdictionFileStatus')
jest.mock('./useSetupMenuItems/getRoundStatus')
getJurisdictionFileStatusMock.mockReturnValue('PROCESSED')
getRoundStatusMock.mockReturnValue(false)

afterEach(() => {
  apiMock.mockClear()
  checkAndToastMock.mockClear()
  routeMock.mockReturnValue({
    url: '/election/1/setup',
    params: {
      electionId: '1',
      view: 'setup',
    },
  })
  paramsMock.mockReturnValue({
    electionId: '1',
    view: 'setup',
  })
})

describe('RiskLimitingAuditForm', () => {
  it('fetches initial state from api', async () => {
    apiMock.mockImplementation(
      generateApiMock({ statusReturn: statusStates.empty })
    )
    const { container } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    )

    expect(container).toMatchSnapshot()
    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(apiMock.mock.calls[0][0]).toMatch(
        /\/election\/[^/]+\/audit\/status/
      )
      expect(apiMock.mock.results[0].value).resolves.toBe(statusStates.empty)
    })
  })

  it('renders correctly with initialData', async () => {
    const { container } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    )
    expect(container).toMatchSnapshot()
  })

  it('still renders if there is a server error', async () => {
    checkAndToastMock.mockReturnValueOnce(true)
    await asyncActRender(
      <Router>
        <Audit />
      </Router>
    )
    expect(checkAndToastMock).toBeCalledTimes(1)
  })

  it('does not render SelectBallotsToAudit when /audit/status is processing samplesizes', async () => {
    apiMock.mockImplementation(
      generateApiMock({ statusReturn: statusStates.contestFirstRound })
    )
    const { container, queryByTestId } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    )

    expect(queryByTestId('form-two')).toBeNull()
    expect(container).toMatchSnapshot()
    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(apiMock.mock.calls[0][0]).toMatch(
        /\/election\/[^/]+\/audit\/status/
      )
      expect(apiMock.mock.results[0].value).resolves.toBe(
        statusStates.contestFirstRound
      )
    })
  })

  it('renders SelectBallotsToAudit when /audit/status returns contest data', async () => {
    apiMock.mockImplementation(
      generateApiMock({ statusReturn: statusStates.sampleSizeOptions })
    )
    const { container, getByTestId } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    )

    const fillFormTwo = await waitForElement(() => getByTestId('form-two'), {
      container,
    })

    expect(fillFormTwo).toBeTruthy()
    expect(container).toMatchSnapshot()
    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(apiMock.mock.calls[0][0]).toMatch(
        /\/election\/[^/]+\/audit\/status/
      )
      expect(apiMock.mock.results[0].value).resolves.toBe(
        statusStates.sampleSizeOptions
      )
    })
  })

  it('does not render CalculateRiskMeasurement when audit.jurisdictions has length but audit.rounds does not', async () => {
    apiMock.mockImplementation(
      generateApiMock({ statusReturn: statusStates.jurisdictionsInitial })
    )
    const { container, getByTestId, queryByTestId } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    ) // this one will not have the first empty round

    const fillFormTwo = await waitForElement(() => getByTestId('form-two'), {
      container,
    })

    expect(fillFormTwo).toBeTruthy()
    expect(queryByTestId('form-three-1')).toBeNull()
    expect(container).toMatchSnapshot()
    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(apiMock.mock.calls[0][0]).toMatch(
        /\/election\/[^/]+\/audit\/status/
      )
      expect(apiMock.mock.results[0].value).resolves.toBe(
        statusStates.jurisdictionsInitial
      )
    })
  })

  it('renders CalculateRiskMeasurement when /audit/status returns round data', async () => {
    apiMock
      .mockImplementationOnce(
        generateApiMock({ statusReturn: statusStates.ballotManifestProcessed })
      )
      .mockImplementationOnce(generateApiMock({ ballotsReturn: dummyBallots }))
    const { container, getByTestId } = await asyncActRender(
      <Router>
        <Audit />
      </Router>
    ) // this one will not have the first empty round

    const formThree = await waitForElement(() => getByTestId('form-three-1'), {
      container,
    })

    expect(formThree).toBeTruthy()
    expect(container).toMatchSnapshot()
    await wait(() => {
      expect(apiMock).toBeCalledTimes(2)
      expect(apiMock.mock.calls[0][0]).toMatch(
        /\/election\/[^/]+\/audit\/status/
      )
      expect(apiMock.mock.results[0].value).resolves.toBe(
        statusStates.ballotManifestProcessed
      )
    })
  })
})

describe('AA setup flow', () => {
  it('renders sidebar when authenticated on /setup', async () => {
    apiMock.mockImplementation(
      generateApiMock({
        statusReturn: statusStates.sampleSizeOptions,
        authReturn: {
          type: 'audit_admin',
          name: 'Joe',
          email: 'test@email.org',
          jurisdictions: [],
          organizations: [
            {
              id: 'org-id',
              name: 'State',
              elections: [],
            },
          ],
        },
        settingsReturn: auditSettings.all,
        roundReturn: { rounds: [] },
        jurisdictionReturn: { jurisdictions: [] },
        contestsReturn: contestMocks.filledTargeted,
      })
    )
    const { container, queryAllByText } = await asyncActRender(
      <AuthDataProvider>
        <Router>
          <Audit />
        </Router>
      </AuthDataProvider>
    )

    await wait(() => {
      expect(apiMock).toBeCalledTimes(5)
      expect(apiMock).toHaveBeenNthCalledWith(1, '/election/1/audit/status')
      expect(apiMock).toHaveBeenNthCalledWith(2, '/auth/me')
      expect(apiMock).toHaveBeenNthCalledWith(3, '/election/1/round')
      expect(apiMock).toHaveBeenNthCalledWith(4, '/election/1/settings')
      expect(apiMock).toHaveBeenNthCalledWith(5, '/election/1/jurisdiction')
      expect(queryAllByText('Participants').length).toBe(2)
      expect(container).toMatchSnapshot()
    })
  })

  it('renders sidebar when authenticated on /progress', async () => {
    routeMock.mockReturnValue({
      url: '/election/1/setup',
      params: {
        electionId: '1',
        view: 'progress',
      },
    })
    apiMock.mockImplementation(
      generateApiMock({
        statusReturn: statusStates.sampleSizeOptions,
        authReturn: {
          type: 'audit_admin',
          name: 'Joe',
          email: 'test@email.org',
          jurisdictions: [],
          organizations: [
            {
              id: 'org-id',
              name: 'State',
              elections: [],
            },
          ],
        },
        settingsReturn: auditSettings.all,
        roundReturn: { rounds: [] },
        jurisdictionReturn: { jurisdictions: [] },
        contestsReturn: contestMocks.filledTargeted,
      })
    )
    const { container, queryAllByText } = await asyncActRender(
      <AuthDataProvider>
        <Router>
          <Audit />
        </Router>
      </AuthDataProvider>
    )

    await wait(() => {
      expect(apiMock).toBeCalledTimes(5)
      expect(apiMock).toHaveBeenNthCalledWith(1, '/election/1/audit/status')
      expect(apiMock).toHaveBeenNthCalledWith(2, '/auth/me')
      expect(apiMock).toHaveBeenNthCalledWith(3, '/election/1/round')
      expect(apiMock).toHaveBeenNthCalledWith(4, '/election/1/settings')
      expect(apiMock).toHaveBeenNthCalledWith(5, '/election/1/jurisdiction')
      expect(queryAllByText('Participants').length).toBe(2)
      expect(container).toMatchSnapshot()
    })
  })

  it('sidebar changes stages', async () => {
    apiMock.mockImplementation(
      generateApiMock({
        statusReturn: statusStates.sampleSizeOptions,
        authReturn: {
          type: 'audit_admin',
          name: 'Joe',
          email: 'test@email.org',
          jurisdictions: [],
          organizations: [
            {
              id: 'org-id',
              name: 'State',
              elections: [],
            },
          ],
        },
        settingsReturn: auditSettings.all,
        roundReturn: { rounds: [] },
        jurisdictionReturn: { jurisdictions: [] },
        contestsReturn: contestMocks.filledTargeted,
      })
    )
    const { queryAllByText, getByText } = await asyncActRender(
      <AuthDataProvider>
        <Router>
          <Audit />
        </Router>
      </AuthDataProvider>
    )

    await wait(() => {
      expect(apiMock).toBeCalledTimes(5)
      expect(apiMock).toHaveBeenNthCalledWith(1, '/election/1/audit/status')
      expect(apiMock).toHaveBeenNthCalledWith(2, '/auth/me')
      expect(apiMock).toHaveBeenNthCalledWith(3, '/election/1/round')
      expect(apiMock).toHaveBeenNthCalledWith(4, '/election/1/settings')
      expect(apiMock).toHaveBeenNthCalledWith(5, '/election/1/jurisdiction')
      expect(queryAllByText('Participants').length).toBe(2)
    })

    fireEvent.click(getByText('Target Contests'), { bubbles: true })

    await wait(() => {
      expect(queryAllByText('Target Contests').length).toBe(2)
    })
  })

  it('next and back buttons change stages', async () => {
    apiMock.mockImplementation(
      generateApiMock({
        statusReturn: statusStates.sampleSizeOptions,
        authReturn: {
          type: 'audit_admin',
          name: 'Joe',
          email: 'test@email.org',
          jurisdictions: [],
          organizations: [
            {
              id: 'org-id',
              name: 'State',
              elections: [],
            },
          ],
        },
        settingsReturn: auditSettings.all,
        roundReturn: { rounds: [] },
        jurisdictionReturn: { jurisdictions: [] },
        contestsReturn: contestMocks.filledTargeted,
      })
    )
    const { queryAllByText, getByText } = await asyncActRender(
      <AuthDataProvider>
        <Router>
          <Audit />
        </Router>
      </AuthDataProvider>
    )

    await wait(() => {
      expect(apiMock).toBeCalledTimes(5)
      expect(apiMock).toHaveBeenNthCalledWith(1, '/election/1/audit/status')
      expect(apiMock).toHaveBeenNthCalledWith(2, '/auth/me')
      expect(apiMock).toHaveBeenNthCalledWith(3, '/election/1/round')
      expect(apiMock).toHaveBeenNthCalledWith(4, '/election/1/settings')
      expect(apiMock).toHaveBeenNthCalledWith(5, '/election/1/jurisdiction')
      expect(queryAllByText('Participants').length).toBe(2)
    })

    fireEvent.click(getByText('Audit Settings'), { bubbles: true })

    await wait(() => {
      expect(queryAllByText('Audit Settings').length).toBe(2)
    })

    fireEvent.click(getByText('Save & Next'))
    await wait(() => {
      expect(queryAllByText('Review & Launch').length).toBe(2)
    })
    fireEvent.click(getByText('Back'))
    await wait(() => {
      expect(queryAllByText('Audit Settings').length).toBe(2)
    })
  })
})
