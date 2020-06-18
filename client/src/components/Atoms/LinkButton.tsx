import React from 'react'
import { Link, LinkProps } from 'react-router-dom'
import { Button } from '@blueprintjs/core'

interface ILinkButtonProps extends LinkProps {
  disabled?: boolean
}

const LinkButton = (props: ILinkButtonProps) => {
  return (
    <Link
      {...props}
      component={({ navigate, ...rest }) => (
        <Button onClick={navigate} {...rest} />
      )}
    />
  )
}

export default LinkButton
