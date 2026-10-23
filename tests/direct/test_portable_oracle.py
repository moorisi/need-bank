import json
import subprocess
import pytest
from support import ROOT, address, deploy, mocks


@pytest.mark.parametrize('case', ['avoidance', 'reuse', 'review', 'blocked'])
def test_actual_vm_trace_matches_independent_live_oracle(direct_deploy, direct_vm, direct_accounts, case):
    accounts = [address(a) for a in direct_accounts[:4]]
    planned = subprocess.run(['node', '-e', "console.log(JSON.stringify(require('./scripts/scenario.cjs').plan(process.argv[1])))", case], cwd=ROOT, check=True, text=True, capture_output=True)
    items = json.loads(planned.stdout)
    c = deploy(direct_deploy, direct_accounts, case)
    mocks(direct_vm, case)
    trace = []
    for item in items:
        direct_vm.sender = direct_accounts[item['caller']]
        before = c.get_state()
        entry = {'before': before}
        if item['method'] == 'advance': entry['preview'] = c.preview(item['args'][0])
        if 'error' in item:
            with direct_vm.expect_revert(item['error']): getattr(c, item['method'])(*item['args'])
        else:
            getattr(c, item['method'])(*item['args'])
            if item['method'] == 'compile': assert direct_vm.run_validator() is True
        entry['after'] = c.get_state()
        trace.append(entry)
    checked = subprocess.run(['node', 'scripts/check-local-trace.cjs'], cwd=ROOT, input=json.dumps({'id': case, 'accounts': accounts, 'trace': trace}), text=True, capture_output=True)
    assert checked.returncode == 0, checked.stderr
