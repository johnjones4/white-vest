import React, { Component } from 'react'
import './Banner.css'

type BannerProps = {
  error: Error | null
}

type BannerState = {
  visible: boolean
}

export default class Banner extends Component<BannerProps, BannerState> {
  constructor(props: BannerProps) {
    super(props)
    this.state = {
      visible: true
    }
  }

  componentDidUpdate (prevProps: BannerProps) {
    if (prevProps.error !== this.props.error && !this.state.visible) {
      this.setState({ visible: true })
    }
  }

  render () {
    return this.props.error && this.state.visible ? (
      <div className='Banner'>
        <div className='Banner-Message'>
          { this.props.error.message }
        </div>
        <button className='Banner-Close' onClick={() => this.setState({ visible: false })}>
          &times;
        </button>
      </div>
    ) : null
  }
}
