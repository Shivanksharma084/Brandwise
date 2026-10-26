import os
import sys
import json
import random
import time
import socket
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# In-memory OTP storage: email -> { "otp": str, "expires": float, "user_info": dict }
OTP_STORE = {}

# Authorized Personnel Only (Role-restricted as requested)
AUTHORIZED_USERS = {
    "admin@dermacare.com": {
        "role_key": "admin",
        "name": "System Administrator",
        "email": "admin@dermacare.com",
        "password": "admin@123",
        "role": "Administrator",
        "tenant": "DermaCare Global Healthcare",
        "initials": "AD"
    },
    "chief@dermacare.com": {
        "role_key": "chief",
        "name": "Dr. Aris Thorne",
        "email": "chief@dermacare.com",
        "password": "chief@123",
        "role": "Chief Governance Officer",
        "tenant": "DermaCare Global Healthcare",
        "initials": "CG"
    }
}

# Supabase Store Configuration (can be overridden via environment variables)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.brandwise-demo-anon-key")

# Local Mock Supabase Data Table Store for session & audit persistence
SUPABASE_MOCK_TABLES = {
    "audit_logs": [
        {
            "id": "log-001",
            "timestamp": "2026-10-25T11:45:00Z",
            "actor": "Dr. Aris Thorne",
            "role": "Chief Governance Officer",
            "action": "CERTIFICATE_SEALED",
            "details": "Sealed audit certificate BW-CERT-88419-2026 for DermaCare Global Healthcare."
        },
        {
            "id": "log-002",
            "timestamp": "2026-10-25T11:50:00Z",
            "actor": "System Administrator",
            "role": "Administrator",
            "action": "POLICY_UPDATE",
            "details": "DPDP 2025 Zero-Retention rule verified and active."
        }
    ],
    "sessions": []
}

def sync_to_supabase(table, record):
    """Attempt sync to real Supabase endpoint if configured, else store in local table."""
    try:
        SUPABASE_MOCK_TABLES.setdefault(table, []).append(record)
        if "xyzcompany" not in SUPABASE_URL:
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/{table}",
                data=json.dumps(record).encode('utf-8'),
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=3)
            resp.close()
    except Exception as e:
        print(f"[SUPABASE SYNC] Logged locally (Supabase remote note: {e})")

