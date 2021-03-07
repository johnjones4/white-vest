import React, { Component } from 'react'
import Widget from './Widget'
import './LocationWidget.css'
import { Locality } from '../../model/Session'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import { Map } from 'leaflet'
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
  private map?: Map

  constructor(props: LocationWidgetProps) {
    super(props)
    this.state = {
      zoom: defaultZoom
    }
  }

  componentDidUpdate (prevProps: LocationWidgetProps) {
    if (this.map) {
      if (this.props.locality && this.props.locality.here && (!prevProps.locality || !prevProps.locality.here || 
        this.props.locality.here[0] !== prevProps.locality.here[0] || this.props.locality.here[1] !== prevProps.locality.here[1])) {
        this.map.setView(this.props.locality.here, this.state.zoom)
      }
    }
  }

  
  render () {
    if (this.props.locality === null) {
      return null
    }
    
    return (
      <Widget 
        name={this.props.name} 
        className='LocationWidget'
        lastReading={`${this.props.locality.distance && this.props.locality.distance.toFixed(2)} m, ${this.props.locality.bearing && this.props.locality.bearing.toFixed(2)}°`}
      >
        <MapContainer center={this.props.locality.here ? this.props.locality.here : [0,0]} zoom={this.state.zoom} scrollWheelZoom={false} whenCreated={map => this.map = map}>
         <TileLayer
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {this.props.locality.there && (<Marker position={this.props.locality.there as [number,number]} />)}
        </MapContainer>
      </Widget>
    )
  }
}
