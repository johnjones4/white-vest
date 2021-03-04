import React, { Component } from 'react'
import Widget from './Widget'
import './LocationWidget.css'
import { Locality } from '../../model/Session'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

type LocationWidgetProps = {
  locality: Locality | null,
  name: string,
}

type LocationWidgetState = {
  zoom: number
}

const defaultZoom = 20
export default class LocationWidget extends Component<LocationWidgetProps, LocationWidgetState> {

  constructor(props: LocationWidgetProps) {
    super(props)
    this.state = {
      zoom: defaultZoom
    }
  }

  
  render () {
    if (this.props.locality === null) {
      return 
    }

    console.log(this.props.locality)

    return (
      <Widget 
        name={this.props.name} 
        dimensionsReady={el => console.log(el)} 
        className='LocationWidget'
        lastReading={`${this.props.locality.distance.toFixed(2)} m, ${this.props.locality.bearing.toFixed(2)}°`}
      >
        <MapContainer center={this.props.locality.here} zoom={this.state.zoom} scrollWheelZoom={false}>
         <TileLayer
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={this.props.locality.there} />
        </MapContainer>
      </Widget>
    )
  }
}
