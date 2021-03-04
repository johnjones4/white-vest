import React, { Component } from 'react'
import './Toolbar.css'

type ToolbarProps = {
  sessions: number[],
  receivingData: boolean | null,
  downloadSession: (session : number | null) => void
}

type ToolbarState = {
  sessionSelectOpen: boolean
}

export default class Toolbar extends Component<ToolbarProps, ToolbarState> {
  constructor(props: ToolbarProps) {
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

  downloadSession(session: number | null) {
    this.toggleSessionSelectOpen()
    this.props.downloadSession(session)
  }

  render () {
    const { sessions, receivingData } = this.props
    return (
      <div className='Toolbar'>
        <div className={['Toolbar-Stream-Status', receivingData !== null ? (receivingData ? 'Toolbar-Stream-Status-Receiving' : 'Toolbar-Stream-Status-Not-Receiving') : ''].join(' ')}>
          { receivingData !== null ? (receivingData ? 'Receiving Data' : 'Not Receiving Data') : 'Data Not Live' }
        </div>

        <div className='Toolbar-Session-Select'>
          <button className='Toolbar-Session-Select-Button' onClick={() => this.toggleSessionSelectOpen()}>Download A Session</button>
          { this.state.sessionSelectOpen && (<div className='Toolbar-Session-Select-Dropdown'>
            <button className='Toolbar-Session-Select-Dropdown-Button' onClick={() => this.downloadSession(null)}>
              Live
            </button>
            { sessions.map(session => (<button className='Toolbar-Session-Select-Dropdown-Button' key={session} onClick={() => this.downloadSession(session)}>{new Date(session * 1000).toLocaleString()}</button>)) }
          </div>)}
        </div>
        
      </div>
    )
  }
}
