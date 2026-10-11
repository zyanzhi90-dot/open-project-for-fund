"""Check proposed public URLs against cached project evidence before opening.

Usage: python -X utf8 scripts/preflight-open-urls.py URL [URL ...]
The result is a retrieval guard, not proof of eligibility or nationwide coverage.
"""
import csv, json, sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'02_检索与核验记录/审计记录/项目去重基准_20261011.csv'

def normalize(url):
    p=urlsplit(url.strip())
    host=p.netloc.lower().removeprefix('www.')
    return urlunsplit(('',host,p.path.rstrip('/'),p.query,''))

def main():
    with BASE.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    output=[]
    for url in sys.argv[1:]:
        key=normalize(url);hits=[]
        for row in rows:
            sources=(row.get('主来源URL','')+'\n'+row.get('全部来源URL','')).replace(';','\n').replace('；','\n').splitlines()
            if any(normalize(s)==key for s in sources if s.strip().startswith(('http://','https://'))):hits.append(row)
        closed=[r for r in hits if '已截止' in r.get('状态原文','')]
        output.append({'url':url,'action':'known_closed_stop' if closed else 'existing_evidence_reuse' if hits else 'not_in_baseline',
            'records':[{'id':r.get('项目编号'),'status':r.get('状态原文'),'deadline':r.get('截止日期原文')} for r in hits],
            'boundary':'Only URL baseline match; no match does not establish a new batch. Also consult mother and external additions; first-blocked links must not be retried.'})
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
