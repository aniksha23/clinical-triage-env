"""
HF Spaces entrypoint — runs inference once on startup, then serves results via HTTP.
"""
import threading
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

results = {"output": "Running inference...", "done": False}


def run_inference():
    proc = subprocess.Popen(
        [sys.executable, "inference.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    output_lines = []
    for line in proc.stdout:
        print(line, end="", flush=True)
        output_lines.append(line)
    proc.wait()
    results["output"] = "".join(output_lines)
    results["done"] = True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = results["output"].encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # suppress access logs


if __name__ == "__main__":
    thread = threading.Thread(target=run_inference, daemon=True)
    thread.start()

    server = HTTPServer(("0.0.0.0", 7860), Handler)
    print("Server running on port 7860", flush=True)
    server.serve_forever()
