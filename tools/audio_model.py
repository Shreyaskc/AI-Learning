"""Fetch only pinned official Kokoro files, without credentials or remote inference."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

REVISION='f3ff3571791e39611d31c381e3a41a3af07b4987'
FILES={'config.json': '5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f', 'kokoro-v1_0.pth': '496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4', 'voices/af_heart.pt': '0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff'}


def digest(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):result.update(chunk)
    return result.hexdigest()


def fetch(destination):
    destination=Path(destination).resolve()
    for name,expected in FILES.items():
        target=destination/name
        if target.exists():
            if digest(target)!=expected:raise SystemExit('Existing model file has an unexpected checksum; preserve and inspect it: '+str(target))
            print('Verified existing',name);continue
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_suffix(target.suffix+'.part')
        request=urllib.request.Request('https://huggingface.co/hexgrad/Kokoro-82M/resolve/'+REVISION+'/'+name)
        with urllib.request.urlopen(request,timeout=120) as response,temporary.open('wb') as output:
            for chunk in iter(lambda:response.read(1024*1024),b''):output.write(chunk)
        if digest(temporary)!=expected:raise SystemExit('Downloaded model checksum mismatch: '+name)
        temporary.replace(target);print('Downloaded and verified',name)
    print('Local snapshot:',destination)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,default=Path('.audio-model'));args=parser.parse_args();fetch(args.destination)
