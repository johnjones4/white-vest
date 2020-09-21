class RocketAngleGraph extends Graph {
  constructor (data, id, name, units, dataPointIndex, filename) {
    super(data, id, name, units, dataPointIndex)
    this.filename = filename
  }

  setupGraph () {
    this.element.classList.add('rocket-angle-graph')
    this.rocket = document.createElement('img')
    this.rocket.className = 'rocket-angle'
    this.rocket.src = this.filename
    this.svgWrapperElement.appendChild(this.rocket)
  }

  refresh () {
    super.refresh()
    if (this.data.length === 0) {
      return
    }

    const value = this.data[this.data.length - 1][this.dataPointIndex]
    this.rocket.style.transform = `rotate(${value}deg)`
  }
}
