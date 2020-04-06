/* eslint-disable react/prop-types */
import React from 'react'
import { ElementType, IAudit } from '../../../types'
import Participants from './Participants'
import Contests from './Contests'
import Settings from './Settings'
import Review from './Review'
import { ISidebarMenuItem } from '../../Atoms/Sidebar'

export const setupStages = [
  'Participants',
  'Target Contests',
  'Opportunistic Contests',
  'Audit Settings',
  'Review & Launch',
] as const

interface IProps {
  stage: ElementType<typeof setupStages>
  audit: IAudit
  menuItems: ISidebarMenuItem[]
}

const Setup: React.FC<IProps> = ({ stage, audit, menuItems }) => {
  const activeStage = menuItems.find(m => m.title === stage)
  const nextStage: ISidebarMenuItem | undefined =
    menuItems[menuItems.indexOf(activeStage!) + 1]
  const prevStage: ISidebarMenuItem | undefined =
    menuItems[menuItems.indexOf(activeStage!) - 1]
  switch (stage) {
    case 'Participants':
      // prevStage === undefined, so don't send it
      return (
        <Participants
          nextStage={nextStage!}
          locked={activeStage!.state === 'locked'}
        />
      )
    case 'Target Contests':
      return (
        <Contests
          isTargeted
          key="targeted"
          audit={audit}
          nextStage={nextStage!}
          prevStage={prevStage!}
          locked={activeStage!.state === 'locked'}
        />
      )
    case 'Opportunistic Contests':
      return (
        <Contests
          isTargeted={false}
          key="opportunistic"
          audit={audit}
          nextStage={nextStage!}
          prevStage={prevStage!}
          locked={activeStage!.state === 'locked'}
        />
      )
    case 'Audit Settings':
      return (
        <Settings
          nextStage={nextStage!}
          prevStage={prevStage!}
          locked={activeStage!.state === 'locked'}
        />
      )
    case 'Review & Launch':
      // nextStage === undefined, so don't send it
      return (
        <Review
          prevStage={prevStage!}
          locked={activeStage!.state === 'locked'}
        />
      )
    /* istanbul ignore next */
    default:
      return null
  }
}

export default Setup
