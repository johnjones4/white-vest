import React, { Component, ReactElement } from 'react'
import './Banner.css'

interface BannerProps {
  error: Error | null
}

interface BannerState {
  visible: boolean
}

export default class Banner extends Component<BannerProps, BannerState> {
  constructor (props: BannerProps) {
    super(props)
    this.state = {
      visible: true
    }
  }

  componentDidUpdate (prevProps: BannerProps): void {
    if (prevProps.error !== this.props.error && !this.state.visible) {
      // eslint-disable-next-line react/no-did-update-set-state
      this.setState({ visible: true })
    }
  }

  render (): ReactElement | null {
    return this.props.error !== null && this.state.visible
      ? (
        <div className='Banner'>
          <div className='Banner-Message'>
            {this.props.error.message}
          </div>
          <button className='Banner-Close' onClick={() => this.setState({ visible: false })}>
            &times;
          </button>
        </div>
        )
      : null
  }
}
