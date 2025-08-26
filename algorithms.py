from typing import List, Tuple
from models import Proc, deep_copy


def schedule_fcfs(procs: List[Proc]) -> Tuple[List[Tuple[int, int, str]], List[Proc]]:
    ps = deep_copy(procs)
    ps.sort(key=lambda p: (p.arrival, p.pid))

    t = 0
    tl: List[Tuple[int, int, str]] = []

    for p in ps:
        if t < p.arrival:
            tl.append((t, p.arrival, "IDLE"))
            t = p.arrival

        p.first_start = t
        s = t
        t += p.burst
        p.remaining = 0
        p.completion = t

        tl.append((s, t, p.pid))

    return tl, ps


def schedule_rr(procs: List[Proc], q: int = 2) -> Tuple[List[Tuple[int, int, str]], List[Proc]]:
    if q <= 0:
        q = 1

    ps = deep_copy(procs)
    t = 0
    tl: List[Tuple[int, int, str]] = []

    arr = sorted(ps, key=lambda p: (p.arrival, p.pid))
    i = 0
    rq: List[int] = []
    n = len(ps)
    fin = 0
    idx = {p.pid: k for k, p in enumerate(ps)}

    while fin < n:
        while i < n and arr[i].arrival <= t:
            rq.append(idx[arr[i].pid])
            i += 1

        if not rq:
            if i < n and t < arr[i].arrival:
                tl.append((t, arr[i].arrival, "IDLE"))
                t = arr[i].arrival
                continue
            else:
                break

        j = rq.pop(0)
        p = ps[j]

        if p.first_start is None:
            p.first_start = t

        sl = min(q, p.remaining)
        s = t
        t += sl
        p.remaining -= sl

        tl.append((s, t, p.pid))

        while i < n and arr[i].arrival <= t:
            rq.append(idx[arr[i].pid])
            i += 1

        if p.remaining == 0:
            p.completion = t
            fin += 1
        else:
            rq.append(j)

    return tl, ps


def schedule_sjf_np(procs: List[Proc]) -> Tuple[List[Tuple[int, int, str]], List[Proc]]:
    ps = deep_copy(procs)
    t = 0
    tl: List[Tuple[int, int, str]] = []

    n = len(ps)
    comp = 0

    while comp < n:
        ready = [p for p in ps if p.arrival <= t and p.remaining > 0]

        if not ready:
            na = min([p.arrival for p in ps if p.remaining > 0])
            if t < na:
                tl.append((t, na, "IDLE"))
                t = na
            continue

        ready.sort(key=lambda p: (p.burst, p.arrival, p.pid))
        p = ready[0]

        if p.first_start is None:
            p.first_start = t

        s = t
        t += p.remaining
        p.remaining = 0
        p.completion = t

        tl.append((s, t, p.pid))
        comp += 1

    return tl, ps


def schedule_srtf(procs: List[Proc]) -> Tuple[List[Tuple[int, int, str]], List[Proc]]:
    ps = deep_copy(procs)
    t = 0
    n = len(ps)
    comp = 0
    run: List[Tuple[int, str]] = []

    while comp < n:
        avail = [p for p in ps if p.arrival <= t and p.remaining > 0]

        if not avail:
            nt = min([p.arrival for p in ps if p.remaining > 0])
            for x in range(t, nt):
                run.append((x, "IDLE"))
            t = nt
            continue

        avail.sort(key=lambda p: (p.remaining, p.arrival, p.pid))
        p = avail[0]

        if p.first_start is None:
            p.first_start = t

        run.append((t, p.pid))
        t += 1
        p.remaining -= 1

        if p.remaining == 0:
            p.completion = t
            comp += 1

    tl: List[Tuple[int, int, str]] = []

    if run:
        cur = run[0][1]
        s = run[0][0]

        for tm, pd in run[1:]:
            if pd != cur:
                tl.append((s, tm, cur))
                cur = pd
                s = tm

        tl.append((s, run[-1][0] + 1, cur))

    return tl, ps


def schedule_mlfq(procs: List[Proc], qs: List[int]) -> Tuple[List[Tuple[int, int, str]], List[Proc]]:
    if not qs:
        qs = [4, 8, 12]

    qs = [max(1, int(x)) for x in qs]
    L = len(qs)

    ps = deep_copy(procs)
    t = 0
    tl: List[Tuple[int, int, str]] = []

    n = len(ps)
    comp = 0

    arr = sorted(ps, key=lambda p: (p.arrival, p.pid))
    i = 0
    idx = {p.pid: k for k, p in enumerate(ps)}
    rq: List[List[int]] = [[] for _ in range(L)]

    def add(u: int):
        nonlocal i
        while i < n and arr[i].arrival <= u:
            rq[0].append(idx[arr[i].pid])
            i += 1

    while comp < n:
        add(t)

        lvl = None
        for k in range(L):
            if rq[k]:
                lvl = k
                break

        if lvl is None:
            if i < n and t < arr[i].arrival:
                tl.append((t, arr[i].arrival, "IDLE"))
                t = arr[i].arrival
                continue
            else:
                break

        j = rq[lvl].pop(0)
        p = ps[j]

        if p.first_start is None:
            p.first_start = t

        q = qs[lvl]
        used = 0
        s = t

        while used < q and p.remaining > 0:
            add(t)
            higher = any(rq[h] for h in range(lvl))
            if higher:
                break
            t += 1
            used += 1
            p.remaining -= 1

        tl.append((s, t, p.pid))

        if p.remaining == 0:
            p.completion = t
            comp += 1
        else:
            if used >= q and lvl < L - 1:
                lvl += 1
            rq[lvl].append(j)

    return tl, ps
