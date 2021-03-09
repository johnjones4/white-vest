import React, { ReactElement } from 'react'
import './Widget.css'

interface WidgetProps {
  className?: string
  name: string
  dimensionsReady?: (el: HTMLDivElement | null) => void
  lastReading?: string | null
  children?: React.ReactNode
}

const Widget = ({ children, className, name, dimensionsReady, lastReading }: WidgetProps): ReactElement | null => (
  <div className={'Widget Dashboard-Panel' + (className !== undefined ? ' Widget-' + className : '')}>
    <div className='Widget-Header'>
      <div className='Widget-Header-Title'>{name}</div>
      <div className='Widget-Header-Reading'>{lastReading}</div>
    </div>
    <div className='Widget-Inside' ref={el => dimensionsReady?.(el)}>
      {children}
    </div>
  </div>
)

export default Widget
