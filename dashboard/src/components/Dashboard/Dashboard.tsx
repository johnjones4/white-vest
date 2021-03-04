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
  liveSession: Session | null,
  receivingData: boolean,
  error: Error | null,
  sessionsList: number[]
}

export default class Dashboard extends Component<DashboardProps, DashboardState> implements SessionStoreDelegate {
  sessionStore: SessionStore

  constructor(props: DashboardProps) {
    super(props)
    this.state = {
      liveSession: null,
      receivingData: false,
      error: null,
      sessionsList: []
    }
    this.sessionStore = new SessionStore(this, true)
  }

  componentDidMount () {
    this.sessionStore.start()
  }

  onNewLiveData () {
    this.setState({
      liveSession: this.sessionStore.liveData
    })
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

  async downloadSession (session: number | null) {
    const sessionObj = session == null ? this.state.liveSession : await this.sessionStore.getSession(session as number)

    if (!sessionObj) {
      return
    }
    
    const a = document.createElement("a")
    document.body.appendChild(a)
    a.style.display = 'none'
    a.href = 'data:text/csv;charset=utf-8,' + encodeURI(sessionObj.getCSV())
    a.download = `${sessionObj.timestamp || 'live'}.csv`
    a.click()
    document.body.removeChild(a)
  }

  render () {
    return (
      <div className='Dashboard'>
        <Toolbar 
          sessions={this.state.sessionsList}
          receivingData={this.state.receivingData}
          downloadSession={session => this.downloadSession(session)}
        />
        { this.state.liveSession && (<Dataviz session={this.state.liveSession} />)}
        <Banner error={this.state.error} />
      </div>
    )
  }
}
