const signalTimeout = 5000

class Dashboard {
  constructor(parent) {
    this.parent = parent
    this.children = []
    this.lastUpdate = null
    this.timeout = null
    this.data = []
  }

  attach() {
    this.container = document.createElement('div')
    this.container.className = 'dashboard'
    this.parent.appendChild(this.container)

    this.children = [
      new MissionInfoWidget('Flight Info', this.container, makeInfoExtractor()),
      new LineChartWidget('Altitude', 'm', this.container, makeXYExtractor('computed', 'smoothedAltitude')),
      new LineChartWidget('Velocity', 'm/s', this.container, makeXYExtractor('computed', 'smoothedVelocity')),
      new LineChartWidget('Temperature', '°C', this.container, makeXYExtractor('computed', 'smoothedTemperature')),
      new LineChartWidget('Pressure', 'mBar', this.container, makeXYExtractor('computed', 'smoothedPressure')),
      new AttitudeWidget('Pitch', this.container, makeSingleExtractor('computed', 'pitch')),
      new AttitudeWidget('Yaw', this.container, makeSingleExtractor('computed', 'yaw')),
      new LineChartWidget('RSSI', 'RSSI', this.container, makeXYExtractor('raw', 'rssi')),
      new KVTableWidget('Signal Stats', ['Data Points', 'Data Rate', 'Last Event Age', 'Receiving', 'RSSI', 'GPS Num Stats', 'GPS Signal Quality'], this.container, (d) => this.signalStatsExtractor(d)),
      new MapWidget('Location', this.container, makeCoordinateExtractor()),
    ]
    this.children.forEach(c => c.attach())
  }

  update(data) {
    if (this.timeout) {
      clearTimeout(this.timeout)
      this.timeout = null
    }
    if (data !== null) {
      this.data = data
      this.container.classList.add('receiving')
    } else {
      this.container.classList.remove('receiving')
    }
    this.children.forEach(child => child.update(this.data))
    if (data !== null) {
      this.lastUpdate = new Date()
    }
    this.timeout = setTimeout(() => this.update(null), signalTimeout)
  }


  signalStatsExtractor(data) {
    if (data.length === 0) {
      return []
    }
    const lastEventAge = this.lastUpdate === null ? null : (new Date().getTime() - this.lastUpdate.getTime())

    return [
      {
        key: 'Data Points',
        value: data.length,
        normal: data.length > 0
      },
      {
        key: 'Data Rate',
        value: data[data.length - 1].computed.dataRate.toFixed(2) + '/s',
        normal: data[data.length - 1].computed.dataRate > 1
      },
      {
        key: 'Last Event Age',
        value: lastEventAge === null ? 'Never' : (lastEventAge / 1000).toFixed(2) + 's',
        normal: lastEventAge !== null && lastEventAge < signalTimeout
      },
      {
        key: 'Receiving',
        value: lastEventAge !== null && lastEventAge < signalTimeout ? 'Yes' : 'No',
        normal: lastEventAge !== null && lastEventAge < signalTimeout
      },
      {
        key: 'RSSI',
        value: data[data.length - 1].raw.rssi,
        normal: data[data.length - 1].raw.rssi > -70
      },
      {
        key: 'GPS Num Stats',
        value: data[data.length - 1].raw.gpsInfo.sats,
        normal: data[data.length - 1].raw.gpsInfo.sats > 0
      },
      {
        key: 'GPS Signal Quality',
        value: data[data.length - 1].raw.gpsInfo.quality,
        normal: data[data.length - 1].raw.gpsInfo.quality > 0
      }
    ]
  }
}

