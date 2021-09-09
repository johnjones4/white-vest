class Widget {
  constructor(title, parent, extractor) {
    this.title = title
    this.parent = parent
    this.extractor = extractor
  }

  attach() {
    const widget = document.createElement('div')
    widget.className = 'widget'

    const header = document.createElement('div')
    header.className = 'widget-header'
    widget.appendChild(header)

    const title = document.createElement('div')
    title.className = 'widget-title'
    title.textContent = this.title
    header.appendChild(title)

    this.details = document.createElement('div')
    this.details.className = 'widget-details'
    header.appendChild(this.details)

    const content = document.createElement('div')
    content.className = 'widget-content'
    content.appendChild(this.initDOM())
    widget.appendChild(content)

    this.parent.appendChild(widget)

    this.initContent()
  }

  setDetails(details) {
    this.details.textContent = details
  }

  update(data) {}

  initDOM() {}

  initContent() {}
}
