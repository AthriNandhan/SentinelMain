from app.agents.blue_agent import blue_agent
from app.models.state import RemediationState

state = RemediationState(
    code_path='../sandbox/vulnerable_code.py',
    vulnerability_type='SQL Injection',
    exploit_success=True,
    exploit_payloads=['admin\' --'],
    iteration_count=0
)

result = blue_agent(state)
print('Blue Agent Result:')
print('Has parameterized query fix:', 'cursor.execute(query, params)' in result.patch_diff)
print('Patch length:', len(result.patch_diff))
print('First 500 chars:')
print(result.patch_diff[:500])
