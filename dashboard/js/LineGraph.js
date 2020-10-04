const graphPadding = 40
const graphAspectRatio = 0.55

class LineGraph extends Graph {
  constructor (data, id, name, units, defaultMin, defaultMax, dataPointIndex) {
    super(data, id, name, units, dataPointIndex)
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
