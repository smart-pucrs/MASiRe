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
    'token':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJOYW1lIjoiTmlzc2FuIiwiVmVyc2lvbiI6IjEuMyIsIlR5cGUiOiJDYXIiLCJPd25lciI6Ijg3NDYyIn0.jBzTytj9vhXC8eNsZe_f7LBXLCFdVjG65v9Znp3ZVQA',
    'id': '1',
    'method': 'move',
    'parameters': ['24', '32']
}


function sendRandomJobs(){

    const  moves = ['move','deliver','photograph','rescue_victim']

    const rand =  moves[Math.floor(Math.random()*4)]

    const move = {
    'token':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJOYW1lIjoiTmlzc2FuIiwiVmVyc2lvbiI6IjEuMyIsIlR5cGUiOiJDYXIiLCJPd25lciI6Ijg3NDYyIn0.jBzTytj9vhXC8eNsZe_f7LBXLCFdVjG65v9Znp3ZVQA',
    'id': '1',
    'method': rand,
    'parameters': [Math.random()*100,Math.random()*100]
    }

    return move
}

axios.post('http://127.0.0.1:5000/requestConnection',agent_accepted).then(response =>{
    let data = response.data;
    const address = `http://${data.ip+':'+data.port}`;
    console.log(data);
    const socket = client.connect(address);
    socket.on('connection_result', ()=>socket.emit('ready',{data:data.encoded}));
    socket.on(data.encoded+'/connecting_agents', (result)=>console.log(result))
    socket.on(data.encoded+'/pre_step', (result)=>{
        console.log(result)
        socket.emit('receive_jobs',sendRandomJobs())
    })
    socket.on('received_jobs_result',(result)=>console.log(result))

}).catch(err => console.log(err));

