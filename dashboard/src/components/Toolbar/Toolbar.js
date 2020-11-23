import React, { Component } from 'react'
import './Toolbar.css'

export default class Toolbar extends Component {
  constructor(props) {
    super(props)
    this.state = {
      sessionSelectOpen: false
    }
  }

  toggleSessionSelectOpen () {
    this.setState({
      sessionSelectOpen: !this.state.sessionSelectOpen
    })
  }

  setActiveSession(session) {
    this.setState({
      sessionSelectOpen: false
    })
    this.props.setActiveSession(session)
  }

  render () {
    const { sessions, activeSession, startNewSession, receivingData } = this.props
    return (
      <div className='Toolbar'>
        <div className='Toolbar-Session-Select'>
          <button className={'Toolbar-Session-Select-Button ' + (activeSession === null ? 'Toolbar-Session-Select-Button-Live-Session' : '')} onClick={() => this.toggleSessionSelectOpen()}>Session: {activeSession === null ? 'Live' : new Date(activeSession * 1000).toLocaleString()}</button>
          { this.state.sessionSelectOpen && (<div className='Toolbar-Session-Select-Dropdown'>
            <button className='Toolbar-Session-Select-Dropdown-Button' onClick={() => this.setActiveSession(null)}>
              Live
            </button>
            { sessions.map(session => (<button className='Toolbar-Session-Select-Dropdown-Button' key={session} onClick={() => this.setActiveSession(session)}>{new Date(session * 1000).toLocaleString()}</button>)) }
          </div>)}
        </div>
        { activeSession === null && (<button className='Toolbar-Start-New-Session' onClick={() => startNewSession()}>Save and Start New Session</button>) }
        <div className={['Toolbar-Stream-Status', receivingData !== null ? (receivingData ? 'Toolbar-Stream-Status-Receiving' : 'Toolbar-Stream-Status-Not-Receiving') : ''].join(' ')}>
          { receivingData !== null ? (receivingData ? 'Receiving Data' : 'Not Receiving Data') : 'Data Not Live' }
        </div>
      </div>
    )
  }
}
