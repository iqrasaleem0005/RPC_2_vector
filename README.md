# Distributed RPC System with Vector Clocks

A Python implementation of a Remote Procedure Call (RPC) system with vector clocks for tracking causality in distributed systems.

## Prerequisites
- Python 3.11+
- Docker (optional, for containerized run)

## Install (local)
```bash
pip install -r requirements.txt
```

## Run Server (local)
```bash
python server.py
```
Server runs on http://localhost:8080

## Test with curl
```bash
curl -s -X POST http://localhost:8080/add -H "Content-Type: application/json" -d '{"x":2, "y":3}'
# {"result":5}

curl -s -X POST http://localhost:8080/multiply -H "Content-Type: application/json" -d '{"x":4, "y":5}'
# {"result":20}
```

## Run Client (with 2s timeout)
```bash
python client.py
# add(2,3) = 5
# multiply(4,5) = 20
```

If the server doesn't respond in 2 seconds, the client prints:
```
Request timed out
```

## Docker
Build and run the server:
```bash
docker build -t rpc-server .
docker run -p 8080:8080 rpc-server
```

This image no longer requires Flask; it's built on Python stdlib HTTPServer.
Then execute the client on your host (requires Python and `requests`).

## Deployed on Render (optional)
Your service URL (example): `https://rpc-1-1.onrender.com`

Notes:
- `/add` and `/multiply` are POST-only. Browsers use GET → you’ll see 404 for GET `/add` or `/multiply`.
- Render uses `HEAD /` for health checks; our server returns 501 for HEAD, which is harmless.

Call endpoints with POST:

PowerShell
```powershell
$body = '{"x":2,"y":3}'
Invoke-RestMethod -Uri https://rpc-1-1.onrender.com/add -Method Post -Body $body -ContentType 'application/json'

$body = '{"x":4,"y":5}'
Invoke-RestMethod -Uri https://rpc-1-1.onrender.com/multiply -Method Post -Body $body -ContentType 'application/json'
```

curl
```bash
curl -s -X POST https://rpc-1-1.onrender.com/add -H "Content-Type: application/json" -d '{"x":2,"y":3}'
curl -s -X POST https://rpc-1-1.onrender.com/multiply -H "Content-Type: application/json" -d '{"x":4,"y":5}'
```

## Vector Clock Implementation

This system implements vector clocks to track causality in distributed systems:

### Vector Clock Operations
- `increment(node_id)` - Increment local counter
- `update(other_clock)` - Merge with another vector clock  
- `compare(other_clock)` - Determine relationship:
  - `happens-before` (→) - This event happened before the other
  - `happens-after` (←) - This event happened after the other
  - `concurrent` (‖) - Events are concurrent
  - `equal` (=) - Events are equal

### Vector Clock RPC Client
```bash
# Basic vector clock client
python client.py

# Causality demonstration with two clients
python client.py causality

# Vector clock simulation and analysis
python demo_vector_clocks.py
```

### Vector Clock Features
- **Causality Detection**: Track which events happened before others
- **Concurrent Event Detection**: Identify events that occurred simultaneously
- **Clock Synchronization**: Merge vector clocks across distributed nodes
- **RPC Integration**: Vector clocks are automatically propagated in RPC calls

### Example Output
```
=== Vector Clock RPC Client ===
Initial client clock: {'client1': 0, 'server': 0}

--- Calling /add ---
[client1] Causality: happens-after
[client1] Client clock: {'client1': 1, 'server': 0}
[client1] Server clock: {'server': 1, 'client1': 1, 'server': 0}
add(2,3) = 5
Client clock after add: {'client1': 1, 'server': 1}
```

## Files
- `vector_clock.py` - Vector clock implementation
- `server.py` - RPC server with vector clock support
- `client.py` - RPC client with vector clock propagation
- `demo_vector_clocks.py` - Comprehensive vector clock demonstrations
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies

GIThub url : https://github.com/iqrasaleem0005/RPC_1
