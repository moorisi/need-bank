import copy
import json
import pytest
from support import F, RESOURCES, address, answer, capacity, compile_pool, conserved, deploy, mocks, record, step


def test_unsafe_acquisition_then_full_completion(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts)
    before = c.get_state()
    direct_vm.sender = direct_accounts[0]
    with direct_vm.expect_revert('Pool not active'): c.advance(0)
    assert c.get_state() == before
    direct_vm.sender = direct_accounts[3]
    compile_pool(c, direct_vm)
    assert c.get_state()['events'][0]['sender'] == address(direct_accounts[3])
    state = step(c, direct_vm, direct_accounts, 0)
    conserved(state)
    assert state['ledger']['free'] == [1, 3]
    assert c.preview(1) == {'verdict': 'UNSAFE', 'ledger': None}
    direct_vm.sender = direct_accounts[1]
    with direct_vm.expect_revert('Unsafe remaining claims'): c.advance(1)
    assert c.get_state() == state
    for job in [0, 0, 1, 1, 1]: conserved(step(c, direct_vm, direct_accounts, job))
    final = c.get_state()
    assert final['ledger']['status'] == 'COMPLETE'
    assert final['ledger']['states'] == ['DONE', 'DONE']
    assert final['ledger']['free'] == [3, 3]
    assert len(final['events']) == 7
    with direct_vm.expect_revert('Pool not active'): c.advance(1)
    assert c.get_state() == final


def test_release_past_peak_and_abort_return_actual_holding(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts, 'reuse')
    compile_pool(c, direct_vm, 'reuse')
    state = step(c, direct_vm, direct_accounts, 0)
    direct_vm.sender = direct_accounts[1]
    assert c.preview(1)['verdict'] == 'INSUFFICIENT'
    with direct_vm.expect_revert('Insufficient free units'): c.advance(1)
    assert c.get_state() == state
    for job in [0, 0, 1]: conserved(step(c, direct_vm, direct_accounts, job))
    state = c.get_state()
    assert state['ledger']['allocations'] == [[0, 1], [2, 0]]
    assert state['ledger']['free'] == [0, 1] and state['ledger']['safe_order'] == [0, 1]
    direct_vm.sender = direct_accounts[0]
    with direct_vm.expect_revert('Only job participant'): c.abort(1)
    assert c.get_state() == state
    direct_vm.sender = direct_accounts[1]
    c.abort(1)
    state = c.get_state(); conserved(state)
    assert state['ledger']['free'] == [2, 1]
    assert state['ledger']['states'] == ['RUNNING', 'ABORTED']
    assert state['events'][-1]['units'] == [2, 0]
    with direct_vm.expect_revert('Job not running'): c.advance(1)
    with direct_vm.expect_revert('Job not running'): c.abort(1)
    assert c.get_state() == state
    final = step(c, direct_vm, direct_accounts, 0); conserved(final)
    assert final['ledger']['status'] == 'COMPLETE' and final['ledger']['free'] == [2, 2]


def test_abort_before_borrowing_and_preview_are_permissionless(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts)
    compile_pool(c, direct_vm)
    before = c.get_state()
    direct_vm.sender = direct_accounts[4]
    assert c.preview(0)['verdict'] == 'ALLOWED'
    assert c.get_state() == before
    direct_vm.sender = direct_accounts[0]
    c.abort(0)
    state = c.get_state(); conserved(state)
    assert state['ledger']['free'] == [3, 3] and state['events'][-1]['units'] == [0, 0]
    assert c.preview(0)['verdict'] == 'TERMINAL'
    direct_vm.sender = direct_accounts[1]
    c.abort(1)
    final = c.get_state(); conserved(final)
    assert final['ledger']['status'] == 'COMPLETE' and final['ledger']['safe_order'] == []


@pytest.mark.parametrize('method', ['advance', 'abort'])
def test_cannot_control_other_participant(direct_deploy, direct_vm, direct_accounts, method):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    before = c.get_state()
    direct_vm.sender = direct_accounts[4]
    with direct_vm.expect_revert('Only job participant'): getattr(c, method)(0)
    assert c.get_state() == before


