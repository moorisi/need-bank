import copy
import itertools
import json
import random
from collections import deque
import pytest
from support import F, RESOURCES, answer, capacity


def initial(compiled, cap):
    n = len(compiled['programs'])
    ledger = dict(status='ACTIVE', cursors=[0] * n, allocations=[[0] * len(cap) for _ in range(n)],
                  states=['RUNNING'] * n, free=list(cap), safe_order=[])
    ledger['safe_order'] = F['safe_order'](compiled['programs'], ledger)
    return ledger


def permutation_oracle(programs, ledger):
    # Independent factorial enumeration, no greedy eligibility selection.
    jobs = [i for i, s in enumerate(ledger['states']) if s == 'RUNNING']
    for order in itertools.permutations(jobs):
        work = list(ledger['free'])
        valid = True
        for i in order:
            peak = programs[i]['remaining_peaks'][ledger['cursors'][i]]
            if any(peak[r] - ledger['allocations'][i][r] > work[r] for r in range(len(work))):
                valid = False
                break
            for r in range(len(work)): work[r] += ledger['allocations'][i][r]
        if valid: return list(order)
    return None


def independent_step(programs, ledger, job):
    following = copy.deepcopy(ledger)
    operation = programs[job]['operations'][ledger['cursors'][job]]
    sign = 1 if operation['operation'] == 'ACQUIRE' else -1
    changes = [sign * x for x in operation['units']]
    if any(delta > free for delta, free in zip(changes, ledger['free'])): return {'verdict': 'INSUFFICIENT', 'ledger': None}
    following['free'] = [free - delta for free, delta in zip(ledger['free'], changes)]
    following['allocations'][job] = [held + delta for held, delta in zip(ledger['allocations'][job], changes)]
    following['cursors'][job] += 1
    if following['cursors'][job] == len(programs[job]['operations']): following['states'][job] = 'DONE'
    order = permutation_oracle(programs, following)
    if order is None: return {'verdict': 'UNSAFE', 'ledger': None}
    following['safe_order'] = order
    following['status'] = 'ACTIVE' if 'RUNNING' in following['states'] else 'COMPLETE'
    return {'verdict': 'ALLOWED', 'ledger': following}


@pytest.mark.parametrize('case,status', [('avoidance', 'ACTIVE'), ('reuse', 'ACTIVE'), ('review', 'REVIEW'), ('blocked', 'BLOCKED')])
def test_fixed_source_program_compilation(case, status):
    compiled = F['compile_programs'](answer(case), RESOURCES, capacity(case))
    assert compiled['status'] == status
    if status == 'REVIEW': assert compiled['reason'] == {'kind': 'UNKNOWN_STEPS', 'steps': [['job-amber', 'step-1']]}
    if status == 'BLOCKED': assert compiled['reason'] == {'kind': 'OVER_CAPACITY', 'job': 'job-amber', 'step': 'step-1'}
    for program in compiled['programs']:
        for p, peak in enumerate(program['remaining_peaks']):
            assert peak == [max(h[r] for h in program['holdings'][p:]) for r in range(2)]
        assert program['holdings'][0] == program['holdings'][-1] == [0, 0]


def test_all_small_two_job_two_resource_states_against_permutations():
    checked = 0
    for cap in itertools.product([1, 2], repeat=2):
        vectors = list(itertools.product(*(range(c + 1) for c in cap)))
        for maxima in itertools.product(vectors, repeat=2):
            for allocations in itertools.product(*[list(itertools.product(*(range(x + 1) for x in m))) for m in maxima]):
                free = [cap[r] - sum(a[r] for a in allocations) for r in range(2)]
                if min(free) < 0: continue
                programs = [{'remaining_peaks': [list(m)]} for m in maxima]
                ledger = dict(free=free, states=['RUNNING'] * 2, cursors=[0, 0], allocations=[list(a) for a in allocations])
                assert F['safe_order'](programs, ledger) == permutation_oracle(programs, ledger)
                checked += 1
    assert checked == 1521


