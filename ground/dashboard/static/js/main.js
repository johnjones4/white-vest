(() => {
  let data = []
  const dashboard = new Dashboard(document.getElementById('main'))
  dashboard.attach()
  const webSocket = new WebSocket(`ws://${window.location.host}/api/data`)
  webSocket.onmessage = (e) => {
    data = data.concat(JSON.parse(e.data))
    dashboard.update(data)
  }
})()