@pytest.mark.parametrize('case,status', [('review', 'REVIEW'), ('blocked', 'BLOCKED')])
def test_unknown_and_impossible_runbooks_disable_pool(direct_deploy, direct_vm, direct_accounts, case, status):
    c = deploy(direct_deploy, direct_accounts, case); compile_pool(c, direct_vm, case)
    before = c.get_state()
    assert before['compiled']['status'] == before['ledger']['status'] == status
    assert before['ledger']['free'] == capacity(case) and before['ledger']['allocations'] == [[0, 0], [0, 0]]
    assert before['compiled']['programs'] == [] and len(before['events']) == 1
    for i in range(2):
        direct_vm.sender = direct_accounts[i]
        assert c.preview(i) == {'verdict': 'DISABLED', 'ledger': None}
        with direct_vm.expect_revert('Pool not active'): c.advance(i)
        with direct_vm.expect_revert('Pool not active'): c.abort(i)
        assert c.get_state() == before


def test_compile_cannot_reinterpret_after_progress(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    step(c, direct_vm, direct_accounts, 0)
    before = c.get_state()
    with direct_vm.expect_revert('Runbook already compiled'): c.compile()
    assert c.get_state() == before


def test_native_abi_address_participants(direct_deploy, direct_vm, direct_accounts, monkeypatch):
    from gltest.direct import loader
    original = loader._calldata_roundtrip_args
    def cli_address_autodetection(args, kwargs):
        from genlayer import Address
        if 'participants' in kwargs:
            kwargs = dict(kwargs, participants=[Address(p) for p in kwargs['participants']])
        return original(args, kwargs)
    monkeypatch.setattr(loader, '_calldata_roundtrip_args', cli_address_autodetection)
    c = deploy(direct_deploy, direct_accounts)
    assert c.get_state()['configuration']['participants'] == [address(a) for a in direct_accounts[:2]]
    compile_pool(c, direct_vm)
    conserved(step(c, direct_vm, direct_accounts, 0))


@pytest.mark.parametrize('job', [-1, 2, True])
def test_index_bounds(direct_deploy, direct_vm, direct_accounts, job):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    before = c.get_state()
    for method in ['advance', 'abort', 'preview']:
        with direct_vm.expect_revert('Unknown job'): getattr(c, method)(job)
        assert c.get_state() == before


@pytest.mark.parametrize('field,value', [('operation', 'RELEASE'), ('operation', 'UNKNOWN'), ('units', [1, 0]), ('units', [2, 1])])
def test_independent_validator_checks_operation_and_each_quantity(direct_deploy, direct_vm, direct_accounts, field, value):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    proposed = answer(); row = proposed['jobs'][0]['steps'][0]; row[field] = value
    if value == 'UNKNOWN': row['units'] = [0, 0]
    mocks(direct_vm, proposed=proposed)
    assert direct_vm.run_validator() is False


def test_unknown_cannot_be_replaced_with_convenient_definite_claim(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts, 'review'); compile_pool(c, direct_vm, 'review')
    proposed = answer('review'); proposed['jobs'][0]['steps'][0].update(operation='ACQUIRE', units=[2, 0])
    mocks(direct_vm, 'review', proposed=proposed)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('audit', [{'jobs': [[False, True, True], [True] * 3]}, {'jobs': [[True] * 3]}, {'jobs': [[1] * 3] * 2}, {'jobs': [[True] * 3] * 2, 'extra': True}])
def test_every_step_requires_full_source_audit(direct_deploy, direct_vm, direct_accounts, audit):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    mocks(direct_vm, audit=audit)
    assert direct_vm.run_validator() is False


def test_quote_wording_can_differ_but_substance_cannot(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    own = answer(); own['jobs'][0]['steps'][0]['quote'] = 'The operative step instead borrows two processor units from the pool'
    mocks(direct_vm, proposed=own)
    assert direct_vm.run_validator() is True


def test_validator_refetches_full_committed_runbook(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    mocks(direct_vm, body=b'{}')
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('change', ['missing-job', 'missing-step', 'reordered', 'invented-quote', 'wrong-quote', 'bool', 'null', 'extra', 'zero-definite', 'nonzero-unknown', 'negative', 'too-many'])
def test_bad_model_output_rolls_back_every_storage_field(direct_deploy, direct_vm, direct_accounts, change):
    c = deploy(direct_deploy, direct_accounts); proposed = answer(); row = proposed['jobs'][0]['steps'][0]
    if change == 'missing-job': proposed['jobs'].pop()
    elif change == 'missing-step': proposed['jobs'][0]['steps'].pop()
    elif change == 'reordered': proposed['jobs'][0]['steps'].reverse()
    elif change == 'invented-quote': row['quote'] = 'This sentence is fabricated and appears nowhere in the source.'
    elif change == 'wrong-quote': row['quote'] = proposed['jobs'][1]['steps'][0]['quote']
    elif change == 'bool': row['units'] = [True, 0]
    elif change == 'null': row['units'] = None
    elif change == 'extra': row['confidence'] = 1
    elif change == 'zero-definite': row['units'] = [0, 0]
    elif change == 'nonzero-unknown': row['operation'] = 'UNKNOWN'
    elif change == 'negative': row['units'] = [-1, 0]
    else: row['units'] = [17, 0]
    mocks(direct_vm, proposed=proposed); before = c.get_state()
    with direct_vm.expect_revert('Invalid complete instructions'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('change', ['scope', 'job-roster', 'step-roster', 'missing-step', 'schema', 'duplicate', 'utf8', 'invalid-json', 'oversized'])
def test_committed_invalid_source_is_rejected(direct_deploy, direct_vm, direct_accounts, change):
    source = json.loads(record()[2])
    if change == 'scope': source['pool'] = 'other-pool'
    elif change == 'job-roster': source['jobs'][0]['job'] = 'other-job'
    elif change == 'step-roster': source['jobs'][0]['steps'][0]['id'] = 'step-99'
    elif change == 'missing-step': source['jobs'][0]['steps'].pop()
    elif change == 'schema': source['jobs'][0]['steps'][0]['extra'] = True
    elif change == 'oversized': source['jobs'][0]['steps'][0]['text'] = 'x' * 25000
    raw = json.dumps(source).encode()
    if change == 'duplicate': raw = b'{"pool":"one","pool":"two"}'
    elif change == 'utf8': raw = bytes([255])
    elif change == 'invalid-json': raw = b'{'
    c = deploy(direct_deploy, direct_accounts, body=raw); mocks(direct_vm, body=raw)
    before = c.get_state()
    with direct_vm.expect_revert('[EXTERNAL]'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('status', [404, 500])
def test_matching_external_or_transient_error_callback(direct_deploy, direct_vm, direct_accounts, status):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    mocks(direct_vm, status=status)
    message = '[EXTERNAL] Runbook commitment mismatch' if status == 404 else '[TRANSIENT] Runbook unavailable'
    assert direct_vm.run_validator(leader_error=Exception(message)) is True
    assert direct_vm.run_validator() is False


def test_llm_error_never_agrees(direct_deploy, direct_vm, direct_accounts):
    c = deploy(direct_deploy, direct_accounts); compile_pool(c, direct_vm)
    mocks(direct_vm, proposed={})
    assert direct_vm.run_validator(leader_error=Exception('[LLM_ERROR] Invalid complete instructions')) is False


@pytest.mark.parametrize('kwargs', [
    {'repository': '../bad'}, {'pool': '../bad'}, {'resources': ['processor-units']},
    {'resources': ['processor-units', 'processor-units']}, {'capacity': [0, 3]}, {'capacity': [True, 3]},
    {'capacity': [13, 3]}, {'jobs': []}, {'participants': ['0x' + '0' * 40, '0x' + '1' * 40]},
    {'participants': ['0x' + '1' * 40] * 2}, {'steps': [['step-1', 'step-1']] * 2},
    {'url': 'https://example.com/runbook'}, {'url': 'https://raw.githubusercontent.com/moorisi/need-bank/main/fixtures/avoidance.json'},
    {'sha256': 'a' * 63},
])
def test_constructor_rejects_unbounded_or_mutable_inputs(direct_deploy, direct_vm, direct_accounts, kwargs):
    with direct_vm.expect_revert('[EXPECTED]'): deploy(direct_deploy, direct_accounts, **kwargs)
