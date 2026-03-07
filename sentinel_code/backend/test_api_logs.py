from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import run_workflow, workflow_store
from app.models.state import RemediationState
import uuid
import os


def test_status_includes_logging_events():
    """Ensure that the status endpoint returns the structured log events generated
    during a workflow run.  The test invokes the workflow synchronously and then
    queries the HTTP API to verify the log payload."""
    # pick a simple vulnerability file that exists in repo
    code_file = os.path.join(os.path.dirname(__file__), "..", "..", "vulnerabilities", "5_insecure_deserialization.py")

    workflow_id = str(uuid.uuid4())
    initial_state = RemediationState(
        code_path=code_file,
        vulnerability_type="DESERIALIZATION",
        iteration_count=0,
    )
    # attach id so agents will record events
    initial_state.workflow_id = workflow_id
    # prepopulate store just like start_remediation would
    workflow_store[workflow_id] = initial_state

    # run the workflow synchronously (skips background tasks)
    run_workflow(workflow_id, initial_state)

    client = TestClient(app)
    resp = client.get(f"/api/status/{workflow_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "state" in data
    assert "logs" in data
    logs = data["logs"]
    assert logs.get("workflow_id") == workflow_id
    assert isinstance(logs.get("events"), list)
    assert len(logs["events"]) > 0
    # check that each event has the expected keys
    for ev in logs["events"]:
        assert "timestamp" in ev and "agent" in ev and "action" in ev
