import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from "react-leaflet"
import { useEffect, useState } from "react"
import axios from "axios"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import AnimatedTrain from "./AnimatedTrain"
import TrainInfoPanel from "./TrainInfoPanel"
import { CircleMarker } from "react-leaflet"
delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png"
})

const trainIcon = new L.Icon({
  iconUrl:"https://cdn-icons-png.flaticon.com/512/565/565410.png",
  iconSize:[30,30]
})

export default function LiveMap(){

const [trains,setTrains] = useState([])
const [tracks,setTracks] = useState(null)

const [occupiedEdges,setOccupiedEdges] = useState([])
const [selectedTrain,setSelectedTrain] = useState(null)

useEffect(()=>{

axios.get("http://127.0.0.1:5000/tracks")
.then(res=>setTracks(res.data))

},[])

useEffect(()=>{

const interval=setInterval(async ()=>{

const res=await axios.get("http://127.0.0.1:5000/trains")
setTrains(res.data)


},1000)

return()=>clearInterval(interval)

},[])
useEffect(()=>{

  const fetchEdges = async () => {
    const res = await axios.get("http://127.0.0.1:5000/edges")
    setOccupiedEdges(res.data)
  }

  fetchEdges()
  const interval = setInterval(fetchEdges,1000)

  return ()=>clearInterval(interval)

},[])




return(

<MapContainer
center={[22.65,88.34]}
zoom={11}
style={{height:"100%",width:"100%"}}
>

<TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

{tracks && (

<GeoJSON
data={tracks}
style={{
color:"#ff2e2e",
weight:3
}}
/>

)}

{trains.map(train => (


<AnimatedTrain
key={train.id}
lat={train.lat}
lon={train.lon}
onClick={()=>setSelectedTrain(train)}
>
<TrainInfoPanel train={selectedTrain}/>
<Popup>
Train {train.id}
</Popup>
</AnimatedTrain>

))}


</MapContainer>

)

}