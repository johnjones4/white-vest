const graphPadding = 40
const graphAspectRatio = 0.55

class LineGraph extends Graph {
  constructor (data, id, name, units, showRocket, defaultMin, defaultMax, dataPointIndex) {
    super(data, id, name, units, dataPointIndex)
    this.showRocket = showRocket
    this.defaultMin = defaultMin
    this.defaultMax = defaultMax
  }

  setupGraph () {
    this.width = this.svgWrapperElement.clientWidth - (graphPadding * 2) - 1
    this.height = (this.svgWrapperElement.clientWidth * graphAspectRatio)
    let svg = d3.select(this.svgWrapperElement)
      .append('svg')
        .attr('width', this.width + (graphPadding * 2))
        .attr('height', this.height + (graphPadding * 2))
      .append('g')
        .attr('transform', `translate(${graphPadding},${graphPadding})`)
    
    const xScale = this.generateXScale()
    const yScale = this.generateYScale()

    this.xAxis = svg.append('g')
      .attr('transform', `translate(0,${this.height})`)
      .call(d3.axisBottom(xScale))
    
    this.yAxis = svg.append('g')
      .call(d3.axisLeft(yScale))
    
    this.path = svg.append('path')
      .datum(this.data)
      .attr('d', d3.line()
        .x(d => xScale(d[0] - this.data[0][0]))
        .y(d => yScale(d[this.dataPointIndex]))
      )

    if (this.showRocket) {
      this.rocket = svg.append('image')
        .attr('width', 20)
        .attr('height', 48)
        .attr('x', -100)
        .attr('y', 0)
        .attr('xlink:href', 'rocket.svg')
    }
  }

  refresh () {
    super.refresh()

    if (this.data.length === 0) {
      return
    }

    const xScale = this.generateXScale()
    this.xAxis.call(d3.axisBottom(xScale))

    const yScale = this.generateYScale()
    this.yAxis.call(d3.axisLeft(yScale))

    this.path
      .datum(this.data)
      .attr('d', d3.line()
        .x(d => xScale(d[0] - this.data[0][0]))
        .y(d => yScale(d[this.dataPointIndex]))
      )

    if (this.rocket) {
      const backIndex = Math.max(0, this.data.length - 4)
      const slope = (
        (
          yScale(this.data[this.data.length - 1][1]) 
          - yScale(this.data[backIndex][1])
        )
        /
        (
          xScale(this.data[this.data.length - 1][0]) 
          - xScale(this.data[backIndex][0])
        )
      ) * -1 
      const rad = Math.atan(slope)
      const rotation = 90 - (rad * (180 / Math.PI))
      const x = xScale(this.data[this.data.length - 1][0] - this.data[0][0])
      const y = yScale(this.data[this.data.length - 1][this.dataPointIndex])
      this.rocket
        .attr('x', x)
        .attr('y', y)
        .attr('transform', `translate(-10,-24) rotate(${rotation}, ${x + 10}, ${y + 24})`)
    }
  }

  generateXScale (width) {
    const defaultLimit = 60
    if (this.data.length === 0) {
      return d3.scaleLinear()
        .domain([0, defaultLimit])
        .range([0, width])
    } else {
      const dataLimit = this.data[this.data.length - 1][0] - this.data[0][0]
      return d3.scaleLinear()
        .domain([0, Math.max(defaultLimit, dataLimit)])
        .range([0, this.width])
    }
  }

  generateYScale () {
    if (this.data.length === 0) {
      return d3.scaleLinear()
        .domain([
          this.defaultMin,
          this.defaultMax
        ])
        .range([ this.height, 0 ])
    } else {
      return d3.scaleLinear()
        .domain([
          Math.min(this.defaultMin, d3.min(this.data, d => d[this.dataPointIndex])),
          Math.max(this.defaultMax, d3.max(this.data, d => d[this.dataPointIndex]))
        ])
        .range([ this.height, 0 ])
    }
  }
}
