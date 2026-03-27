# Sentinel Batch Pipeline Guide

Welcome to the newly refactored Sentinel Multi-Vulnerability remediation system! This guide explains how to use the automated pipeline, what inputs it accepts, and what behaviors you should expect to see in the Frontend UI and Backend terminals.

## 1. How to Use the Frontend UI

With the recent updates, Sentinel has been simplified to require minimal user input while performing maximum testing.

**Input Required:**
- **Target File Path:** You only need to provide the absolute path to the Python file you want to test. 

**Example Inputs:**
- **Mega Vulnerable File (All-in-one):**
  `C:/Projects/Sentinel/sentinel_code/sandbox/mega_vulnerable.py`
  *(Contains SQL Injection, XSS, Path Traversal, and Insecure Deserialization)*
- **Single Vulnerability Files:**
  `C:/Projects/Sentinel/sentinel_code/sandbox/vulnerable_sql.py`
  `C:/Projects/Sentinel/sentinel_code/sandbox/vulnerable_xss.py`

*Note: The system automatically scans for **ALL** known vulnerability types (SQL, XSS, Path Traversal, Buffer Overflow, Command Injection, BOLA, XXE, SSRF, etc.) sequentially, so there is no longer a dropdown to select a specific type.*

## 2. What to Expect in the Frontend UI

Once you click **"Launch Sequence"**, the UI will transition to the **Live Dashboard**. Here is what you will see:

1. **Top Dashboard Metrics:**
   - **Iteration counter** tracking the pipeline's progress.
   - **Network Status** dynamically shifting from *Scanning* to *VULNERABLE* (if any exploits succeed) and eventually to *SECURE*.
   - **Verification Status** indicating the state of the final patch.

2. **Vulnerability Checklist (Left Panel):**
   - You will see a live-updating checklist of all 10+ vulnerability types. 
   - As the Red Agent systematically assaults your file, vulnerabilities will flash to either a green **SECURE** or a red **VULNERABLE** status.

3. **Proposed Patch (Right Panel):**
   - Once the Blue Agent generates a highly complex, consolidated patch fixing all discovered flaws simultaneously, the unified code diff will appear here.

4. **Live Operations Log (Bottom Panel):**
   - A scrolling terminal-like view displaying real-time telemetry from the Red, Blue, and Green agents indicating exactly which payloads are being fired and which validations are passing/failing.

## 3. What to Expect in the Terminals

If you are watching the backend terminal (`uvicorn app.main:app`), you will see the bare metal processes executing in the following sequence:

1. **Red Agent Audit:**
   The terminal will spit out line after line of different adversarial payloads hitting the auto-managed sandbox Flask server.
   - Example log: `Executing payloads (SQL) against ../sandbox/mega_vulnerable.py`
   - Example log: `Trying payload: ' OR '1'='1`
   - Example log: `Failed. Server Error...` or `Success! Found sensitive data.`

2. **Blue Agent Consolidation:**
   After the Red Agent finishes looping through every vulnerability, the Blue Agent engages. It will print its strategy, generating a unified LLM prompt detailing every single exploit that bypassed security.
   - Example log: `--- Blue Agent: Batch Patching ---`
   - Example log: `Using LLM to fix multiple vulnerabilities: SQL, XSS, DESERIALIZATION...`

3. **Green Agent Verification:**
   The terminal will fire up AST (Abstract Syntax Tree) logic to look for structurally unsafe constructs in the new patch. Then, the test harness will start up again to regression-test the patched file with the previous Red Agent exploits.
   - Example log: `Running AST Analysis...`
   - Example log: `AST Analysis PASSED.`
   - Example log: `Regression Test (SQL): PASS`
   - Example log: `Security Test (SQL): PASS (payload failed, effectively patched)`

If the Green Agent fully validates the patch in the terminal, the Frontend will unlock and display "REMEDIATED".
