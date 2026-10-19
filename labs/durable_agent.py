"""Durable bounded workflow + separate idempotent provider simulator.

Both stores are local SQLite files. This teaches crash/recovery semantics, not a
production distributed exactly-once guarantee or an LLM-driven agent.
"""
from contextlib import contextmanager
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path


class CrashAfterEffect(Exception):pass


@contextmanager
def connect(path):
    db=sqlite3.connect(str(path),timeout=5,isolation_level=None)
    db.row_factory=sqlite3.Row
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def encoded_payload(action,arguments):
    if action!='draft_ticket':raise PermissionError('only draft_ticket is allowlisted')
    if not isinstance(arguments,dict) or set(arguments)!={'incident_id'}:
        raise ValueError('incident_id is the only allowed field')
    if not isinstance(arguments['incident_id'],str) or not arguments['incident_id'].isdecimal():
        raise ValueError('incident_id must be a numeric string')
    return json.dumps({'action':action,'arguments':arguments},sort_keys=True,separators=(',',':'))


def identity(tenant,operation_id):
    if not isinstance(tenant,str) or not tenant or not isinstance(operation_id,str) or not operation_id:
        raise PermissionError('trusted tenant identity and operation ID required')


class Provider:
    """A separate effect system with atomic, payload-bound idempotency."""
    def __init__(self,path):
        self.path=path
        with connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS effects (tenant TEXT, op TEXT, payload TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(tenant,op))')
    def status(self,tenant,op):
        identity(tenant,op)
        with connect(self.path) as db:
            row=db.execute('SELECT * FROM effects WHERE tenant=? AND op=?',(tenant,op)).fetchone()
            return dict(row) if row else None
    def apply(self,tenant,op,payload):
        identity(tenant,op)
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM effects WHERE tenant=? AND op=?',(tenant,op)).fetchone()
            if row:
                if row['payload']!=payload:raise ValueError('provider idempotency key payload conflict')
                return json.loads(row['result'])
            result={'ticket_id':'sim-'+hashlib.sha256((tenant+':'+op).encode()).hexdigest()[:12],
                    'status':'drafted','incident_id':json.loads(payload)['arguments']['incident_id']}
            db.execute('INSERT INTO effects VALUES (?,?,?,?)',(tenant,op,payload,json.dumps(result,sort_keys=True)))
            return result
    def count(self):
        with connect(self.path) as db:return db.execute('SELECT count(*) FROM effects').fetchone()[0]


class DurableWorkflow:
    def __init__(self,path,provider,max_attempts=2):
        if max_attempts<1:raise ValueError('positive attempt budget required')
        self.path,self.provider,self.max_attempts=path,provider,max_attempts
        with connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS jobs (tenant TEXT,op TEXT,payload TEXT NOT NULL,state TEXT NOT NULL,attempts INTEGER NOT NULL,max_attempts INTEGER NOT NULL,result TEXT,PRIMARY KEY(tenant,op))')
            db.execute('CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT,tenant TEXT,op TEXT,event TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS memory (tenant TEXT,id TEXT,source TEXT,owner TEXT,expires REAL,verified INTEGER,statement TEXT,PRIMARY KEY(tenant,id))')
    @staticmethod
    def log(db,tenant,op,event):db.execute('INSERT INTO audit(tenant,op,event) VALUES (?,?,?)',(tenant,op,event))
    def submit(self,tenant,op,action,arguments):
        identity(tenant,op);payload=encoded_payload(action,arguments)
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT payload FROM jobs WHERE tenant=? AND op=?',(tenant,op)).fetchone()
            if row:
                if row['payload']!=payload:raise ValueError('operation ID payload conflict')
            else:
                db.execute('INSERT INTO jobs VALUES (?,?,?,\'PENDING\',0,?,NULL)',(tenant,op,payload,self.max_attempts))
                self.log(db,tenant,op,'SUBMITTED')
    def status(self,tenant,op):
        identity(tenant,op)
        with connect(self.path) as db:
            row=db.execute('SELECT * FROM jobs WHERE tenant=? AND op=?',(tenant,op)).fetchone()
            if row is None:raise KeyError(op)
            return dict(row)
    def finish(self,tenant,op,result,event):
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE jobs SET state=\'SUCCEEDED\',result=? WHERE tenant=? AND op=?',
                       (json.dumps(result,sort_keys=True),tenant,op))
            self.log(db,tenant,op,event)
        return result
    def run(self,tenant,op,crash=False):
        row=self.status(tenant,op)
        if row['state']=='SUCCEEDED':return json.loads(row['result'])
        # Reconcile ambiguous previous effects BEFORE retry or budget rejection.
        previous=self.provider.status(tenant,op)
        if previous:
            if previous['payload']!=row['payload']:raise ValueError('provider/local payload mismatch')
            return self.finish(tenant,op,json.loads(previous['result']),'RECONCILED_PROVIDER_EFFECT')
        exhausted=False
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT * FROM jobs WHERE tenant=? AND op=?',(tenant,op)).fetchone()
            if current['attempts']>=current['max_attempts']:
                exhausted=True
                db.execute('UPDATE jobs SET state=\'STOPPED\' WHERE tenant=? AND op=?',(tenant,op))
                self.log(db,tenant,op,'ATTEMPT_BUDGET_EXHAUSTED')
            else:
                db.execute('UPDATE jobs SET state=\'RUNNING\',attempts=attempts+1 WHERE tenant=? AND op=?',(tenant,op))
                self.log(db,tenant,op,'DISPATCH_ATTEMPT')
        if exhausted:raise RuntimeError('attempt budget exhausted')
        result=self.provider.apply(tenant,op,row['payload'])
        if crash:raise CrashAfterEffect('effect committed; local acknowledgement not committed')
        return self.finish(tenant,op,result,'ACKNOWLEDGED')
    def events(self,tenant,op):
        with connect(self.path) as db:return [r[0] for r in db.execute('SELECT event FROM audit WHERE tenant=? AND op=? ORDER BY seq',(tenant,op))]
    def remember(self,tenant,key,statement,source,owner,expires,verified=False):
        identity(tenant,key)
        if not source or not owner or not isinstance(statement,str):raise ValueError('provenance and owner required')
        with connect(self.path) as db:db.execute('INSERT OR REPLACE INTO memory VALUES (?,?,?,?,?,?,?)',
             (tenant,key,source,owner,expires,int(verified),statement))
    def recall(self,tenant,now):
        identity(tenant,'memory-read')
        with connect(self.path) as db:return [dict(r) for r in db.execute('SELECT * FROM memory WHERE tenant=? AND verified=1 AND expires>? ORDER BY id',(tenant,now))]
    def delete_source(self,tenant,source):
        with connect(self.path) as db:db.execute('DELETE FROM memory WHERE tenant=? AND source=?',(tenant,source))



