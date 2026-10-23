import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'contracts/need_bank.py'
REPO = 'moorisi/need-bank'
RESOURCES = ['processor-units', 'storage-units']


def functions():
    names = {'integer', 'clone', 'compile_programs', 'remaining_need', 'safe_order', 'advance_candidate', 'abort_ledger', 'valid_observations'}
    tree = ast.parse(SOURCE.read_text())
    ns = {'json': json}
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names], type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


F = functions()


def address(value):
    return value.lower() if isinstance(value, str) else '0x' + value.hex()


def record(case='avoidance'):
    raw = (ROOT / 'fixtures' / (case + '.json')).read_bytes()
    return f'https://raw.githubusercontent.com/{REPO}/' + 'a' * 40 + f'/fixtures/{case}.json', hashlib.sha256(raw).hexdigest(), raw


def answer(case='avoidance'):
    value = json.loads((ROOT / 'tests' / (case + '-expected.json')).read_text())
    source = json.loads(record(case)[2])
    for job, original in zip(value['jobs'], source['jobs']):
        for step, text in zip(job['steps'], original['steps']): step['quote'] = text['text']
    return value


def capacity(case):
    return [2, 2] if case == 'reuse' else [3, 3]


def deploy(factory, accounts, case='avoidance', body=None, **kwargs):
    url, sha, raw = record(case)
    source = json.loads(raw)
    args = dict(repository=REPO, pool=case + '-pool', resources=RESOURCES, capacity=capacity(case),
                participants=[address(a) for a in accounts[:2]], jobs=[j['job'] for j in source['jobs']],
                steps=[[s['id'] for s in j['steps']] for j in source['jobs']], url=url,
                sha256=hashlib.sha256(body).hexdigest() if body is not None else sha)
    args.update(kwargs)
    return factory(str(SOURCE), **args)


def mocks(vm, case='avoidance', proposed=None, audit=None, body=None, status=200):
    vm.clear_mocks()
    url, _, raw = record(case)
    vm.mock_web(re.escape(url), {'status': status, 'body': raw if body is None else body})
    vm.mock_llm(r'.*NEEDBANK-EXTRACT.*', json.dumps(answer(case) if proposed is None else proposed))
    default_audit = {'jobs': [[True] * len(j['steps']) for j in answer(case)['jobs']]}
    vm.mock_llm(r'.*NEEDBANK-AUDIT.*', json.dumps(default_audit if audit is None else audit))


def compile_pool(c, vm, case='avoidance'):
    mocks(vm, case)
    c.compile()
    assert vm.run_validator() is True


def step(c, vm, accounts, job):
    vm.sender = accounts[job]
    preview = c.preview(job)
    before_events = c.get_state()['events']
    assert preview['verdict'] == 'ALLOWED'
    c.advance(job)
    state = c.get_state()
    assert state['ledger'] == preview['ledger']
    assert state['events'][:-1] == before_events
    assert state['events'][-1]['sender'] == address(accounts[job])
    return state


def conserved(state):
    ledger, config = state['ledger'], state['configuration']
    assert all(free >= 0 for free in ledger['free'])
    for r, cap in enumerate(config['capacity']):
        assert ledger['free'][r] + sum(a[r] for a in ledger['allocations']) == cap
    for i, status in enumerate(ledger['states']):
        if status in ['DONE', 'ABORTED']: assert ledger['allocations'][i] == [0] * len(config['resources'])
    if ledger['status'] == 'ACTIVE':
        assert F['safe_order'](state['compiled']['programs'], ledger) == ledger['safe_order']
