import React, { Component } from 'react'
import Widget from './Widget'
import * as d3 from 'd3'
import './LocationWidget.css'
import { Locality } from '../../model/Session'

type LocationWidgetProps = {
  locality: Locality | null,
  name: string,
}

type LocationWidgetState = {
  projection: d3.GeoProjection
}


export default class LocationWidget extends Component<LocationWidgetProps, LocationWidgetState> {
  width: number
  height: number

  constructor(props: LocationWidgetProps) {
    super(props)
    this.width = 0
    this.height = 0
    this.state = {
      projection: this.generateProjection()
    }
  }

  componentDidUpdate (prevProps: LocationWidgetProps) {
    if (JSON.stringify(prevProps.locality) !== JSON.stringify(this.props.locality)) {
      this.setState({
        projection: this.generateProjection()
      })
    }
  }

  dimensionsReady (el: HTMLDivElement | null) {
    if (el) {
      let update = false
      if (this.width !== el.clientWidth) {
        this.width = el.clientWidth
        update = true
      }
      if (this.height !== el.clientHeight) {
        this.height = el.clientHeight
        update = true
      }
      if (update) {
        this.setState({
          projection: this.generateProjection()
        })
      }
    }
  }

  generateProjection () {
    if (this.props.locality === null) {
      return d3.geoMercator()
    }
    const heightLat = Math.abs(this.props.locality.there[1] - this.props.locality.here[1]) * 2
    const widthLon = Math.abs(this.props.locality.there[0] - this.props.locality.here[0]) * 2
    const s = Math.min(
      this.width / widthLon,
      this.height / heightLat
    ) * 40

    const projection = d3.geoMercator()
      .scale(s)
      .translate([this.width / 2, this.height / 2])
      .center(this.props.locality.here)

    return projection
  }

  render () {
    if (this.props.locality === null) {
      return 
    }

    const locBase = this.state.projection(this.props.locality.here) as [number, number]
    const locRocket = this.state.projection(this.props.locality.there) as [number, number]

    const arrowUnit = (this.height / 10)

    return (
      <Widget 
        name={this.props.name} 
        dimensionsReady={el => this.dimensionsReady(el)} 
        className='LocationWidget'
        lastReading={`${this.props.locality.distance.toFixed(2)} m, ${this.props.locality.bearing.toFixed(2)}°`}
      >
        <svg className='LocationWidget'>
          <line 
            x1={locBase[0]}
            y1={locBase[1]}
            x2={locRocket[0]}
            y2={locRocket[1]}
            className='LocationWidget-Connector'
          />
          <line 
            x1={locBase[0]}
            y1={locBase[1]}
            x2={locBase[0]}
            y2={locBase[1] - arrowUnit}
            className='LocationWidget-North'
          />
          <line 
            x1={locBase[0]}
            y1={locBase[1] - arrowUnit}
            x2={locBase[0] - (arrowUnit * 0.25)}
            y2={locBase[1] - (arrowUnit * 0.75)}
            className='LocationWidget-North'
          />
          <line 
            x1={locBase[0]}
            y1={locBase[1] - arrowUnit}
            x2={locBase[0] + (arrowUnit * 0.25)}
            y2={locBase[1] - (arrowUnit * 0.75)}
            className='LocationWidget-North'
          />
          <text
            x={locBase[0] - 5}
            y={locBase[1] - (arrowUnit * 1.1)}
            className='LocationWidget-North-Text'
          >N</text>
          <circle
            cx={locBase[0]}
            cy={locBase[1]}
            r={4}
            className='LocationWidget-Base'
          />
          <circle
            cx={locRocket[0]}
            cy={locRocket[1]}
            r={4}
            className='LocationWidget-Rocket'
          />
          
        </svg>
      </Widget>
    )
  }
}
