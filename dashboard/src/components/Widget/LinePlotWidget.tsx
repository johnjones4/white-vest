import React, { Component } from 'react'
import Widget from './Widget'
import * as d3 from 'd3'
import './LinePlotWidget.css'

const hPadding = 35
const vPadding = 20

type LinePlotWidgetProps = {
  data: Array<[number, number]> | null,
  defaultMin: number,
  defaultMax: number,
  name: string,
  units: string
}

type LinePlotWidgetState = {
  xScale: d3.ScaleLinear<number, number>,
  yScale: d3.ScaleLinear<number, number>,
}

export default class LinePlotWidget extends Component<LinePlotWidgetProps, LinePlotWidgetState> {
  width: number
  height: number

  constructor(props: LinePlotWidgetProps) {
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

  componentDidUpdate (prevProps: LinePlotWidgetProps) {
    if (this.props.data && (!prevProps.data || prevProps.data.length !== this.props.data.length)) {
      this.setState({
        xScale: this.generateXScale(),
        yScale: this.generateYScale()
      })
    }
  }

  dimensionsReady (el: HTMLDivElement | null) {
    if (el) {
      let update = false
      if (this.width !== el.clientWidth - (hPadding * 2)) {
        this.width = el.clientWidth - (hPadding * 2)
        update = true
      }
      if (this.height !== el.clientHeight - (vPadding * 2)) {
        this.height = el.clientHeight - (vPadding * 2)
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

  generateXScale () : d3.ScaleLinear<number, number> {
    if (!this.props.data) {
      return d3.scaleLinear()
    }
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

  generateYScale () : d3.ScaleLinear<number, number> {
    if (!this.props.data) {
      return d3.scaleLinear()
    }
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
          Math.min(this.props.defaultMin, d3.min(this.props.data, d => d[1]) as number),
          Math.max(this.props.defaultMax, d3.max(this.props.data, d => d[1]) as number)
        ])
        .range([ this.height, 0 ])
    }
  }

  render () {
    if (!this.props.data) {
      return null
    }

    const lineGenerator = d3.line()
      .x(d => this.state.xScale(d[0] - (this.props.data as Array<[number, number]>)[0][0]))
      .y(d => this.state.yScale(d[1]))

    return (
      <Widget
        dimensionsReady={el => this.dimensionsReady(el)}
        name={this.props.name}
        lastReading={this.props.data.length > 0 ? this.props.data[this.props.data.length - 1][1].toFixed(2) + ' ' + this.props.units : ''}
      >
        <svg className='LinePlotWidget'>
          <g transform={`translate(${hPadding},${vPadding})`}>
            <g ref={axis => d3.select(axis).call(d3.axisLeft(this.state.yScale) as any) } />
            <g transform={`translate(0,${this.height})`} ref={axis => d3.select(axis).call(d3.axisBottom(this.state.xScale) as any) } />
            <path d={lineGenerator(this.props.data) as string} />
          </g>
        </svg>
      </Widget>
    )
  }
}
