const modeMap = {
  'P': 'Prelaunch',
  'AP': 'Powered Ascent',
  'AU': 'Unpowered Ascent',
  'DF': 'Freefall Descent',
  'DP': 'Parachute Descent',
  'R': 'Recovery'
}

class MissionInfoWidget extends Widget {
  update(data) {
    const extractedData = this.extractor(data)
    this.time.textContent = formatSeconds(extractedData.time)
    this.mode.textContent = modeMap[extractedData.mode]
    this.mode.className = ['mission-info-mode', 'mission-info-mode-' + extractedData.mode.toLowerCase()].join(' ')
  }

  initDOM() {
    const container = document.createElement('div')
    container.className = 'mission-info-container'

    this.time = document.createElement('div')
    this.time.className = 'mission-info-time'
    container.appendChild(this.time)

    this.mode = document.createElement('div')
    this.mode.className = 'mission-info-mode'
    container.appendChild(this.mode)

    return container
  }

  initContent() {
    
  }
}
