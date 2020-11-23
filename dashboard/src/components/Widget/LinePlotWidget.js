import React, { Component } from 'react'
import Widget from './Widget'
import * as d3 from 'd3'
import './LinePlotWidget.css'
import {Axis, axisPropsFromTickScale, LEFT, BOTTOM} from 'react-d3-axis'

const padding = 40

export default class LinePlotWidget extends Component {
  constructor(props) {
    super(props)
    this.width = 0
    this.height = 0
    this.state = {
      xScale: this.generateXScale(),
      yScale: this.generateYScale()
    }
  }

  componentDidMount () {

  }

  componentDidUpdate (prevProps) {
    if (prevProps.data.length !== this.props.data.length) {
      this.setState({
        xScale: this.generateXScale(),
        yScale: this.generateYScale()
      })
    }
  }

  dimensionsReady (el) {
    if (el) {
      let update = false
      if (this.width !== el.clientWidth - (padding * 2)) {
        this.width = el.clientWidth - (padding * 2)
        update = true
      }
      if (this.height !== el.clientHeight - (padding * 2)) {
        this.height = el.clientHeight - (padding * 2)
        update = true
      }
      if (update) {
        this.setState({
          xScale: this.generateXScale(),
          yScale: this.generateYScale()
        })
      }
    }
  }

  generateXScale () {
    const defaultLimit = 60
    if (this.props.data.length === 0) {
      return d3.scaleLinear()
        .domain([0, defaultLimit])
        .range([0, this.width])
    } else {
      const dataLimit = this.props.data[this.props.data.length - 1][0] - this.props.data[0][0]
      return d3.scaleLinear()
        .domain([0, Math.max(defaultLimit, dataLimit)])
        .range([0, this.width])
    }
  }

  generateYScale () {
    if (this.props.data.length === 0) {
      return d3.scaleLinear()
        .domain([
          this.props.defaultMin,
          this.props.defaultMax
        ])
        .range([ this.height, 0 ])
    } else {
      return d3.scaleLinear()
        .domain([
          Math.min(this.props.defaultMin, d3.min(this.props.data, d => d[1])),
          Math.max(this.props.defaultMax, d3.max(this.props.data, d => d[1]))
        ])
        .range([ this.height, 0 ])
    }
  }

  render () {
    const lineGenerator = d3.line()
      .x(d => this.state.xScale(d[0] - this.props.data[0][0]))
      .y(d => this.state.yScale(d[1]))
    return (
      <Widget
        dimensionsReady={el => this.dimensionsReady(el)}
        name={this.props.name}
        lastReading={this.props.data.length > 0 ? this.props.data[this.props.data.length - 1][1].toFixed(2) + ' ' + this.props.units : ''}
      >
        <svg className='LinePlotWidget'>
          <g transform={`translate(${padding},${padding})`}>
            <Axis {...axisPropsFromTickScale(this.state.yScale, 10)} style={{orient: LEFT}} />
            <g transform={`translate(0,${this.height})`}>
              <Axis {...axisPropsFromTickScale(this.state.xScale, 10)} style={{orient: BOTTOM}} />
            </g>
            <path d={lineGenerator(this.props.data)} />
          </g>
        </svg>
      </Widget>
    )
  }
}
