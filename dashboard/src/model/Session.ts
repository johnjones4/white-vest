import { Command, Index, SEA_LEVEL_PRESSURE } from '../consts'
import { transformTelemetryArray } from '../derivedData'

export type TimePlottable = Array<[number, number]>

export type Coordinate = [number, number]

export interface Locality {
  here: Coordinate | null
  there: Coordinate | null
  bearing: number | null
  distance: number | null
}

export interface Attitude {
  pitch: number | null
  roll: number | null
  yaw: number | null
}

export enum ReceivingState {
  Receiving = 'Receiving Data',
  NoSignal = 'No Signal',
  NotReceiving = 'Not Receiving',
}
export interface SessionDelegate {
  onNewLiveData: () => void
  onReceivingDataChange: () => void
  onError: (error: Error) => void
}

export default class Session {
  private readonly delegate: SessionDelegate
  private receivingDataTimeout: null | number
  public receivingState: ReceivingState
  private data: Array<Array<number | null>>
  private ws?: WebSocket
  private readonly fileStream: any
  private wsAddress?: string
  private basePressure: number | null
  private closed = false

  constructor (delegate: SessionDelegate) {
    this.delegate = delegate
    this.fileStream = (window as any).createWriteStream(`White Vest Data ${new Date().getTime()}.csv`)
    this.data = []
    this.receivingDataTimeout = null
    this.receivingState = ReceivingState.NotReceiving
    this.basePressure = null
  }

  start (wsAddress?: string): void {
    if (this.closed) {
      return
    }
    if (wsAddress !== undefined) {
      this.wsAddress = wsAddress
    }
    try {
      if (this.ws !== undefined) {
        this.ws?.close()
      }
    } catch (e) {}
    this.setReceivingState(ReceivingState.NotReceiving)
    this.ws = new WebSocket(`ws://${this.wsAddress as string}:5678/`)
    this.ws.onmessage = (event: MessageEvent) => this.newWebSocketData(event)
    this.ws.onerror = () => {
      console.log('Restarting')
      setTimeout(() => this.start(), 1000)
    }
  }

  stop (): void {
    this.closed = true
    this.ws?.close()
    if (this.receivingDataTimeout !== null) {
      clearTimeout(this.receivingDataTimeout)
    }
  }

  async sendCommand (command: Command): Promise<any> {
    if (this.wsAddress === undefined) {
      return await Promise.resolve()
    }
    await fetch(`http://${this.wsAddress}:8080/${command}`, {
      method: 'POST',
      mode: 'no-cors'
    })
  }

  setReceivingState (newState: ReceivingState): void {
    if (newState !== this.receivingState) {
      this.receivingState = newState
      this.delegate.onReceivingDataChange()
    }
  }

  establishBasePressure (): void {
    if (this.basePressure === null) {
      const pressures = this.data.filter(row => row[Index.PRESSURE] !== null).map(row => row[Index.PRESSURE]).slice(0, 10) as number[]
      if (pressures.length > 0) {
        this.basePressure = pressures.reduce((total, pressure) => total + pressure, 0) / pressures.length
      }
    }
  }

  newWebSocketData (event: MessageEvent): void {
    try {
      if (this.closed) {
        return
      }
      const receivedData = JSON.parse(event.data) as number[][]
      const transformedData = transformTelemetryArray(receivedData, this.basePressure === null ? SEA_LEVEL_PRESSURE : this.basePressure)
      this.fileStream.write(receivedData.map(line => line.join(',')).join('\n') + '\n')
      this.data = this.data.concat(transformedData)
      this.establishBasePressure()
      this.delegate.onNewLiveData()
      if (this.receivingDataTimeout !== null) {
        clearTimeout(this.receivingDataTimeout)
      }
      this.setReceivingState(this.data.length > 0 && this.data[this.data.length - 1][Index.TIMESTAMP] !== null ? ReceivingState.Receiving : ReceivingState.NoSignal)
      this.receivingDataTimeout = window.setTimeout(() => {
        this.setReceivingState(ReceivingState.NotReceiving)
      }, 7000)
    } catch (e) {
      this.delegate.onError(e)
    }
  }

  getTimePlottable (yAxis: Index): TimePlottable {
    return this.data
      .filter(row => row[Index.TIMESTAMP] !== null && row[yAxis] !== null)
      .map(row => [row[Index.TIMESTAMP] as number, row[yAxis] as number])
  }

  getCurrentLocality (): Locality | null {
    if (this.data.length === 0) {
      return null
    }
    const current = this.data[this.data.length - 1]
    return {
      here: current[Index.BASE_LAT] === null || current[Index.BASE_LON] === null
        ? null
        : [current[Index.BASE_LAT] as number, current[Index.BASE_LON] as number],
      there: current[Index.ROCKET_LAT] === null || current[Index.ROCKET_LON] === null
        ? null
        : [current[Index.ROCKET_LAT] as number, current[Index.ROCKET_LON] as number],
      bearing: current[Index.BEARING],
      distance: current[Index.DISTANCE]
    }
  }

  getCurrentAttitude (): Attitude | null {
    if (this.data.length === 0) {
      return null
    }
    const current = this.data[this.data.length - 1]
    return {
      pitch: current[Index.PITCH],
      roll: current[Index.ROLL],
      yaw: current[Index.YAW]
    }
  }

  getCurrentSeconds (): number | null {
    return this.data[this.data.length - 1][Index.TIMESTAMP] === null ? null : this.data[this.data.length - 1][Index.TIMESTAMP] as number
  }

  isCameraRecording (): boolean {
    return this.data.length > 0 && this.data[this.data.length - 1][Index.CAMERA_IS_RUNNING] === 1.0
  }
}
