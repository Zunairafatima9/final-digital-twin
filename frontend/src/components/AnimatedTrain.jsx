import { Marker } from "react-leaflet"
import { useSpring, animated } from "@react-spring/web"
import { useEffect } from "react"
import L from "leaflet"

const trainIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/565/565410.png",
  iconSize: [30, 30]
})

export default function AnimatedTrain({position}){

const [styles,api] = useSpring(()=>({
  lat: position[0],
  lng: position[1]
}))

useEffect(()=>{

api.start({
  lat: position[0],
  lng: position[1],
  config:{duration:1000}
})

},[position])

return(

<Marker
position={[styles.lat.get(),styles.lng.get()]}
icon={trainIcon}
/>

)

}