/**
 * MY-OSINT Node.js Server Alternative (Zero-Dependency)
 * Alternatif runner jika pengguna ingin menjalankan dengan `node backend/server.js`
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = process.env.PORT || 8080;
const PUBLIC_DIR = path.join(__dirname, '..', 'public');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);

  // Forward API calls to Python backend runner or execute Python module CLI
  if (url.pathname.startsWith('/api/')) {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      // Execute Python command
      const pythonScript = path.join(__dirname, 'server.py');
      // Forward directly via internal invocation or python command
      const cmd = `python3 -c "
import sys, json
sys.path.insert(0, '${__dirname}')
from server import RetroOSINTHandler
from modules.nik_parser import parse_nik
from modules.phone_tracer import analyze_phone
from modules.holehe_checker import check_email_footprint
from modules.username_tracker import scan_username
from modules.google_dorker import generate_dorks
from modules.ghunt_profiler import analyze_google_account
from modules.ghost_intel import analyze_target_intel

data = json.loads('''${body.replace(/'/g, "\\'")}''') if '''${body.replace(/'/g, "\\'")}''' else {}
path = '${url.pathname}'
if path == '/api/nik':
    print(json.dumps(parse_nik(data.get('nik', ''))))
elif path == '/api/phone':
    print(json.dumps(analyze_phone(data.get('phone', ''))))
elif path == '/api/email':
    print(json.dumps(check_email_footprint(data.get('email', ''))))
elif path == '/api/username':
    print(json.dumps(scan_username(data.get('username', ''))))
elif path == '/api/dorks':
    print(json.dumps(generate_dorks(data.get('target', ''))))
elif path == '/api/ghunt':
    print(json.dumps(analyze_google_account(data.get('target', ''))))
elif path == '/api/ghostintel':
    print(json.dumps(analyze_target_intel(data.get('target', ''))))
else:
    print(json.dumps({'error': 'Not found'}))
"`;
      exec(cmd, { maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
        if (error) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: error.message }));
          return;
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(stdout);
      });
    });
    return;
  }

  // Static File Serving
  let filePath = path.join(PUBLIC_DIR, url.pathname === '/' ? 'index.html' : url.pathname);
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found in C:\\WINDOWS\\SYSTEM32\\OSINT\\');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log(`[Node.js Runner] MY-OSINT 95 running on http://localhost:${PORT}`);
});
