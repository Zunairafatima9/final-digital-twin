import LiveMap from "./components/LiveMap"

function App(){

return(

<div style={{
background:"#111",
color:"white",
height:"100vh"
}}>

<h1 style={{
padding:"20px",
fontSize:"40px"
}}>
Railway Digital Twin Control Center
</h1>

<div style={{
padding:"20px"
}}>

<LiveMap/>

</div>

</div>

)

}

export default App