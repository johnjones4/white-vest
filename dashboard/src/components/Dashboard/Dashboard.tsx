import React, { Component } from 'react'
import Dataviz from '../Dataviz/Dataviz'
import Toolbar from '../Toolbar/Toolbar'
import Banner from '../Banner/Banner'
import './Dashboard.css'
import SessionStore, { SessionStoreDelegate } from '../../model/SessionStore'
import Session from '../../model/Session'

type DashboardProps = {
}

type DashboardState = {
  activeSession: Session | null,
  receivingData: boolean,
  error: Error | null
  sessionsList: number[]
}

export default class Dashboard extends Component<DashboardProps, DashboardState> implements SessionStoreDelegate {
  sessionStore: SessionStore

  constructor(props: DashboardProps) {
    super(props)
    this.state = {
      activeSession: null,
      receivingData: false,
      error: null,
      sessionsList: []
    }
    this.sessionStore = new SessionStore(this, false)
  }

  componentDidMount () {
    this.sessionStore.start()
  }

  onNewLiveData () {
    if (this.state.activeSession === null || this.state.activeSession.timestamp === null) {
      this.setState({
        activeSession: this.sessionStore.liveData
      })
    }
  }
  
  onReceivingDataChange ()  {
    this.setState({
      receivingData: this.sessionStore.receivingData
    })
  }

  onError (error: Error)  {
    this.setState({
      error
    })
  }

  onSessionsListAvailable ()  {
    this.setState({
      sessionsList: this.sessionStore.sessionsList
    })
  }

  async setActiveSession (session: number | null) {
    if (session !== null) {
      const activeSession = await this.sessionStore.getSession(session)
      if (activeSession) {
        this.setState({
          activeSession
        })
      }
    } else {
      this.setState({
        activeSession: this.sessionStore.liveData
      })
    }
  }

  render () {
    return (
      <div className='Dashboard'>
        <Toolbar 
          sessions={this.state.sessionsList}
          activeSession={this.state.activeSession ? this.state.activeSession.timestamp : null}
          setActiveSession={session => this.setActiveSession(session)}
          startNewSession={() => this.sessionStore.startNewSession()}
          receivingData={this.state.activeSession && this.state.activeSession.timestamp !== null ? null : this.state.receivingData}
        />
        { this.state.activeSession && (<Dataviz session={this.state.activeSession} />)}
        <Banner error={this.state.error} />
      </div>
    )
  }
}
