import React, { Component } from 'react'
import './Banner.css'

export default class Banner extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: true
    }
  }

  componentDidUpdate (prevProps) {
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