def ownership_paths(service,edges,tenant,allowed_nodes,now):
    # Typed two-hop relation query; every node and edge is permission/freshness scoped.
    usable=[e for e in edges if e['tenant']==tenant and e['expires']>now and e['source_id']
            and e['from'] in allowed_nodes and e['to'] in allowed_nodes]
    paths=[]
    for dependency in usable:
        if dependency['from']!=service or dependency['relation']!='DEPENDS_ON':continue
        for owner in usable:
            if owner['from']==dependency['to'] and owner['relation']=='OWNED_BY':
                paths.append({'team':owner['to'],'path':[service,dependency['to'],owner['to']],
                              'sources':[dependency['source_id'],owner['source_id']]})
    return paths


def demo():
    with tempfile.TemporaryDirectory(prefix='ai-fluency-durable-') as directory:
        local,remote=Path(directory)/'jobs.sqlite',Path(directory)/'provider.sqlite'
        provider=Provider(remote);flow=DurableWorkflow(local,provider)
        flow.submit('blue','op42','draft_ticket',{'incident_id':'42'})
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',str(local),'--provider',str(remote)]
        crashed=subprocess.run(command+['--crash'],capture_output=True,text=True)
        if crashed.returncode!=73:raise RuntimeError('failure injection did not reach crash point: '+crashed.stderr)
        after_crash=flow.status('blue','op42')
        recovered=subprocess.run(command,capture_output=True,text=True,check=True)
        # Reopen after process exit rather than relying on in-memory state.
        flow=DurableWorkflow(local,Provider(remote));after_recovery=flow.status('blue','op42')
        flow.remember('blue','m1','Checked incident 42','incident:42','operator',expires=200,verified=True)
        before_delete=len(flow.recall('blue',100));expired=len(flow.recall('blue',201))
        flow.delete_source('blue','incident:42')
        return {'kind':'two SQLite stores; separate worker processes; simulated provider effects',
                'crash_process_exit':crashed.returncode,'state_after_crash':after_crash['state'],
                'state_after_recovery':after_recovery['state'],'provider_effect_count':provider.count(),
                'attempts':after_recovery['attempts'],'audit':flow.events('blue','op42'),
                'memory_counts':{'valid':before_delete,'expired':expired,'after_source_delete':len(flow.recall('blue',100))},
                'limits':'serial recovery; no distributed leases or real external API; provider status is definitive and provider idempotency is atomic in this simulator'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=Path);parser.add_argument('--provider',type=Path)
    parser.add_argument('--crash',action='store_true');parser.add_argument('--report',type=Path);args=parser.parse_args()
    if args.worker:
        flow=DurableWorkflow(args.worker,Provider(args.provider))
        try:result=flow.run('blue','op42',crash=args.crash)
        except CrashAfterEffect:os._exit(73)
    else:result=demo()
    text=json.dumps(result,indent=2,sort_keys=True)
    if args.report:args.report.write_text(text+'\n')
    print(text)


if __name__=='__main__':main()
