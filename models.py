from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class Proc:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)
    first_start: Optional[int] = None
    completion: Optional[int] = None

    def __post_init__(self):
        self.remaining = int(self.burst)


def deep_copy(procs: List[Proc]) -> List[Proc]:
    return [Proc(p.pid, int(p.arrival), int(p.burst)) for p in procs]


def compute_metrics(procs: List[Proc]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}

    for p in procs:
        if p.completion is None:
            continue

        tat = p.completion - p.arrival
        wait = tat - p.burst
        resp = (p.first_start - p.arrival) if p.first_start is not None else 0

        out[p.pid] = {
            "waiting": wait,
            "turnaround": tat,
            "response": resp,
            "completion": p.completion,
        }

    return out
