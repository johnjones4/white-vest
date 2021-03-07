import React, { Component } from 'react'
import Widget from './Widget'
import './AttitudeWidget.css'
import { Attitude } from '../../model/Session'

type AttitudeWidgetProps = {
  name: string
  data: Attitude | null
}

export default class AttitudeWidget extends Component<AttitudeWidgetProps> {
  

  render () {
    if (this.props.data === null) {
      return null
    }
    const rotation = {
      transform: [
        `rotateX(${this.props.data.pitch}deg)`,
        `rotateY(${this.props.data.roll}deg)`,
        `rotateZ(${this.props.data.yaw}deg)`,
      ].join(' ')
    }
    return (
      <Widget name={this.props.name} lastReading=''>
        <div className='AttitudeWidget'>
          <div className='AttitudeWidget-Readings'>
            <p>
              <strong>Roll:</strong> {this.props.data.roll && this.props.data.roll.toFixed(1)}&deg;
            </p>
            <p>
              <strong>Pitch:</strong> {this.props.data.pitch && this.props.data.pitch.toFixed(1)}&deg;
            </p>
            <p>
              <strong>Yaw:</strong> {this.props.data.yaw && this.props.data.yaw.toFixed(1)}&deg;
            </p>
          </div>
          <div className='AttitudeWidget-Scene' style={rotation}>
            <div className='shape pyramid-1 pyr-1'>
              <div className='face-wrapper ft'>
                <div className='face'>
                  <div className='photon-shader'></div>
                </div>
              </div>
              <div className='face-wrapper bk'>
                <div className='face'>
                  <div className='photon-shader'></div>
                </div>
              </div>
              <div className='face-wrapper lt'>
                <div className='face'>
                  <div className='photon-shader'></div>
                </div>
              </div>
              <div className='face-wrapper rt'>
                <div className='face'>
                  <div className='photon-shader'></div>
                </div>
              </div>
              <div className='face bm'>
                <div className='photon-shader'></div>
              </div>
            </div>
          </div>
        </div>
      </Widget>
    )
  }
}
