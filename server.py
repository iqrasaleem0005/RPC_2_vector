import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from vector_clock import VectorClock


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def parse_json(handler: BaseHTTPRequestHandler):
    try:
        length = int(handler.headers.get("Content-Length", "0"))
        raw = handler.rfile.read(length) if length > 0 else b""
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def validate_operands(payload):
    if not isinstance(payload, dict):
        return False, "Invalid JSON body"
    if "x" not in payload or "y" not in payload:
        return False, "Missing 'x' or 'y' in request body"
    try:
        x_val = float(payload["x"]) if isinstance(payload["x"], (int, float, str)) else None
        y_val = float(payload["y"]) if isinstance(payload["y"], (int, float, str)) else None
    except (TypeError, ValueError):
        return False, "'x' and 'y' must be numbers"
    if x_val is None or y_val is None:
        return False, "'x' and 'y' must be numbers"
    return True, (x_val, y_val)


class RpcHandler(BaseHTTPRequestHandler):
    # Server's vector clock
    server_clock = VectorClock("server", ["server"])
    
    def do_GET(self):
        if self.path == "/" or self.path == "":
            json_response(self, 200, {
                "message": "RPC server is running",
                "endpoints": {
                    "POST /add": {"x": "number", "y": "number"},
                    "POST /multiply": {"x": "number", "y": "number"},
                    "GET /health": "ok"
                }
            })
        elif self.path == "/health":
            json_response(self, 200, {"status": "ok"})
        else:
            json_response(self, 404, {"error": "Not found"})

    def do_POST(self):
        # Parse request with vector clock
        payload = parse_json(self)
        if not payload:
            json_response(self, 400, {"error": "Invalid JSON"})
            return
            
        # Extract client vector clock if present
        client_clock = None
        if "vector_clock" in payload:
            try:
                client_clock = VectorClock.from_dict(payload["vector_clock"], "client")
                # Update server clock with client clock
                self.server_clock.update(client_clock)
            except Exception as e:
                print(f"Error parsing client vector clock: {e}")
        
        # Increment server clock
        self.server_clock.increment()
        
        if self.path == "/add":
            ok, data = validate_operands(payload)
            if not ok:
                json_response(self, 400, {"error": data, "vector_clock": self.server_clock.to_dict()})
                return
            x_val, y_val = data
            result = x_val + y_val
            if float(result).is_integer():
                result = int(result)
            json_response(self, 200, {
                "result": result, 
                "vector_clock": self.server_clock.to_dict(),
                "causality": {
                    "server_clock": self.server_clock.to_dict(),
                    "client_clock": client_clock.to_dict() if client_clock else None,
                    "relationship": self.server_clock.compare(client_clock) if client_clock else "no_client_clock"
                }
            })
            return

        if self.path == "/multiply":
            ok, data = validate_operands(payload)
            if not ok:
                json_response(self, 400, {"error": data, "vector_clock": self.server_clock.to_dict()})
                return
            x_val, y_val = data
            result = x_val * y_val
            if float(result).is_integer():
                result = int(result)
            json_response(self, 200, {
                "result": result, 
                "vector_clock": self.server_clock.to_dict(),
                "causality": {
                    "server_clock": self.server_clock.to_dict(),
                    "client_clock": client_clock.to_dict() if client_clock else None,
                    "relationship": self.server_clock.compare(client_clock) if client_clock else "no_client_clock"
                }
            })
            return

        json_response(self, 404, {"error": "Not found", "vector_clock": self.server_clock.to_dict()})


def run(host: str = "0.0.0.0", port: int = 8080):
    server = HTTPServer((host, port), RpcHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()

