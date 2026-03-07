# Test that agent-generated logs reach the frontend via status API

Test flow:
1. Backend receives remediation request via POST /api/remediate
2. Starts workflow in background task with a workflow_id
3. Each agent calls logger.log_and_print() which:
   - Prints to stdout (visible in terminal)
   - Records event in workflow log file (logs/{workflow_id}.json)
4. Frontend polls GET /api/status/{workflow_id}
5. Response includes logs.events array with all timestamped agent actions
6. Frontend renders events in "Live Operations Log" panel

Changes made:
- Added workflow_id field to RemediationState
- Added log_and_print() helper to WorkflowLogger
- Updated all 3 agents (red, blue, green) to use logger.log_and_print()
- run_workflow() assigns workflow_id to state
- /status endpoint already returns logs, frontend already uses them

Result: All backend terminal output now visible in frontend's live log panel.
