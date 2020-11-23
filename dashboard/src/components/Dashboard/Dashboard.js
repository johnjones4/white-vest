import React, { Component } from 'react'
import Dataviz from '../Dataviz/Dataviz'
import Toolbar from '../Toolbar/Toolbar'
import Banner from '../Banner/Banner'
import { transformTelemetryArray, testData, testSessions } from '../../dataUtil'

import './Dashboard.css'

const TESTING = false

export default class Dashboard extends Component {
  constructor(props) {
    super(props)
    this.state = {
      activeSession: null,
      sessions: TESTING ? testSessions : [],
      sessionDataMap: {},
      liveData: TESTING ? transformTelemetryArray(testData) : [],
      receivingData: false,
      error: null
    }
    this.receivingDataTimeout = null
  }

  componentDidMount () {
    // this.loadSessions()
    // this.connectToLiveStream()
  }

  connectToLiveStream () {
    try {
      this.ws = new WebSocket(`ws://${window.location.hostname}:5678/`)
      this.ws.onmessage = event => {
        this.setState({
          liveData: this.state.liveData.concat(transformTelemetryArray(JSON.parse(event.data))),
          receivingData: true
        })
        if (this.receivingDataTimeout) {
          clearTimeout(this.receivingDataTimeout)
        }
        this.receivingDataTimeout = setTimeout(() => {
          this.setState({
            receivingData: false
          })
        }, 5000)
      }
    } catch (error) {
      this.setState({ error })
    }
  }

  async loadSessions () {
    try {
      const response = await fetch('/api/session')
      const data = await response.json()
      if (response.status !== 200) {
        throw new Error(data.message)
      }
      this.setState({ sessions: data })
    } catch (error) {
      this.setState({ error })
    }
  }

  async setActiveSession (session) {
    if (session && !this.state.sessionDataMap[session]) {
      try {
        if (TESTING) {
          const mapUpdate = {}
          mapUpdate[session] = transformTelemetryArray(testData)
          this.setState({
            activeSession: session,
            sessionDataMap: Object.assign({}, this.state.sessionDataMap, mapUpdate)
          })
        } else {
          const response = await fetch(`/api/session/${session}`)
          const data = await response.json()
          if (response.status !== 200) {
            throw new Error(data.message)
          }
          const mapUpdate = {}
          mapUpdate[session] = transformTelemetryArray(data)
          this.setState({
            activeSession: session,
            sessionDataMap: Object.assign({}, this.state.sessionDataMap, mapUpdate)
          })
        }
      } catch (error) {
        this.setState({ error })
      }
    } else {
      this.setState({
        activeSession: session
      })
    }
  }

  async startNewSession () {
    try {
      await fetch('/api/session', {
        method: 'POST'
      })
    } catch (error) {
      this.setState({ error })
    }
    await this.loadSessions()
  }

  render () {
    return (
      <div className='Dashboard'>
        <Toolbar 
          sessions={this.state.sessions}
          activeSession={this.state.activeSession}
          setActiveSession={session => this.setActiveSession(session)}
          startNewSession={() => this.startNewSession()}
          receivingData={this.state.activeSession ? null : this.state.receivingData}
        />
        { this.state.activeSession ? 
          (<Dataviz data={this.state.sessionDataMap[this.state.activeSession]} />)
          : (<Dataviz data={this.state.liveData} />)
        }
        <Banner error={this.state.error} />
      </div>
    )
  }
}
