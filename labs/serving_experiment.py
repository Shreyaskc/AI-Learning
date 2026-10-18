"""Measure a bounded threaded MOCK service; no sockets, model or token inference.

Real monotonic timings include scheduler noise. Synthetic service = small hashes
plus sleep to model a fixed + per-item cost. Results are not GPU/LLM throughput.
"""
import argparse
import hashlib
import json
import math
import os
import queue
import sys
import threading
import time
from pathlib import Path


def percentile(values,fraction):
    if not values:return None
    if not 0<fraction<=1:raise ValueError('fraction must be in (0,1]')
    ordered=sorted(values)
    return ordered[math.ceil(fraction*len(ordered))-1]


def distribution(values):
    return {'n':len(values),'mean_ms':1000*sum(values)/len(values) if values else None,
            'p50_ms':1000*percentile(values,.5) if values else None,
            'p95_ms':1000*percentile(values,.95) if values else None,
            'p99_ms':1000*percentile(values,.99) if values else None}


def experiment(name,count=100,interval=.001,workers=2,capacity=8,batch_size=1,
               fixed_seconds=.004,per_item_seconds=.002):
    if min(count,workers,capacity,batch_size)<1 or interval<=0:raise ValueError('positive workload settings required')
    pending=queue.Queue(maxsize=capacity);lock=threading.Lock();records=[];rejected=[];max_depth=0
    def worker():
        while True:
            first=pending.get()
            if first is None:pending.task_done();return
            batch=[first]
            while len(batch)<batch_size:
                try:batch.append(pending.get_nowait())
                except queue.Empty:break
            begin=time.perf_counter()
            payload=b'ai-fluency-synthetic-request'
            for _ in range(100*len(batch)):payload=hashlib.sha256(payload).digest()
            time.sleep(fixed_seconds+per_item_seconds*len(batch))
            end=time.perf_counter()
            with lock:
                records.extend({'id':number,'queue_seconds':begin-arrival,'service_seconds':end-begin,
                                'end_to_end_seconds':end-arrival,'batch_items':len(batch)} for number,arrival in batch)
            for _ in batch:pending.task_done()
    threads=[threading.Thread(target=worker,daemon=True) for _ in range(workers)]
    for thread in threads:thread.start()
    start=time.perf_counter()
    for number in range(count):
        target=start+number*interval
        remaining=target-time.perf_counter()
        if remaining>0:time.sleep(remaining)
        arrival=time.perf_counter()
        try:pending.put_nowait((number,arrival));max_depth=max(max_depth,pending.qsize())
        except queue.Full:rejected.append(number)
    offer_end=time.perf_counter();pending.join();end=time.perf_counter()
    for _ in threads:pending.put(None)
    for thread in threads:thread.join()
    elapsed=end-start;offer_window=max(offer_end-start,interval)
    return {'scenario':name,'configuration':{'offered_requests':count,'arrival_interval_seconds':interval,
             'workers':workers,'queue_capacity':capacity,'max_batch':batch_size,
             'mock_fixed_service_seconds':fixed_seconds,'mock_per_item_seconds':per_item_seconds},
            'offered':count,'completed':len(records),'rejected':len(rejected),
            'rejection_fraction':len(rejected)/count,'max_observed_queue_depth':max_depth,
            'offer_window_seconds':offer_window,'drain_window_seconds':elapsed,
            'observed_offered_requests_per_second':count/offer_window,
            'completed_requests_per_second_including_drain':len(records)/elapsed,
            'queue':distribution([r['queue_seconds'] for r in records]),
            'service':distribution([r['service_seconds'] for r in records]),
            'end_to_end':distribution([r['end_to_end_seconds'] for r in records]),
            'largest_observed_batch':max((r['batch_items'] for r in records),default=0)}


def run():
    return {'kind':'MEASURED LOCAL MOCK SERVICE; no model inference, network, GPU, or token throughput',
            'runtime':{'python':sys.version.split()[0],'system':os.uname().sysname,
                       'release':os.uname().release,'architecture':os.uname().machine,'logical_cpus':os.cpu_count()},
            'clock':'time.perf_counter (monotonic)',
            'percentile_convention':'nearest rank: sorted[ceil(p*n)-1]; accepted requests only',
            'limitations':'single short run, OS scheduling noise, shared host, not a capacity certification; rejected requests are excluded from latency distributions and reported separately; synthetic batch cost is an assumption',
            'results':[experiment('underload',count=60,interval=.01),
                       experiment('overload_single',count=120,interval=.0005),
                       experiment('overload_batch4',count=120,interval=.0005,batch_size=4)]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    text=json.dumps(run(),indent=2,sort_keys=True)
    if args.report:args.report.write_text(text+'\n')
    print(text)


if __name__=='__main__':main()
