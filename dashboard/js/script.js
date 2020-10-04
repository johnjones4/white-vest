(() => {
  const INDEX = {
    TIMESTAMP:          0,
    PRESSURE:           1,
    TEMPERATURE:        2,
    ACCELERATION_X:     3,
    ACCELERATION_Y:     4,
    ACCELERATION_Z:     5,
    MAGNETIC_X:         6,
    MAGNETIC_Y:         7,
    MAGNETIC_Z:         8,
    RSSI:               9,
    //Calculated values
    ALTITUDE:           10,
    VELOCITY:           11,
    PITCH:              12,
    ROLL:               13,
    YAW:                14
  }
  const SEA_LEVEL_PRESSURE = 1014.050964

  const data = []

  const flightTimeElement = document.getElementById('flight-time')
  let receivingData = false
  let receivingDataTimeout = null
  let graphs = [
    new LineGraph(data, 'rssi', 'Signal Strength', 'RSSI', -100, 0, INDEX.RSSI),
    new LineGraph(data, 'altitude', 'Altitude', 'm', 0, 100, INDEX.ALTITUDE),
    new LineGraph(data, 'velocity', 'Velocity', 'm/s', -10, 10, INDEX.VELOCITY),
    new LineGraph(data, 'temperature', 'Temperature', 'C', 0, 50, INDEX.TEMPERATURE),
    new LineGraph(data, 'pressure', 'Pressure', 'mbar', 1000, 1050, INDEX.PRESSURE),
    new RocketAngleGraph(data, 'pitch', 'Pitch', '°', INDEX.PITCH, 'res/rocket.svg'),
    new RocketAngleGraph(data, 'roll', 'Yaw', '°', INDEX.ROLL, 'res/rocket.svg'),
    new RocketAngleGraph(data, 'yaw', 'Roll', '°', INDEX.YAW, 'res/rocket_top.svg'),
  ]

  const setupGraphs = () => {
    graphs.forEach(g => g.setup())
  }

  const setupSocket = () => {
    if (window.location.hostname === '') {
      return
    }
    let ws = new WebSocket(`ws://${window.location.hostname}:5678/`)
    ws.onmessage = event => {
      JSON.parse(event.data).forEach(dataPoint => {
        dataPoint.push(44307.7 * (1 - Math.pow((dataPoint[INDEX.PRESSURE] / SEA_LEVEL_PRESSURE), 0.190284)))
        dataPoint.push(data.length > 0 ? (dataPoint[INDEX.ALTITUDE] - data[data.length - 1][INDEX.ALTITUDE]) / (dataPoint[INDEX.TIMESTAMP] - data[data.length - 1][INDEX.TIMESTAMP]) : 0)
        dataPoint.push(Math.atan2(-1.0 * dataPoint[INDEX.ACCELERATION_X], dataPoint[INDEX.ACCELERATION_Z]) * (180.0 / Math.PI))
        dataPoint.push(Math.atan2(-1.0 * dataPoint[INDEX.ACCELERATION_Y], dataPoint[INDEX.ACCELERATION_Z]) * (180.0 / Math.PI))
        dataPoint.push((Math.atan2(dataPoint[INDEX.MAGNETIC_Y], dataPoint[INDEX.MAGNETIC_X]) * 180.0) / Math.PI)
        data.push(dataPoint)
      })
      receivingData = true
      if (receivingDataTimeout) {
        clearTimeout(receivingDataTimeout)
      }
      receivingDataTimeout = setTimeout(() => {
        receivingData = false
      }, 5000)
    }
  }

  const refresh = () => {
    if (receivingData && !document.body.classList.contains('status-receiving')) {
      document.body.classList.remove('status-not-receiving')
      document.body.classList.add('status-receiving')
    } else if (!receivingData && !document.body.classList.contains('status-not-receiving')) {
      document.body.classList.remove('status-receiving')
      document.body.classList.add('status-not-receiving')
    }
    
    graphs.forEach(g => g.refresh())

    if (data.length > 0) {
      const time = data[data.length - 1][0]
      const minutes = Math.floor(time / 60)
      const seconds = (time - minutes * 60).toFixed(1)
      flightTimeElement.textContent = `Flight Time: ${minutes}:${seconds}`
    }
  }

  setupGraphs()
  setupSocket()
  setInterval(refresh, 1000)
  refresh()
})()
