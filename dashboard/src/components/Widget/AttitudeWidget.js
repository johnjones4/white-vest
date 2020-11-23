import React, { Component } from 'react'
import Widget from './Widget'
import './AttitudeWidget.css'

export default class AttitudeWidget extends Component {
  render () {
    return (
      <Widget name={this.props.name} lastReading=''>
        <div className='AttitudeWidget'>

        </div>
      </Widget>
    )
  }
}
