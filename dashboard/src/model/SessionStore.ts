import { transformTelemetryArray } from '../derivedData'
import Session from './Session'

export interface SessionStoreDelegate {
  onNewLiveData: () => void
  onReceivingDataChange: () => void
  onError: (error: Error) => void
  onSessionsListAvailable: () => void
}

export default class SessionStore {
  private receivingDataTimeout: null | number
  public receivingData: boolean
  private ws?: WebSocket
  private delegate: SessionStoreDelegate
  private sessionsCache: Map<number, Session>
  public liveData: Session
  public sessionsList: number[]
  private testMode: boolean

  constructor(delegate: SessionStoreDelegate, testMode: boolean) {
    this.delegate = delegate
    this.testMode = testMode
    this.receivingDataTimeout = null
    this.sessionsCache = new Map<number, Session>()
    if (!testMode) {
      this.sessionsList = []
      this.liveData = new Session(null, [])
      this.receivingData = false
    } else {
      this.sessionsList = Session.testSessions
      this.liveData = new Session(null, transformTelemetryArray(Session.testData))
      this.receivingData = true
    }
  }

  start () {
    if (!this.testMode) {
      this.ws = new WebSocket(`ws://${window.location.hostname}:5678/`)
      this.ws.onmessage = (event: MessageEvent) => this.newWebSocketData(event)
      this.loadSessionsList()
    } else {
      this.delegate.onNewLiveData()
      this.delegate.onSessionsListAvailable()
      this.delegate.onReceivingDataChange()
    }
  }

  newWebSocketData (event: MessageEvent) {
    try {
      const receivedData = JSON.parse(event.data) as number[][]
      const transformedData = transformTelemetryArray(receivedData)
      this.liveData = this.liveData.concat(transformedData)
      this.delegate.onNewLiveData()

      if (this.receivingDataTimeout) {
        clearTimeout(this.receivingDataTimeout)
      }
      this.receivingData = true
      this.delegate.onReceivingDataChange()
      this.receivingDataTimeout = window.setTimeout(() => {
        this.receivingData = false
        this.delegate.onReceivingDataChange()
      }, 5000)
    } catch (e) {
      this.delegate.onError(e)
    }
  }

  async loadSessionsList () {
    try {
      const response = await fetch('/api/session')
      const data = await response.json()
      if (response.status !== 200) {
        throw new Error(data.message)
      }
      this.sessionsList = data as number[]
      this.delegate.onSessionsListAvailable()
    } catch (e) {
      this.delegate.onError(e)
    }
  }

  async getSession(session: number) : Promise<Session | undefined> {
    if (this.testMode) {
      return new Session(session, transformTelemetryArray(Session.testData))
    }
    try {
      if (this.sessionsCache.has(session)) {
        return this.sessionsCache.get(session)
      }
      const response = await fetch(`/api/session/${session}`)
      const data = await response.json()
      if (response.status !== 200) {
        throw new Error(data.message)
      }
      const transformedData = transformTelemetryArray(data as number[][])
      const sessionObj = new Session(session, transformedData)
      this.sessionsCache.set(session, sessionObj)
      return sessionObj
    } catch (e) {
      this.delegate.onError(e)
    }
  }

  async startNewSession() {
    try {
      await fetch('/api/session', {
        method: 'POST'
      })
      this.loadSessionsList()
    } catch (e) {
      this.delegate.onError(e)
    }
  }
}
