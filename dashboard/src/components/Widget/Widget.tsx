import React from 'react'
import './Widget.css'

type WidgetProps = {
  className?: string,
  name: string,
  dimensionsReady?: (el: HTMLDivElement | null) => void,
  lastReading?: string | null,
  children?: React.ReactNode
}

export default ({ children, className, name, dimensionsReady, lastReading }: WidgetProps) => (
  <div className={'Widget Dashboard-Panel' + (className ? ' Widget-' + className : '')}>
    <div className='Widget-Header'>
      <div className='Widget-Header-Title'>{ name }</div>
      <div className='Widget-Header-Reading'>{ lastReading }</div>
    </div>
    <div className='Widget-Inside' ref={el => dimensionsReady && dimensionsReady(el)}>
      { children }
    </div>
  </div>
)
