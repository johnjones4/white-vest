class Graph {
  constructor (data, id, name, units, dataPointIndex) {
    this.data = data
    this.id = id
    this.name = name
    this.units = units
    this.dataPointIndex = dataPointIndex
  }

  setup () {
    this.setupMainElement()
    this.setupGraph()
  }

  setupMainElement () {
    this.element = document.createElement('div')
    this.element.id = this.id
    this.element.classList.add('graph')
    const graphTemplate = document.getElementById('graph-template').innerHTML
    this.element.innerHTML = Mustache.render(graphTemplate, { name: this.name })
    this.currentDataElement = this.element.querySelector('.graph-current-data')
    this.svgWrapperElement = this.element.querySelector('.graph-svg-wrapper')
    document.getElementById('graphs').appendChild(this.element)
  }

  setupGraph () {
    throw new Error('Not implemented!')
  }

  refresh () {
    if (this.data.length === 0) {
      return 
    }

    const current = this.data[this.data.length - 1][this.dataPointIndex].toFixed(2) 
    this.currentDataElement.textContent = `${current} ${this.units}`
  }
}
