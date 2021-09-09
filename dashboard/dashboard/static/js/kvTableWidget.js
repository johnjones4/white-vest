class KVTableWidget extends Widget {
  constructor(title, keys, parent, extractor) {
    super(title, parent, extractor)
    this.keys = keys
  }

  update(data) {
    const extractedData = this.extractor(data)
    extractedData.forEach(({key, value, normal}) => {
      if (this.valueTds[key]) {
        this.valueTds[key].textContent = value
        if (normal) {
          this.valueTds[key].classList.add('normal')
        } else {
          this.valueTds[key].classList.remove('normal')
        }
      }
    })
  }

  initDOM() {
    const table = document.createElement('table')
    table.className = 'kv-table'
    const thead = document.createElement('thead')
    table.appendChild(thead)
    const tr = document.createElement('tr')
    thead.appendChild(tr)
    const headers = ['Attribute', 'Value']
    headers.forEach(h => {
      const th = document.createElement('th')
      th.textContent = h
      tr.appendChild(th)
    })
    const tbody = document.createElement('tbody')
    table.appendChild(tbody)
    this.valueTds = {}
    this.keys.forEach(key => {
      const tr = document.createElement('tr')
      tbody.appendChild(tr)
      const keyTd = document.createElement('td')
      keyTd.textContent = key
      tr.appendChild(keyTd)
      const valueTd = document.createElement('td')
      valueTd.className = 'kv-table-value'
      tr.appendChild(valueTd)
      this.valueTds[key] = valueTd
    })
    return table
  }

  initContent() {
    
  }
}