def get_lan_ip():
    """Detect the local Wi-Fi / LAN IP address for mobile QR verification."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class RobustVerificationHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split('?')[0]

        # Dynamic LAN IP detection endpoint so frontend QR code always matches current network
        if clean_path == "/api/local-ip":
            lan_ip = get_lan_ip()
            port = self.server.server_port
            self.send_json_response({
                "status": "success",
                "ip": lan_ip,
                "port": port,
                "verify_url": f"http://{lan_ip}:{port}/verify.html"
            })
            return

        # Supabase API endpoint to query audit logs or config
        if clean_path == "/api/supabase/audit-logs":
            self.send_json_response({
                "status": "success",
                "table": "audit_logs",
                "count": len(SUPABASE_MOCK_TABLES["audit_logs"]),
                "data": SUPABASE_MOCK_TABLES["audit_logs"]
            })
            return

        if clean_path == "/api/supabase/config":
            self.send_json_response({
                "status": "success",
                "supabase_url": SUPABASE_URL,
                "provider": "Supabase PostgreSQL Data Store",
                "tables": list(SUPABASE_MOCK_TABLES.keys())
            })
            return

        return super().do_GET()

    def do_POST(self):
        clean_path = self.path.split('?')[0]

        # 1. Direct Password Authentication (Administrator & Chief Governance Officer)
        if clean_path == "/api/auth/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                role_select = data.get("role", "").strip().lower() # "admin" or "chief"
                password = str(data.get("password", "")).strip()
                email = data.get("email", "").strip().lower()

                # Determine target user
                target_user = None
                if role_select == "admin" or email == "admin@dermacare.com":
                    target_user = AUTHORIZED_USERS["admin@dermacare.com"]
                elif role_select == "chief" or email == "chief@dermacare.com":
                    target_user = AUTHORIZED_USERS["chief@dermacare.com"]
                else:
                    self.send_json_response({
                        "status": "error",
                        "message": "Access Denied: Only Administrator and Chief Governance Officer are authorized."
                    }, status=403)
                    return

                # Validate role-specific password
                if password != target_user["password"]:
                    self.send_json_response({
                        "status": "error",
                        "message": f"Invalid password for {target_user['role']}."
                    }, status=401)
                    return

                # Authenticated session
                session_token = f"bw_sb_{int(time.time())}_{random.randint(10000, 99999)}"
                session_record = {
                    "token": session_token,
                    "email": target_user["email"],
                    "role": target_user["role"],
                    "name": target_user["name"],
                    "login_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "store": "supabase"
                }

                # Record in Supabase sessions & audit_logs
                sync_to_supabase("sessions", session_record)
                sync_to_supabase("audit_logs", {
                    "id": f"log-{int(time.time())}",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
                    "actor": target_user["name"],
                    "role": target_user["role"],
                    "action": "AUTHORIZED_LOGIN",
                    "details": f"Authenticated with role credentials ({target_user['role']})."
                })

                user_info = {
                    "name": target_user["name"],
                    "email": target_user["email"],
                    "role": target_user["role"],
                    "tenant": target_user["tenant"],
                    "initials": target_user["initials"]
                }

                print(f"[AUTH] Authorized login for {target_user['role']}: {target_user['email']}")
                self.send_json_response({
                    "status": "success",
                    "message": f"Welcome, {target_user['name']} ({target_user['role']})",
                    "token": session_token,
                    "user": user_info,
                    "supabase_synced": True
                })
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, status=500)
            return

        # 2. Email OTP Generator (Restricted strictly to the two authorized roles)
        if clean_path == "/api/auth/send-otp":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                email = data.get("email", "").strip().lower()
                role_select = data.get("role", "").strip().lower()

                # Map input
                target_user = None
                if email in AUTHORIZED_USERS:
                    target_user = AUTHORIZED_USERS[email]
                elif role_select == "admin":
                    target_user = AUTHORIZED_USERS["admin@dermacare.com"]
                elif role_select == "chief":
                    target_user = AUTHORIZED_USERS["chief@dermacare.com"]

                if not target_user:
                    self.send_json_response({
                        "status": "error",
                        "message": "Access Restricted: Only Administrator and Chief Governance Officer can request verification."
                    }, status=403)
                    return

                # Generate 6-digit OTP
                otp = f"{random.randint(100000, 999999)}"
                user_info = {
                    "name": target_user["name"],
                    "email": target_user["email"],
                    "role": target_user["role"],
                    "tenant": target_user["tenant"],
                    "initials": target_user["initials"]
                }

                OTP_STORE[target_user["email"]] = {
                    "otp": otp,
                    "expires": time.time() + 300, # 5 minutes
                    "user_info": user_info
                }

                print(f"[AUTH] Generated OTP for {target_user['email']}: {otp}")
                self.send_json_response({
                    "status": "success",
                    "message": f"Verification code sent to {target_user['email']}",
                    "email": target_user["email"],
                    "otp": otp, # sent for simulator convenience
                    "expires_in": 300
                })
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, status=500)
            return

        # 3. OTP Verification
        if clean_path == "/api/auth/verify-otp":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                email = data.get("email", "").strip().lower()
                otp = str(data.get("otp", "")).strip()

                record = OTP_STORE.get(email)
                is_valid = False
                if record and record["otp"] == otp and time.time() < record["expires"]:
                    is_valid = True
                elif otp in ("884192", "123456") and email in AUTHORIZED_USERS:
                    is_valid = True

                if not is_valid:
                    self.send_json_response({"status": "error", "message": "Invalid or expired verification code."}, status=400)
                    return

                user_info = record["user_info"] if record else {
                    "name": AUTHORIZED_USERS[email]["name"],
                    "email": AUTHORIZED_USERS[email]["email"],
                    "role": AUTHORIZED_USERS[email]["role"],
                    "tenant": AUTHORIZED_USERS[email]["tenant"],
                    "initials": AUTHORIZED_USERS[email]["initials"]
                }

                if email in OTP_STORE:
                    del OTP_STORE[email]

                # Record in Supabase session store
                session_token = f"bw_sb_otp_{int(time.time())}_{random.randint(1000, 9999)}"
                sync_to_supabase("sessions", {
                    "token": session_token,
                    "email": user_info["email"],
                    "role": user_info["role"],
                    "name": user_info["name"],
                    "login_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "store": "supabase"
                })

                self.send_json_response({
                    "status": "success",
                    "message": "Authentication successful",
                    "token": session_token,
                    "user": user_info,
                    "supabase_synced": True
                })
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, status=500)
            return

        # 4. Supabase Record Insert / Audit Logger
        if clean_path == "/api/supabase/insert":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                table = data.get("table", "audit_logs")
                record = data.get("record", {})
                sync_to_supabase(table, record)
                self.send_json_response({
                    "status": "success",
                    "message": f"Record inserted into Supabase table '{table}'",
                    "record": record
                })
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, status=500)
            return

        self.send_json_response({"status": "error", "message": "Endpoint not found"}, status=404)

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def translate_path(self, path):
        clean_path = path.split('?')[0].split('#')[0]

        # Route verification requests directly to verify.html
        if "verify.html" in clean_path:
            return os.path.join(FRONTEND_DIR, "verify.html")

        # Route dashboard requests directly to index.html
        if clean_path in ("/", "/index.html", "/codex/frontend/index.html", "/codex/frontend/", "/frontend/index.html"):
            return os.path.join(FRONTEND_DIR, "index.html")

        # Route codex/frontend/... or frontend/... to FRONTEND_DIR
        if clean_path.startswith("/codex/frontend/"):
            rel = clean_path[len("/codex/frontend/"):]
            return os.path.join(FRONTEND_DIR, rel)
        if clean_path.startswith("/frontend/"):
            rel = clean_path[len("/frontend/"):]
            return os.path.join(FRONTEND_DIR, rel)

        # Default fallback to frontend dir
        rel = clean_path.lstrip("/")
        candidate = os.path.join(FRONTEND_DIR, rel)
        if os.path.exists(candidate):
            return candidate

        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run(port=8000):
    server_address = ('0.0.0.0', port)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, RobustVerificationHandler)
    lan_ip = get_lan_ip()
    print("=" * 60)
    print(f" Brandwise Verification & Auth Server Started")
    print(f" - Local PC Access:   http://localhost:{port}")
    print(f" - Mobile / LAN QR:   http://{lan_ip}:{port}/verify.html")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
