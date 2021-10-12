class AttitudeWidget extends Widget {
  update(data) {
    const angle = this.extractor(data)
    this.setDetails(angle.toFixed(2) + '°')
    this.arrow.style.transform = `rotate(${angle}deg)`
  }

  initDOM() {
    const attitudeContainer = document.createElement('div')
    attitudeContainer.className = 'attitude-container'
    this.arrow = document.createElement('div')
    this.arrow.className = 'attitude-arrow'
    attitudeContainer.appendChild(this.arrow)
    return attitudeContainer
  }

  initContent() {}
}
