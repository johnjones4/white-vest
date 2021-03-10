import React, { Component, ReactElement } from 'react'
import Widget from './Widget'
import './LocationWidget.css'
import { Locality, Coordinate } from '../../model/Session'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import L, { Map } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow
})

L.Marker.prototype.options.icon = DefaultIcon
interface LocationWidgetProps {
  locality: Locality | null
  name: string
}

interface LocationWidgetState {
  zoom: number
}

const defaultZoom = 20
export default class LocationWidget extends Component<LocationWidgetProps, LocationWidgetState> {
  private map?: Map

  constructor (props: LocationWidgetProps) {
    super(props)
    this.state = {
      zoom: defaultZoom
    }
  }

  componentDidUpdate (prevProps: LocationWidgetProps): void {
    if (this.map !== undefined) {
      if (this.props.locality?.here !== null && (prevProps.locality === null || prevProps.locality.here === null ||
        (this.props.locality?.here as Coordinate)[0] !== prevProps.locality.here[0] || (this.props.locality?.here as Coordinate)[1] !== prevProps.locality.here[1])) {
        this.map.setView((this.props.locality?.here as Coordinate), this.state.zoom)
      }
    }
  }

  setMap (map: Map): void {
    this.map = map
  }

  render (): ReactElement | null {
    if (this.props.locality === null) {
      return null
    }
    return (
      <Widget
        name={this.props.name}
        className='LocationWidget'
        lastReading={`${this.props.locality.distance !== null ? this.props.locality.distance.toFixed(2) : ''} m, ${this.props.locality.bearing !== null ? this.props.locality.bearing.toFixed(2) : ''}°`}
      >
        <MapContainer center={this.props.locality.here !== null ? this.props.locality.here : [0, 0]} zoom={this.state.zoom} scrollWheelZoom={false} whenCreated={map => this.setMap(map)}>
          <TileLayer
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
          />
          {this.props.locality.there !== null ? (<Marker position={this.props.locality.there as [number, number]} />) : null}
        </MapContainer>
      </Widget>
    )
  }
}
