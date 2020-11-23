import React, { Component } from 'react'
import Widget from './Widget'
import * as d3 from 'd3'
import * as topojson from 'topojson'
import './LocationWidget.css'


export default class LocationWidget extends Component {
  constructor(props) {
    super(props)
    this.width = 0
    this.height = 0
    this.state = {
      projection: this.generateProjection(),
      mapFeatures: []
    }
  }

  componentDidUpdate (prevProps) {
    if (prevProps.data.join(',') !== this.props.data.join(',')) {
      this.setState({
        projection: this.generateProjection()
      })
    }
  }

  componentDidMount () {
    // this.loadMapFeatures()
  }

  async loadMapFeatures() {
    try {
      const response = await fetch('/features.json')
      const mapFeatures = await response.json()
      this.setState({
        mapFeatures: mapFeatures.features
      })
    } catch (e) {
      console.error(e)
    }
  }

  dimensionsReady (el) {
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

  getBaseCoords () {
    return [this.props.data[3], this.props.data[2]]
  }

  getRocketCoords () {
    return [this.props.data[1], this.props.data[0]]
  }

  generateProjection () {
    const heightLat = Math.abs(this.props.data[0] - this.props.data[2]) * 2
    const widthLon = Math.abs(this.props.data[1] - this.props.data[3]) * 2
    const s = Math.min(
      this.width / widthLon,
      this.height / heightLat
    ) * 40

    const projection = d3.geoMercator()
      .scale(s)
      .translate([this.width / 2, this.height / 2])
      .center(this.getBaseCoords())

    return projection
  }

  render () {
    const locBase = this.state.projection(this.getBaseCoords())
    const locRocket = this.state.projection(this.getRocketCoords())

    const arrowUnit = (this.height / 10)

    const mapPath = d3.geoPath().projection(this.state.projection)

    return (
      <Widget 
        name={this.props.name} 
        dimensionsReady={el => this.dimensionsReady(el)} lastReading='' className='LocationWidget'
        lastReading={`${this.props.data[4].toFixed(2)} m, ${this.props.data[5].toFixed(2)}°`}
      >
        <svg className='LocationWidget'>

          <g>
            { this.state.mapFeatures.map((feature, i) => (
              <path 
                d={mapPath(feature)}
                key={i}
                className='LocationWidget-Map-Line'
              />
            )) }
          </g>

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
