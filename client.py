import sys
import json
import socket
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError
from vector_clock import VectorClock


BASE_URL = "http://localhost:8082"
# BASE_URL = "https://rpc-1-1.onrender.com"

TIMEOUT_SECONDS = 5


class RpcClient:
    """RPC Client with vector clock support."""
    
    def __init__(self, client_id: str, base_url: str = BASE_URL):
        self.client_id = client_id
        self.base_url = base_url
        self.vector_clock = VectorClock(client_id, [client_id, "server"])
        self.timeout = TIMEOUT_SECONDS
        
    def call_rpc(self, endpoint: str, payload: dict):
        """Make RPC call with vector clock propagation."""
        # Increment client clock before sending
        self.vector_clock.increment()
        
        # Add vector clock to payload
        payload_with_clock = payload.copy()
        payload_with_clock["vector_clock"] = self.vector_clock.to_dict()
        
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(payload_with_clock).encode("utf-8")
        req = urlrequest.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                raw = resp.read().decode(charset)
                data = json.loads(raw)
                
                # Update client clock with server response
                if "vector_clock" in data:
                    server_clock = VectorClock.from_dict(data["vector_clock"], "server")
                    self.vector_clock.update(server_clock)
                    
                # Log causality information
                if "causality" in data:
                    causality = data["causality"]
                    print(f"[{self.client_id}] Causality: {causality['relationship']}")
                    print(f"[{self.client_id}] Client clock: {causality.get('client_clock', 'N/A')}")
                    print(f"[{self.client_id}] Server clock: {causality.get('server_clock', 'N/A')}")
                
                return data.get("result"), data
                
        except HTTPError as e:
            try:
                raw = e.read().decode("utf-8")
                data = json.loads(raw)
                print(f"[{self.client_id}] Request failed: HTTP {e.code} - {data}")
            except Exception:
                print(f"[{self.client_id}] Request failed: HTTP {e.code}")
            return None, None
        except URLError as e:
            if isinstance(e.reason, (TimeoutError, socket.timeout)):
                print(f"[{self.client_id}] Request timed out")
            else:
                print(f"[{self.client_id}] Request failed: {e}")
            return None, None
    
    def get_clock(self):
        """Get current vector clock."""
        return self.vector_clock.to_dict()


def call_rpc(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw = resp.read().decode(charset)
            data = json.loads(raw)
            return data.get("result")
    except HTTPError as e:
        try:
            raw = e.read().decode("utf-8")
            data = json.loads(raw)
            print(f"Request failed: HTTP {e.code} - {data}")
        except Exception:
            print(f"Request failed: HTTP {e.code}")
        return None
    except URLError as e:
        if isinstance(e.reason, (TimeoutError, socket.timeout)):
            print("Request timed out")
        else:
            print(f"Request failed: {e}")
        return None


def main():
    """Main function demonstrating vector clock RPC."""
    print("=== Vector Clock RPC Client ===")
    
    # Create client with vector clock support
    client = RpcClient("client1")
    print(f"Initial client clock: {client.get_clock()}")
    
    # Make RPC calls
    print("\n--- Calling /add ---")
    add_result, add_data = client.call_rpc("/add", {"x": 2, "y": 3})
    if add_result is not None:
        print(f"add(2,3) = {add_result}")
    print(f"Client clock after add: {client.get_clock()}")
    
    print("\n--- Calling /multiply ---")
    multiply_result, multiply_data = client.call_rpc("/multiply", {"x": 4, "y": 5})
    if multiply_result is not None:
        print(f"multiply(4,5) = {multiply_result}")
    print(f"Client clock after multiply: {client.get_clock()}")
    
    print("\n--- Final client clock ---")
    print(f"Final client clock: {client.get_clock()}")


def demo_causality():
    """Demonstrate causality with two clients."""
    print("\n=== Causality Demonstration ===")
    
    # Create two clients
    client_a = RpcClient("clientA")
    client_b = RpcClient("clientB")
    
    print(f"Initial clocks - A: {client_a.get_clock()}, B: {client_b.get_clock()}")
    
    # Client A makes a request
    print("\n--- Client A calls /add ---")
    result_a, data_a = client_a.call_rpc("/add", {"x": 1, "y": 2})
    print(f"Client A result: {result_a}")
    print(f"Client A clock: {client_a.get_clock()}")
    
    # Client B makes a request
    print("\n--- Client B calls /multiply ---")
    result_b, data_b = client_b.call_rpc("/multiply", {"x": 3, "y": 4})
    print(f"Client B result: {result_b}")
    print(f"Client B clock: {client_b.get_clock()}")
    
    # Compare clocks
    clock_a = VectorClock.from_dict(client_a.get_clock(), "clientA")
    clock_b = VectorClock.from_dict(client_b.get_clock(), "clientB")
    relationship = clock_a.compare(clock_b)
    print(f"\nClock relationship: {relationship}")
    
    # Client A makes another request
    print("\n--- Client A calls /add again ---")
    result_a2, data_a2 = client_a.call_rpc("/add", {"x": 5, "y": 6})
    print(f"Client A result: {result_a2}")
    print(f"Client A clock: {client_a.get_clock()}")
    
    # Final comparison
    clock_a_final = VectorClock.from_dict(client_a.get_clock(), "clientA")
    clock_b_final = VectorClock.from_dict(client_b.get_clock(), "clientB")
    final_relationship = clock_a_final.compare(clock_b_final)
    print(f"\nFinal clock relationship: {final_relationship}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "causality":
        demo_causality()
    else:
        main()


