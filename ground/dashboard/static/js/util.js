function makeXYExtractor(propType, propName) {
  return (data) => data.map(segment => ({
    x: segment.raw.timestamp,
    y: segment[propType][propName]
  }))
}

function makeCoordinateExtractor() {
  return (data) => ({
    coordinates: [data[data.length - 1].raw.coordinate.lat, data[data.length - 1].raw.coordinate.lon],
    bearing: data[data.length - 1].computed.bearing,
    distance: data[data.length - 1].computed.distance
  })
}

function makeInfoExtractor() {
  return (data) => ({
    pcnt: data[data.length - 1].raw.cameraProgress,
    time: data[data.length - 1].raw.timestamp,
    mode: data[data.length - 1].computed.flightMode
  })
}

function makeSingleExtractor(propType, propName) {
  return (data) => data[data.length - 1][propType][propName]
}

function formatSeconds(time) {   
  const hrs = ~~(time / 3600)
  const mins = ~~((time % 3600) / 60)
  const secs = ~~time % 60
  let ret = ''
  if (hrs > 0) {
      ret += '' + hrs + ':' + (mins < 10 ? '0' : '')
  }
  ret += '' + mins + ':' + (secs < 10 ? '0' : '')
  ret += '' + secs
  return ret
}
