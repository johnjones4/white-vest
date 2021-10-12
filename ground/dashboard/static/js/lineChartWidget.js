class LineChartWidget extends Widget {
  constructor(title, units, parent, extractor) {
    super(title, parent, extractor)
    this.units = units
  }

  update(data) {
    const extractedData = this.extractor(data)
    this.chart.data.datasets[0].data = extractedData
    this.chart.update()
    if (extractedData.length > 0) {
      this.setDetails(`${extractedData[extractedData.length - 1].y.toFixed(2)} ${this.units}`)
    }
  }

  initDOM() {
    this.canvas = document.createElement('canvas')
    return this.canvas
  }

  initContent() {
    const ctx = this.canvas.getContext('2d')
    this.chart = new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: [{
          data: [],
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1,
        showLine: true,
        elements: {
          point: {
            radius: 0
          },
          line: {
            borderColor: '#000',
            borderWidth: 1,
          }
        },
        plugins: {
          legend: {
            display: false
          }
        },
        animation: {
          duration: 0,
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Seconds'
            }
          },
          y: {
            title: {
              display: true,
              text: this.units
            }
          }
        }
      }
    })
  }
}
