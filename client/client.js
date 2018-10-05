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

step_config_agent = {
    'id': '1',
    'method': 'move',
    'parameters': ['24', '32']
}

axios.post('http://127.0.0.1:5000/requestConnection',agent_accepted).then(response =>{
    let data = response.data;
    const address = `http://${data.ip+':'+data.port}`;
    console.log(data);
    const socket = client.connect(address);
    socket.on('connection_result', ()=>socket.emit('ready',{data:data.encoded}));
    socket.on(data.encoded+'/connecting_agents', (result)=>console.log(result))
    socket.on(data.encoded+'/pre_step', ()=>socket.emit('receive_jobs',step_config_agent))

}).catch(err => console.log(err));

