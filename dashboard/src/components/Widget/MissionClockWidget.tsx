import React from 'react'
import Widget from './Widget'
import './MissionClockWidget.css'

type MissionClockWidgetProps = {
  seconds: number | null,
  cameraIsRunning: boolean,
  name: string
}

const MissionClockWidget = (props: MissionClockWidgetProps) => {
  if (!props.seconds) {
    return null
  }
  const minutes = Math.floor(props.seconds / 60)
  const seconds = (props.seconds - minutes * 60)
  let secondsStr = `${seconds.toFixed(1)}`
  if (seconds < 10) {
    secondsStr = `0${seconds.toFixed(1)}`
  }
  return (
    <Widget name={`${props.name} (${props.cameraIsRunning ? 'Recording' : 'Not Recording'})`}>
      <div className='MissionClockWidget'>
        <div className='MissionClockWidget-Digits'>
          {minutes}:{secondsStr}
        </div>
      </div>
    </Widget>
  )
}

export default MissionClockWidget