def test_256_generated_four_job_three_resource_states():
    rng = random.Random(7741)
    for _ in range(256):
        cap = [rng.randrange(1, 5) for _ in range(3)]
        allocations = [[0, 0, 0] for _ in range(4)]
        for r in range(3):
            for _ in range(rng.randrange(cap[r] + 1)): allocations[rng.randrange(4)][r] += 1
        maxima = [[rng.randrange(a[r], cap[r] + 1) for r in range(3)] for a in allocations]
        ledger = dict(free=[cap[r] - sum(a[r] for a in allocations) for r in range(3)],
                      states=['RUNNING'] * 4, cursors=[0] * 4, allocations=allocations)
        programs = [{'remaining_peaks': [m]} for m in maxima]
        assert F['safe_order'](programs, ledger) == permutation_oracle(programs, ledger)


@pytest.mark.parametrize('case', ['avoidance', 'reuse'])
def test_every_reachable_prefix_with_signed_advance_or_abort(case):
    compiled = F['compile_programs'](answer(case), RESOURCES, capacity(case))
    programs, cap = compiled['programs'], capacity(case)
    queue, seen = deque([initial(compiled, cap)]), set()
    while queue:
        ledger = queue.popleft()
        key = json.dumps(ledger, sort_keys=True)
        if key in seen: continue
        seen.add(key)
        assert ledger['safe_order'] == permutation_oracle(programs, ledger)
        for r in range(2):
            assert ledger['free'][r] >= 0
            assert ledger['free'][r] + sum(a[r] for a in ledger['allocations']) == cap[r]
        for job, state in enumerate(ledger['states']):
            if state != 'RUNNING':
                assert ledger['allocations'][job] == [0, 0]
                continue
            candidate = F['advance_candidate'](programs, ledger, job)
            assert candidate == independent_step(programs, ledger, job)
            if candidate['verdict'] == 'ALLOWED': queue.append(candidate['ledger'])
            aborted = F['abort_ledger'](programs, ledger, job)
            assert aborted['safe_order'] is not None and aborted['allocations'][job] == [0, 0]
            queue.append(aborted)
    assert len(seen) > 20


def test_zero_holding_job_cannot_fictitiously_release_its_maximum_claim():
    programs = [{'remaining_peaks': [[2, 2]]}, {'remaining_peaks': [[2, 2]]}, {'remaining_peaks': [[1, 1]]}]
    ledger = dict(free=[1, 1], cursors=[0] * 3, states=['RUNNING'] * 3, allocations=[[2, 0], [0, 2], [0, 0]])
    assert F['safe_order'](programs, ledger) is None
    assert permutation_oracle(programs, ledger) is None


def test_sufficient_free_units_can_still_be_unsafe():
    compiled = F['compile_programs'](answer(), RESOURCES, [3, 3])
    ledger = F['advance_candidate'](compiled['programs'], initial(compiled, [3, 3]), 0)['ledger']
    assert ledger['free'] == [1, 3]
    assert compiled['programs'][1]['operations'][0]['units'] == [0, 2]
    assert F['advance_candidate'](compiled['programs'], ledger, 1) == {'verdict': 'UNSAFE', 'ledger': None}


@pytest.mark.parametrize('kind', ['OVER_RELEASE', 'UNRETURNED_UNITS'])
def test_definite_invalid_plan_is_blocked_without_rewriting(kind):
    observations = answer()
    if kind == 'OVER_RELEASE': observations['jobs'][0]['steps'][0].update(operation='RELEASE')
    else: observations['jobs'][0]['steps'][-1]['units'] = [1, 2]
    compiled = F['compile_programs'](observations, RESOURCES, [3, 3])
    assert compiled['status'] == 'BLOCKED' and compiled['reason']['kind'] == kind
    assert compiled['programs'] == []


def test_released_historical_peak_is_not_a_future_claim():
    compiled = F['compile_programs'](answer('reuse'), RESOURCES, [2, 2])
    programs = compiled['programs']
    assert programs[0]['remaining_peaks'] == [[2, 1], [2, 1], [0, 1], [0, 1], [0, 0]]
    ledger = initial(compiled, [2, 2])
    for job in [0, 0, 0, 1]:
        candidate = F['advance_candidate'](programs, ledger, job)
        assert candidate['verdict'] == 'ALLOWED'
        ledger = candidate['ledger']
    assert ledger['allocations'] == [[0, 1], [2, 0]] and ledger['free'] == [0, 1]
    assert ledger['safe_order'] == [0, 1]
    obsolete = copy.deepcopy(programs)
    for i, p in enumerate(obsolete): p['remaining_peaks'] = [p['remaining_peaks'][0]] * len(p['remaining_peaks'])
    assert F['safe_order'](obsolete, ledger) is None
