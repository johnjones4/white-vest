const fs = require('fs')
const path = require('path')
const os = require('os')

window.createWriteStream = (filename) => fs.createWriteStream(path.join(os.homedir(), filename))
