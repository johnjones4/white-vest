import React from 'react'
import './Widget.css'

export default ({ children, className, name, dimensionsReady, lastReading }) => (
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
