class MapWidget extends Widget {
  constructor(title, parent, extractor) {
    super(title, parent, extractor)
  }

  update(data) {
    const mapData = this.extractor(data)
    this.map.setView(mapData.coordinates, this.map.getZoom())
    this.marker.setLatLng(mapData.coordinates)
    this.setDetails(`Bearing: ${mapData.bearing.toFixed(2)}°, Distance: ${mapData.distance.toFixed(2)}m`)
  }

  initDOM() {
    this.mapContainer = document.createElement('div')
    this.mapContainer.className = 'map-container'
    return this.mapContainer
  }

  initContent() {
    this.map = L.map(this.mapContainer).setView([0,0], 17)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map)
    this.marker = L.circle([0,0], {
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.5,
      radius: 5
    }).addTo(this.map)
  }
}
