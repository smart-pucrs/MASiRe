import requests

agents = [
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQxIn0.OyDxesy_GlKAZxdaGieiUVas-W6BCpVVzNQMwU3cd9s",
                "agent_info": {"name": "car1"}
            },
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQyIn0.ocVROx0f1A7fH8fq9x8WRMNITSDi7q-HtGT0lAUhMPg",
                "agent_info": {"name": "drone1"}
            },
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQzIn0.7EDzzHgxbuLOa5oncQdMrIJ7ceIi_GbHDWY97NEiNs4",
                "agent_info": {"name": "boat1"}
            }
        ]

if __name__ == '__main__':
    for agent in agents:
        response = requests.post('http://localhost:12345/register_agent', json=agent).json()

    print("Agentes connectados")





