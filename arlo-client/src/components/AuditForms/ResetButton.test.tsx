import React from 'react'
import { render, fireEvent, wait } from '@testing-library/react'
import { toast } from 'react-toastify'
import ResetButton from './ResetButton'
import { api, checkAndToast } from '../utilities'

const apiMock = api as jest.Mock<ReturnType<typeof api>, Parameters<typeof api>>
const checkAndToastMock = checkAndToast as jest.Mock<
  ReturnType<typeof checkAndToast>,
  Parameters<typeof checkAndToast>
>

jest.mock('../utilities')
apiMock.mockImplementationOnce(async () => '{}')
checkAndToastMock.mockImplementation(() => false)
const toastSpy = jest.spyOn(toast, 'error').mockImplementation()

afterEach(() => {
  apiMock.mockClear()
  toastSpy.mockClear()
  checkAndToastMock.mockClear()
})

describe('ResetButton', () => {
  it('renders', () => {
    const updateAuditMock = jest.fn()
    const { container } = render(
      <ResetButton electionId="1" updateAudit={updateAuditMock} />
    )
    expect(container).toMatchSnapshot()
  })

  it('renders disabled', () => {
    const updateAuditMock = jest.fn()
    const { container } = render(
      <ResetButton electionId="1" updateAudit={updateAuditMock} />
    )
    expect(container).toMatchSnapshot()
  })

  it('posts to /audit/reset and calls updateAudit', async () => {
    const updateAuditMock = jest.fn()
    const wrapper = document.createElement('div')
    wrapper.setAttribute('id', 'reset-button-wrapper')

    const { getByText } = render(
      <ResetButton electionId="1" updateAudit={updateAuditMock} />,
      { container: document.body.appendChild(wrapper) }
    )

    fireEvent.click(getByText('Clear & Restart'), { bubbles: true })

    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(checkAndToastMock).toBeCalledTimes(1)
      expect(updateAuditMock).toBeCalledTimes(1)
    })
  })

  it('handles server errors', async () => {
    checkAndToastMock.mockImplementationOnce(() => true)
    const updateAuditMock = jest.fn()
    const wrapper = document.createElement('div')
    wrapper.setAttribute('id', 'reset-button-wrapper')

    const { getByText } = render(
      <ResetButton electionId="1" updateAudit={updateAuditMock} />,
      { container: document.body.appendChild(wrapper) }
    )

    fireEvent.click(getByText('Clear & Restart'), { bubbles: true })

    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(checkAndToastMock).toBeCalledTimes(1)
      expect(updateAuditMock).toBeCalledTimes(0)
      expect(toastSpy).toBeCalledTimes(0)
    })
  })

  it('handles 404 errors', async () => {
    checkAndToastMock.mockImplementationOnce(() => true)
    apiMock.mockImplementationOnce(async () => {
      throw new Error('404')
    })
    const updateAuditMock = jest.fn()
    const wrapper = document.createElement('div')
    wrapper.setAttribute('id', 'reset-button-wrapper')

    const { getByText } = render(
      <ResetButton electionId="1" updateAudit={updateAuditMock} />,
      { container: document.body.appendChild(wrapper) }
    )

    fireEvent.click(getByText('Clear & Restart'), { bubbles: true })

    await wait(() => {
      expect(apiMock).toBeCalledTimes(1)
      expect(checkAndToastMock).toBeCalledTimes(0)
      expect(updateAuditMock).toBeCalledTimes(0)
      expect(toastSpy).toBeCalledTimes(1)
    })
  })
})
