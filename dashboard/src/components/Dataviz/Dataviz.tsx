import React from 'react'
import LinePlotWidget from '../Widget/LinePlotWidget'
import LocationWidget from '../Widget/LocationWidget'
import {
  Index,
} from '../../consts'

import './Dataviz.css'
import Session from '../../model/Session'

type DatavizProps = {
  session: Session
}

export default (props: DatavizProps) => (
  <div className='Dataviz'>
    <LocationWidget
      name='Location'
      locality={props.session.getCurrentLocality()}
    />

    <LinePlotWidget 
      name='RSSI'
      data={props.session.getTimePlottable(Index.RSSI)}
      defaultMin={-100}
      defaultMax={0}
      units='rssi'
    />

    <LinePlotWidget 
      name='Altitude'
      data={props.session.getTimePlottable(Index.ALTITUDE)}
      defaultMin={0}
      defaultMax={100}
      units='m'
    />

    <LinePlotWidget 
      name='Velocity'
      data={props.session.getTimePlottable(Index.VELOCITY)}
      defaultMin={-10}
      defaultMax={10}
      units='m/s'
    />

    <LinePlotWidget 
      name='Distance'
      data={props.session.getTimePlottable(Index.DISTANCE)}
      defaultMin={0}
      defaultMax={100}
      units='m'
    />

    <LinePlotWidget 
      name='Temperature'
      data={props.session.getTimePlottable(Index.TEMPERATURE)}
      defaultMin={0}
      defaultMax={50}
      units='C'
    />

    <LinePlotWidget 
      name='Pressure'
      data={props.session.getTimePlottable(Index.PRESSURE)}
      defaultMin={1000}
      defaultMax={1050}
      units='mBar'
    />
  </div>
)
