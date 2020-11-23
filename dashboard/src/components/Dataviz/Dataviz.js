import React from 'react'
import LinePlotWidget from '../Widget/LinePlotWidget'
import LocationWidget from '../Widget/LocationWidget'
import {
  INDEX,
  plottableData,
  recentData
} from '../../dataUtil'

import './Dataviz.css'

export default ({ data }) => (
  <div className='Dataviz'>
    <LocationWidget
      name='Location'
      data={recentData(data, [INDEX.ROCKET_LAT, INDEX.ROCKET_LON, INDEX.BASE_LAT, INDEX.BASE_LON, INDEX.DISTANCE, INDEX.BEARING])}
    />

    <LinePlotWidget 
      name='RSSI'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.RSSI])}
      defaultMin={-100}
      defaultMax={0}
      units='rssi'
    />

    <LinePlotWidget 
      name='Altitude'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.ALTITUDE])}
      defaultMin={0}
      defaultMax={100}
      units='m'
    />

    <LinePlotWidget 
      name='Velocity'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.VELOCITY])}
      defaultMin={-10}
      defaultMax={10}
      units='m/s'
    />

    <LinePlotWidget 
      name='Distance'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.DISTANCE])}
      defaultMin={0}
      defaultMax={100}
      units='m'
    />

    <LinePlotWidget 
      name='Temperature'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.TEMPERATURE])}
      defaultMin={0}
      defaultMax={50}
      units='C'
    />

    <LinePlotWidget 
      name='Pressure'
      data={plottableData(data, [INDEX.TIMESTAMP, INDEX.PRESSURE])}
      defaultMin={1000}
      defaultMax={1050}
      units='mBar'
    />
  </div>
)
