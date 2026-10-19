"""Point-in-time data, capacity arithmetic and deterministic tool control.

This is an in-memory teaching model. It does not provide durable transactions,
real authentication, network calls, a production service or an autonomous agent.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_time: int
    available_time: int
    value: float


def observed_total(events, decision_time):
    return sum(e.value for e in events
               if e.event_time <= decision_time and e.available_time <= decision_time)


def kv_bytes(layers, positions, kv_heads, head_width, bytes_per_value=2, batch=1):
    sizes = [layers, positions, kv_heads, head_width, bytes_per_value, batch]
    if any(not isinstance(x, int) or x <= 0 for x in sizes):
        raise ValueError('positive integer dimensions required')
    return 2*layers*positions*kv_heads*head_width*bytes_per_value*batch


def cache_key(tenant, policy_version, model_version, index_version, query):
    return (tenant, policy_version, model_version, index_version, query)


class Workflow:
    """Trusted deterministic state/allowlist boundary; callers must authenticate upstream."""
    allowed = {'lookup', 'draft'}

    def __init__(self, budget=4):
        if budget < 1:
            raise ValueError('positive step budget required')
        self.budget = budget
        self.steps = 0
        self.effects = {}
        self.audit = []

    def call(self, action, arguments, operation_id):
        if action not in self.allowed:
            raise PermissionError('tool not allowlisted')
        if not isinstance(arguments, dict) or set(arguments) != {'incident_id'}:
            raise ValueError('expected incident_id only')
        incident_id = arguments['incident_id']
        if not isinstance(incident_id, str) or not incident_id.isdecimal():
            raise ValueError('incident_id must be a numeric string')
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError('operation ID required')
        payload = (action, incident_id)
        if operation_id in self.effects:
            previous, result = self.effects[operation_id]
            if previous != payload:
                raise ValueError('operation ID reused with a different payload')
            return result
        if self.steps >= self.budget:
            raise RuntimeError('step budget exhausted')
        self.steps += 1
        result = {'action': action, 'incident_id': incident_id, 'status': 'simulated'}
        self.effects[operation_id] = (payload, result)
        self.audit.append((operation_id, action, incident_id))
        return result


def main():
    events = [Event(8,9,5), Event(7,12,100), Event(11,11,20)]
    print('point-in-time total at t=10 =', observed_total(events, 10))
    print('event-time-only (leaky) total =', sum(e.value for e in events if e.event_time <= 10))
    size = kv_bytes(32,4096,8,128)
    print('KV bytes / GiB =', size, size/2**30)
    print('weight GB / GiB =', 7e9*2/1e9, 7e9*2/2**30)
    workflow = Workflow(budget=2)
    print('lookup =', workflow.call('lookup', {'incident_id':'42'}, 'op1'))
    workflow.call('lookup', {'incident_id':'42'}, 'op1')
    workflow.call('draft', {'incident_id':'42'}, 'op2')
    print('effects after retry =', len(workflow.effects), 'audit =', workflow.audit)
    try:
        workflow.call('restart_server', {'incident_id':'42'}, 'op3')
    except PermissionError as error:
        print('forbidden tool rejected =', str(error))
    try:
        workflow.call('lookup', {'incident_id':'43'}, 'op3')
    except RuntimeError as error:
        print('budget stop =', str(error))
    print('error budget failures =', int((1-.999)*1_000_000))


if __name__ == '__main__':
    main()
