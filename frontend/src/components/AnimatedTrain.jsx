import { Marker } from "react-leaflet"
import { useSpring } from "@react-spring/web"
import { useEffect } from "react"
import L from "leaflet"

const trainIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/565/565410.png",
  iconSize: [30, 30],
  iconAnchor: [15, 15]
})

export default function AnimatedTrain({ lat, lon, onClick }) {

  const [style, api] = useSpring(() => ({
    lat: lat,
    lon: lon,
    config: { duration: 800 }
  }))

  useEffect(() => {

    if(lat !== undefined && lon !== undefined){

      api.start({
        lat: lat,
        lon: lon
      })

    }

  }, [lat, lon])

  return (

    <Marker
      position={[style.lat.get(), style.lon.get()]}
      icon={trainIcon}
      eventHandlers={{
        click: onClick
      }}
    />

  )

}