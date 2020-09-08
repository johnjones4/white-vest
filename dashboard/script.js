(() => {
  const data = []
  const velocityMpsElement = document.getElementById('velocity-mps')
  const velocityFpsElement = document.getElementById('velocity-fps')
  const altitudeMetersElement = document.getElementById('altitude-m')
  const altitudeFeetElement = document.getElementById('altitude-f')
  const altitudeGraph = document.getElementById('altitude')
  const velocityGraph = document.getElementById('velocity')
  const graphAspectRatio = 3/4

  const setupSocket = () => {
    if (window.location.hostname === '') {
      return
    }
    let ws = new WebSocket(`ws://${window.location.hostname}:5678/`)
    ws.onmessage = event => {
      JSON.parse(event.data).forEach(dataPoint => {
        const [timestamp, meters] = dataPoint
        const metersPerSecond = data.length > 0 ? (meters - data[data.length - 1][1]) / (timestamp - data[data.length - 1][0]) : 0
        data.push([timestamp, meters, metersPerSecond])
      })
      // console.log(JSON.stringify(data))
    }
  }

  const generateXScale = (width) => {
    const defaultLimit = 60
    if (data.length === 0) {
      return d3.scaleLinear()
        .domain([0, defaultLimit])
        .range([0, width])
    } else {
      const dataLimit = data[data.length - 1][0] - data[0][0]
      return d3.scaleLinear()
        .domain([0, Math.max(defaultLimit, dataLimit)])
        .range([0, width])
    }
  }

  const generateYScale = (height, defaultMin, defaultMax, dataPointIndex) => {
    if (data.length === 0) {
      return d3.scaleLinear()
        .domain([
          defaultMin,
          defaultMax
        ])
        .range([ height, 0 ])
    } else {
      return d3.scaleLinear()
        .domain([
          Math.min(defaultMin, d3.min(data, d => d[dataPointIndex])),
          Math.max(defaultMax, d3.max(data, d => d[dataPointIndex]))
        ])
        .range([ height, 0 ])
    }
  }

  const setupGraph = (showRocket, element, defaultMin, defaultMax, dataPointIndex) => {
    const padding = 40
    const width = element.clientWidth - (padding * 2)
    const height = (element.clientWidth * graphAspectRatio)
    let svg = d3.select(element)
      .append('svg')
        .attr('width', width + (padding * 2))
        .attr('height', height + (padding * 2))
      .append('g')
        .attr('transform', `translate(${padding},${padding})`)
    
    const xScale = generateXScale(width)
    const yScale = generateYScale(height, defaultMin, defaultMax, dataPointIndex)

    const xAxis = svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
    
    const yAxis = svg.append('g')
      .call(d3.axisLeft(yScale))
    
    const path = svg.append('path')
      .datum(data)
      .attr('d', d3.line()
        .x(d => xScale(d[0] - data[0][0]))
        .y(d => yScale(d[dataPointIndex]))
      )

    let rocket = null
    if (showRocket) {
      rocket = svg.append('image')
        .attr('width', 20)
        .attr('height', 48)
        .attr('x', -100)
        .attr('y', 0)
        .attr('xlink:href', 'rocket.svg')
    }

    return {
      width,
      height,
      xAxis,
      yAxis,
      path,
      defaultMin,
      defaultMax,
      dataPointIndex,
      rocket
    }
  }

  const refreshGraph = ({width, height, xAxis, yAxis, path, defaultMin, defaultMax, dataPointIndex, rocket}) => {
    const xScale = generateXScale(width)
    xAxis.call(d3.axisBottom(xScale))

    const yScale = generateYScale(height, defaultMin, defaultMax, dataPointIndex)
    yAxis.call(d3.axisLeft(yScale))

    path
      .datum(data)
      .attr('d', d3.line()
        .x(d => xScale(d[0] - data[0][0]))
        .y(d => yScale(d[dataPointIndex]))
      )

    if (rocket) {
      const backIndex = Math.max(0, data.length - 4)
      const slope = (
        (
          yScale(data[data.length - 1][1]) 
          - yScale(data[backIndex][1])
        )
        /
        (
          xScale(data[data.length - 1][0]) 
          - xScale(data[backIndex][0])
        )
      ) * -1 
      const rad = Math.atan(slope)
      const rotation = 90 - (rad * (180 / Math.PI))
      const x = xScale(data[data.length - 1][0] - data[0][0])
      const y = yScale(data[data.length - 1][dataPointIndex])
      rocket
        .attr('x', x)
        .attr('y', y)
        .attr('transform', `translate(-10,-24) rotate(${rotation}, ${x + 10}, ${y + 24})`)
    }
  }

  const refresh = () => {
    if (data.length == 0) {
      return
    }
    const latest = data[data.length - 1]
    const velocityMps = latest[2]
    const velocityFps = velocityMps * 3.28084
    velocityMpsElement.textContent = `${velocityMps.toFixed(2)} meters/second`
    velocityFpsElement.textContent = `${velocityFps.toFixed(2)} feet/second`
    const altitudeMeters = latest[1]
    const altitudeFeet = altitudeMeters * 3.28084
    altitudeMetersElement.textContent = `${altitudeMeters.toFixed(2)} meters`
    altitudeFeetElement.textContent = `${altitudeFeet.toFixed(2)} feet`

    refreshGraph(altitudeGraphInfo)
    refreshGraph(velocityGraphInfo)
  }

  setupSocket()
  const altitudeGraphInfo = setupGraph(true, altitudeGraph, 0, 100, 1)
  const velocityGraphInfo = setupGraph(false, velocityGraph, -10, 10, 2)
  setInterval(refresh, 1000)
  refresh()
})()
