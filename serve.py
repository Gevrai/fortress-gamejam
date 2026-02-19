#!/usr/bin/env python3
import http.server, socket, sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# get local IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

handler = http.server.SimpleHTTPRequestHandler
handler.log_message = lambda *a: None  # silence request logs

print(f"Serving on http://{ip}:{port}")
print("Ctrl+C to stop")
http.server.HTTPServer(("0.0.0.0", port), handler).serve_forever()
