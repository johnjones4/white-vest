import React, { Component } from 'react'
import AttitudeWidget from '../Widget/AttitudeWidget'
import MissionClockWidget from '../Widget/MissionClockWidget'
import LinePlotWidget from '../Widget/LinePlotWidget'
import LocationWidget from '../Widget/LocationWidget'
import Toolbar from '../Toolbar/Toolbar'
import Banner from '../Banner/Banner'
import './Dashboard.css'
import Session, { SessionDelegate, Locality, Attitude, TimePlottable, ReceivingState } from '../../model/Session'
import {Index} from '../../consts'
import * as Tone from 'tone'

type DashboardProps = {
}

type DashboardState = {
  receivingState: ReceivingState,
  error: Error | null,
  locality: Locality | null,
  attitude: Attitude | null,
  rssi: TimePlottable | null,
  altitude: TimePlottable | null,
  velocity: TimePlottable | null,
  distance: TimePlottable | null,
  temperature: TimePlottable | null,
  pressure: TimePlottable | null,
  seconds: number | null,
  wsAddress: string
  cameraIsRunning: boolean
}

export default class Dashboard extends Component<DashboardProps, DashboardState> implements SessionDelegate {
  session: Session
  synth: Tone.Synth

  constructor(props: DashboardProps) {
    super(props)
    this.synth = new Tone.Synth().toDestination()
    this.state = {
      receivingState: ReceivingState.NotReceiving,
      error: null,
      locality: null,
      attitude: null,
      rssi: null,
      altitude: null,
      velocity: null,
      distance: null,
      temperature: null,
      pressure: null,
      seconds: null,
      wsAddress: 'ground.local:5678',
      cameraIsRunning: false
    }
    this.session = new Session(this)
  }

  componentDidMount () {
    this.session.start(this.state.wsAddress)
  }

  componentDidUpdate (prevProps: DashboardProps, prevState: DashboardState) {
    if (this.state.wsAddress !== prevState.wsAddress) {
      this.session.start(this.state.wsAddress)
    }
  }

  onNewLiveData () {
    this.setState({
      locality: this.session.getCurrentLocality(),
      attitude: this.session.getCurrentAttitude(),
      rssi: this.session.getTimePlottable(Index.RSSI),
      altitude: this.session.getTimePlottable(Index.ALTITUDE),
      velocity: this.session.getTimePlottable(Index.VELOCITY),
      distance: this.session.getTimePlottable(Index.DISTANCE),
      temperature: this.session.getTimePlottable(Index.TEMPERATURE),
      pressure: this.session.getTimePlottable(Index.PRESSURE),
      seconds: this.session.getCurrentSeconds(),
      cameraIsRunning: this.session.isCameraRecording()
    })
  }
  
  onReceivingDataChange ()  {
    let note : String | null = null
    switch (this.session.receivingState) {
      case ReceivingState.NotReceiving:
        note = 'C2'
        break
      case ReceivingState.NoSignal:
        note = 'C4'
        break
      case ReceivingState.Receiving:
        note = 'C6'
        break
    }
    if (note) {
      this.synth.triggerAttackRelease(note as string, '8n')
    }
    this.setState({
      receivingState: this.session.receivingState
    })
  }

  onError (error: Error)  {
    this.setState({
      error
    })
  }

  render () {
    return (
      <div className='Dashboard'>
        <Toolbar 
          receivingState={this.state.receivingState}
          wsAddress={this.state.wsAddress}
          wsAddressUpdated={(wsAddress: string) => this.setState({wsAddress: wsAddress})}
        />
        <div className='Dataviz'>
          <LocationWidget
            name='Location'
            locality={this.state.locality}
          />

          <LinePlotWidget 
            name='RSSI'
            data={this.state.rssi}
            defaultMin={-100}
            defaultMax={0}
            units='rssi'
          />

          <LinePlotWidget 
            name='Altitude'
            data={this.state.altitude}
            defaultMin={0}
            defaultMax={100}
            units='m'
          />

          <LinePlotWidget 
            name='Velocity'
            data={this.state.velocity}
            defaultMin={-10}
            defaultMax={10}
            units='m/s'
          />

          <LinePlotWidget 
            name='Distance'
            data={this.state.distance}
            defaultMin={0}
            defaultMax={100}
            units='m'
          />

          <LinePlotWidget 
            name='Temperature'
            data={this.state.temperature}
            defaultMin={0}
            defaultMax={50}
            units='C'
          />

          <LinePlotWidget 
            name='Pressure'
            data={this.state.pressure}
            defaultMin={1000}
            defaultMax={1050}
            units='mBar'
          />

          <AttitudeWidget
            name='Attitude'
            data={this.state.attitude}
          />

          <MissionClockWidget
            name='Mission Clock'
            cameraIsRunning={this.state.cameraIsRunning}
            seconds={this.state.seconds}
          />
        </div>
        <Banner error={this.state.error} />
      </div>
    )
  }
}
