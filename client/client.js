const axios = require('axios');
const client = require('socket.io-client');

const agent_denied = {
    "Name": "Toyota",
    "Version": "1.3",
    "Type": "Car",
    "Owner": "87462"
};


const agent_accepted = {
    "Name": "Nissan",
    "Version": "1.3",
    "Type": "Car",
    "Owner": "87462"
};


axios.post('http://127.0.0.1:5000/requestConnection',agent_accepted).then(response =>{
    let data = response.data;
    const address = `http://${data.ip+':'+data.port}`;
    console.log(address);
    const socket = client.connect(address);
    socket.on('connecting_agents', ()=>socket.emit('ready',{data:data.encoded}));
    socket.on('connection_result',(data)=> console.log(data));
    socket.on(data.encoded,(result)=>console.log(result))
}).catch(err => console.log(err));

