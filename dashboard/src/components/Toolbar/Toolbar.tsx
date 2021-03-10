import React, { Component, ReactElement } from 'react'
import { ReceivingState } from '../../model/Session'
import './Toolbar.css'

interface ToolbarProps {
  receivingState: ReceivingState
  wsAddress: string
  wsAddressUpdated: (wsAddress: string) => void
  onReset: () => void
}

interface ToolbarState {
  wsAddress: string
}

export default class Toolbar extends Component<ToolbarProps, ToolbarState> {
  constructor (props: ToolbarProps) {
    super(props)
    this.state = {
      wsAddress: props.wsAddress
    }
  }

  cssForReceivingState (): string {
    switch (this.props.receivingState) {
      case ReceivingState.Receiving:
        return 'Toolbar-Stream-Status-Receiving'
      default:
        return 'Toolbar-Stream-Status-Not-Receiving'
    }
  }

  render (): ReactElement | null {
    const { receivingState } = this.props
    return (
      <div className='Toolbar'>
        <div className={['Toolbar-Stream-Status', this.cssForReceivingState()].join(' ')}>
          {receivingState}
        </div>
        <div className='Toolbar-Address'>
          <input type='text' placeholder='Ground Device Address' value={this.state.wsAddress} onChange={event => this.setState({ wsAddress: event.target.value })} className='Toolbar-Address-Input' />
          <button className='Toolbar-Address-Button' onClick={() => this.props.wsAddressUpdated(this.state.wsAddress)}>Set</button>
        </div>
        <button className='Toolbar-Reset-Button' onClick={() => this.props.onReset()}>Reset Stream</button>
      </div>
    )
  }
}
