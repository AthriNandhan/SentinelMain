import sqlite3
import os
import importlib.util
import sys
import json

import os
import sys
import json
import time
import shutil
import requests
import subprocess

class TestHarness:
    def __init__(self):
        self.flag = "SECRET_FLAG_DATA_123"
        self.server_process = None
        self.sandbox_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sandbox"))
        self.backup_path = os.path.join(self.sandbox_dir, "vulnerable_code.py.bak")
        self.target_code_path = os.path.join(self.sandbox_dir, "vulnerable_code.py")
        self.server_url = "http://localhost:5000/analyze"

    def start_server(self, code_path: str = None, code_content: str = None):
        """Starts the Flask app in a subprocess. Replaces vulnerable_code.py if code requested."""
        if not os.path.exists(self.backup_path):
            shutil.copyfile(self.target_code_path, self.backup_path)

        if code_path and os.path.exists(code_path) and os.path.abspath(code_path) != self.target_code_path:
            shutil.copyfile(code_path, self.target_code_path)
        elif code_content:
            with open(self.target_code_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            # Ensure file is fully flushed to disk
            time.sleep(0.5)
        
        # Wait a bit longer for port to be released from previous server
        time.sleep(0.5)
        
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['PYTHONUNBUFFERED'] = '1'
        
        print("Starting Flask server...")
        self.server_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=self.sandbox_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait and retry for server startup
        max_retries = 10
        retry_count = 0
        server_ready = False
        
        while retry_count < max_retries and not server_ready:
            time.sleep(1)
            
            # Check if process has died
            if self.server_process.poll() is not None:
                try:
                    stdout_output = self.server_process.stdout.read() if self.server_process.stdout else "(no output)"
                except:
                    stdout_output = "(could not read output)"
                print(f"ERROR: Flask process exited unexpectedly!")
                print(f"Server output:\n{stdout_output}")
                raise RuntimeError(f"Flask server failed to start. Output: {stdout_output}")
            
            try:
                response = requests.post(
                    self.server_url, 
                    json={"username": "alice", "request_id": "ping"}, 
                    timeout=2
                )
                server_ready = True
                print("Flask server is up and responding!")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                retry_count += 1
                print(f"Waiting for server... ({retry_count}/{max_retries})")
        
        if not server_ready:
            # Try to kill the process and read output
            if self.server_process:
                self.server_process.terminate()
                try:
                    stdout_output, _ = self.server_process.communicate(timeout=2)
                    print(f"Server output:\n{stdout_output}")
                except Exception as e:
                    print(f"Could not retrieve server output: {e}")
            raise RuntimeError(f"Flask server did not start after {max_retries} attempts")

    def stop_server(self):
        """Stops the Flask app and restores original vulnerable code."""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                try:
                    self.server_process.wait(timeout=2)
                except:
                    pass
            self.server_process = None
            # Wait for port to be released
            time.sleep(1.5)
            
        if os.path.exists(self.backup_path):
            try:
                shutil.move(self.backup_path, self.target_code_path)
            except Exception as e:
                print(f"Warning: Could not restore backup: {e}")
                # If move fails, try to remove and copy instead
                try:
                    os.remove(self.target_code_path)
                    shutil.copy(self.backup_path, self.target_code_path)
                    os.remove(self.backup_path)
                except:
                    pass

    def run_attack(self, payload, code_path: str = None, vuln_type: str = "SQL") -> dict:
        """
        Runs the attack using the given payload with retry logic.
        Payload may be a string or dictionary depending on vulnerability type.
        If the server isn't running, it starts it briefly for this attack.
        """
        manage_server = False
        if not self.server_process:
            manage_server = True
            self.start_server(code_path=code_path)
            
        result = {"success": False, "data": None, "error": None}
        
        def build_input(p):
            # if we've already been given a dict, just use it
            if isinstance(p, dict):
                return p
            # build input payloads according to the vulnerability type
            if vuln_type == "SQL":
                return {"username": p, "request_id": "test_run_1"}
            elif vuln_type == "XSS":
                return {"comment": p}
            elif vuln_type == "PATH_TRAVERSAL":
                return {"filename": p}
            elif vuln_type == "BUFFER_OVERFLOW":
                return {"input": p}
            elif vuln_type == "INFO_EXPOSURE":
                # some vulnerabilities expect both a key and data field
                return {"key": "test", "data": p}
            elif vuln_type == "XXE":
                # pass xml string inside a JSON object so the server will dump it to a string
                return {"xml": p}
            elif vuln_type == "SSRF":
                return {"url": p}
            elif vuln_type == "INSECURE_RANDOMNESS":
                # include a dummy user_id for token generation
                return {"user_id": 1, "data": p}
            elif vuln_type == "RACE_CONDITION":
                # additional fields are accepted by the vulnerable function
                return {"data": p}
            elif vuln_type == "BOLA":
                # the payloads in config are already JSON strings
                try:
                    return json.loads(p)
                except Exception:
                    return {"data": p}
            elif vuln_type == "HARDCODED_SECRETS":
                return {"data": p}
            elif vuln_type == "DESERIALIZATION":
                return {"session_data": p}
            else:
                return {"data": p}
        
        try:
            # Retry logic for sending the attack
            max_attack_retries = 3
            for attempt in range(max_attack_retries):
                try:
                    input_data = build_input(payload)
                    response = requests.post(self.server_url, json=input_data, timeout=5)
                    
                    try:
                        res_json = response.json()
                    except ValueError:
                        result["error"] = f"Invalid JSON response. Status: {response.status_code}, Text: {response.text}"
                        return result
                        
                    data = res_json.get("data")
                    status = res_json.get("status")
                    
                    if status == "success" and data:
                        result["data"] = str(data)
                        if self.flag and self.flag in str(data):
                            result["success"] = True
                    elif status == "error":
                        result["error"] = res_json.get("error", "Unknown server error")
                    
                    return result
                    
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    if attempt < max_attack_retries - 1:
                        print(f"Attack attempt {attempt + 1} failed, retrying... ({str(e)[:50]})")
                        time.sleep(1)
                    else:
                        result["error"] = f"Failed to execute attack after {max_attack_retries} attempts: {str(e)}"
                except Exception as e:
                    result["error"] = str(e)
                    break
        finally:
            if manage_server:
                self.stop_server()
                
        return result

    def verify_fix(self, code_content: str, security_payloads: list = None, vuln_type: str = "SQL") -> dict:
        """
        Verifies the fix by running:
        1. Regression test (valid user/normal input)
        2. Security test (ensure Red Agent's payloads fail)
        """
        results = {
            "regression_passed": False,
            "security_passed": False,
            "details": []
        }
        
        # choose a normal payload based on vulnerability type
        normal_inputs = {
            "SQL": "alice",
            "XSS": "Hello world",
            "PATH_TRAVERSAL": "data.txt",
            "BUFFER_OVERFLOW": "safe"
        }
        normal_payload = normal_inputs.get(vuln_type, "test")
        
        try:
            self.start_server(code_content=code_content)
            
            # 1. Regression Test: Normal input
            res_normal = self.run_attack(normal_payload, vuln_type=vuln_type)
            # heuristic check for expected return
            if res_normal.get("data"):
                results["regression_passed"] = True
                results["details"].append("Regression Test: PASS (Normal input returned data)")
            else:
                results["details"].append(f"Regression Test: FAIL (No normal data: {res_normal.get('data')} | Error: {res_normal.get('error')})")

            # 2. Security Test: Re-run attacks
            if not security_payloads:
                security_payloads = ["' OR '1'='1"]
            
            # run each security payload
            for payload in security_payloads:
                res_attack = self.run_attack(payload, vuln_type=vuln_type)
                if res_attack.get("success"):
                    results["details"].append(f"Security Test: FAIL (payload {payload} succeeded with data {res_attack.get('data')})")
                    results["security_passed"] = False
                    break
            else:
                results["security_passed"] = True
                results["details"].append("Security Test: PASS (no payload succeeded)")
                
        finally:
            self.stop_server()
                
        return results

test_harness = TestHarness()

