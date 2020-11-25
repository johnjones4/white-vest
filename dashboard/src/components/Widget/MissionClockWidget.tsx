import React from 'react'
import Widget from './Widget'
import './MissionClockWidget.css'

type MissionClockWidgetProps = {
  seconds: number,
  name: string
}

export default (props: MissionClockWidgetProps) => {
  const minutes = Math.floor(props.seconds / 60)
  const seconds = (props.seconds - minutes * 60)
  let secondsStr = `${seconds.toFixed(1)}`
  if (seconds < 10) {
    secondsStr = `0${seconds.toFixed(1)}`
  }
  return (
    <Widget name={props.name}>
      <div className='MissionClockWidget'>
        <div className='MissionClockWidget-Digits'>
          {minutes}:{secondsStr}
        </div>
      </div>
    </Widget>
  )
}
