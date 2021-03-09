import {Index, SEA_LEVEL_PRESSURE} from './consts'

export const transformTelemetryArray = (data: Array<Array<number | null>>): Array<Array<number | null>> => {
  const data1 = data
    .map(dataPoint => dataPoint.concat([
      dataPoint[Index.PRESSURE] === null ? null : 44307.7 * (1 - Math.pow((dataPoint[Index.PRESSURE] as number / 100) / SEA_LEVEL_PRESSURE, 0.190284)),
      0,
      dataPoint[Index.ACCELERATION_X] === null || dataPoint[Index.ACCELERATION_Z] === null ? null : Math.atan2(-1.0 * (dataPoint[Index.ACCELERATION_X] as number), dataPoint[Index.ACCELERATION_Z] as number) * (180.0 / Math.PI),
      dataPoint[Index.ACCELERATION_Y] === null || dataPoint[Index.ACCELERATION_Z] === null ? null : Math.atan2(-1.0 * (dataPoint[Index.ACCELERATION_Y] as number), dataPoint[Index.ACCELERATION_Z] as number) * (180.0 / Math.PI),
      dataPoint[Index.MAGNETIC_Y] === null || dataPoint[Index.MAGNETIC_X] === null ? null : (Math.atan2(dataPoint[Index.MAGNETIC_Y] as number, dataPoint[Index.MAGNETIC_X] as number) * 180.0) / Math.PI,
      calculateDistance(
        dataPoint[Index.ROCKET_LAT],
        dataPoint[Index.ROCKET_LON],
        dataPoint[Index.BASE_LAT],
        dataPoint[Index.BASE_LON]
      ),
      bearing(
        dataPoint[Index.BASE_LAT],
        dataPoint[Index.BASE_LON],
        dataPoint[Index.ROCKET_LAT],
        dataPoint[Index.ROCKET_LON]
      )
    ]))
  return data1.map(dataPoint => {
    if (dataPoint[Index.PRESSURE] !== null) {
      dataPoint[Index.PRESSURE] = dataPoint[Index.PRESSURE] as number / 100
    }
    dataPoint[Index.VELOCITY] = dataPoint[Index.ALTITUDE] !== null 
      && data1[data1.length - 1][Index.ALTITUDE] !== null 
      && dataPoint[Index.TIMESTAMP] !== null
      && data1[data1.length - 1][Index.TIMESTAMP] !== null
      && data1.length > 0 ? 
        (dataPoint[Index.ALTITUDE] as number - (data1[data1.length - 1][Index.ALTITUDE] as number)) / (dataPoint[Index.TIMESTAMP] as number - (data1[data1.length - 1][Index.TIMESTAMP] as number)) 
        : 0
    return dataPoint
  })
}

export const calculateDistance = (lat1: number | null, lon1: number | null, lat2: number | null, lon2: number | null) : number | null => {
  if (lat1 === null || lon1 === null || lat2 === null || lon2 === null) {
    return null
  }
  const R = 6371e3; // metres
  const φ1 = lat1 * Math.PI/180; // φ, λ in radians
  const φ2 = lat2 * Math.PI/180;
  const Δφ = (lat2-lat1) * Math.PI/180;
  const Δλ = (lon2-lon1) * Math.PI/180;

  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  return R * c; // in metres
}

function toRadians(degrees: number) : number {
  return degrees * Math.PI / 180;
};
 
// Converts from radians to degrees.
function toDegrees(radians: number) : number {
  return radians * 180 / Math.PI;
}


function bearing(startLat: number | null, startLng: number | null, destLat: number | null, destLng: number | null) : number | null {
  if (startLat === null || startLng === null || destLat === null || destLng === null) {
    return null
  }
  startLat = toRadians(startLat);
  startLng = toRadians(startLng);
  destLat = toRadians(destLat);
  destLng = toRadians(destLng);

  const y = Math.sin(destLng - startLng) * Math.cos(destLat);
  const x = Math.cos(startLat) * Math.sin(destLat) -
        Math.sin(startLat) * Math.cos(destLat) * Math.cos(destLng - startLng);
  let brng = Math.atan2(y, x);
  brng = toDegrees(brng);
  return (brng + 360) % 360;
}
