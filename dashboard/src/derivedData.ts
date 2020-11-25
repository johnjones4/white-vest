import {Index, SEA_LEVEL_PRESSURE} from './consts'

export const transformTelemetryArray = (data: Array<Array<number>>) => {
  const data1 = data
    .map(dataPoint => dataPoint.concat([
      44307.7 * (1 - Math.pow((dataPoint[Index.PRESSURE] / SEA_LEVEL_PRESSURE), 0.190284)),
      0,
      Math.atan2(-1.0 * dataPoint[Index.ACCELERATION_X], dataPoint[Index.ACCELERATION_Z]) * (180.0 / Math.PI),
      Math.atan2(-1.0 * dataPoint[Index.ACCELERATION_Y], dataPoint[Index.ACCELERATION_Z]) * (180.0 / Math.PI),
      (Math.atan2(dataPoint[Index.MAGNETIC_Y], dataPoint[Index.MAGNETIC_X]) * 180.0) / Math.PI,
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
    dataPoint[Index.VELOCITY] = data1.length > 0 ? (dataPoint[Index.ALTITUDE] - data1[data1.length - 1][Index.ALTITUDE]) / (dataPoint[Index.TIMESTAMP] - data1[data1.length - 1][Index.TIMESTAMP]) : 0
    return dataPoint
  })
}

export const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) : number => {
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


function bearing(startLat: number, startLng: number, destLat: number, destLng: number) : number {
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
