import React, { Component } from 'react'
import Widget from './Widget'
import './AttitudeWidget.css'

type AttitudeWidgetProps = {
  name: string
}

export default class AttitudeWidget extends Component<AttitudeWidgetProps> {
  render () {
    return (
      <Widget name={this.props.name} lastReading=''>
        <div className='AttitudeWidget'>

        </div>
      </Widget>
    )
  }
}
