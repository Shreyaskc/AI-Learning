"""Run every cheap offline lab without overwriting committed evidence."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LABS=['foundations','learning','attention','retrieval','platform','multimodal','experiments','electives',
      'model_comparison','language_model','rag_evaluation','durable_agent','serving_experiment','representations']


def main():
    for name in LABS:
        result=subprocess.run([sys.executable,str(ROOT/'labs'/f'{name}.py')],cwd=ROOT,capture_output=True,text=True,timeout=30)
        if result.returncode:
            print(result.stdout);print(result.stderr,file=sys.stderr)
            raise SystemExit(f'FAIL: {name}')
        print(f'PASS: {name}')
    print(f'{len(LABS)} offline labs completed; no committed evidence files overwritten')


if __name__=='__main__':main()
