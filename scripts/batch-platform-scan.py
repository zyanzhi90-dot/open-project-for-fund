"""Fetch queue evidence; never changes the mother table or decides eligibility.
Usage: python scripts/batch-platform-scan.py --limit 50 --batch fast001
"""
import argparse,csv,json,re,hashlib,time,threading
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import requests

ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'02_检索与核验记录/未覆盖平台续查_20261011'
CACHE=ROOT/'.sync/batch-fetch-cache'
KEY=re.compile(r'开放(?:课题|基金|研究)|申请指南|申报通知|延期|延长|滚动')
FIELD=re.compile(r'截止|受理|申请|申报|方向|机器人|无人|装备|操控|控制|万元|博士|职称|合作')
LOCAL=threading.local()
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.links=[];self.href=None;self.label=[];self.hidden=0
    def handle_starttag(self,t,a):
        if t in ('script','style'):self.hidden+=1
        if t=='a':self.href=dict(a).get('href');self.label=[]
        if t in ('p','div','br','li','tr','h1','h2','h3'):self.parts.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style'):self.hidden=max(0,self.hidden-1)
        if t=='a':
            if self.href:self.links.append((''.join(self.label),self.href))
            self.href=None
    def handle_data(self,s):
        if not self.hidden:
            self.parts.append(s)
            if self.href:self.label.append(s)
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def fetch(url):
    key=hashlib.sha256(url.encode()).hexdigest();p=CACHE/(key+'.json')
    if p.exists():
        r=json.loads(p.read_text(encoding='utf-8'));return dict(r,cache_hit=True)
    r={'url':url,'status':'blocked','time':time.strftime('%Y-%m-%dT%H:%M:%S'),'cache_hit':False}
    try:
        if not hasattr(LOCAL,'session'):LOCAL.session=requests.Session()
        response=LOCAL.session.get(url,timeout=(4,8),headers={'User-Agent':'Mozilla/5.0'},stream=True)
        response.raise_for_status();typ=response.headers.get('Content-Type','')
        r.update(final_url=response.url,content_type=typ)
        if 'html' not in typ and 'text/' not in typ:
            r.update(status='non_html',gap='附件未展开；不下载申请书或补条款')
        else:
            chunks=[];size=0
            for chunk in response.iter_content(32768):
                chunks.append(chunk);size+=len(chunk)
                if size>=1500000:break
            response._content=b''.join(chunks)
            if not response.encoding or response.encoding.lower()=='iso-8859-1':response.encoding=response.apparent_encoding
            page=Page();page.feed(response.text)
            lines=[re.sub(r'\s+',' ',s).strip() for s in ''.join(page.parts).splitlines()]
            lines=[s for s in lines if s]
            body='\n'.join(lines);(CACHE/(key+'.txt')).write_text(body,encoding='utf-8')
            excerpts=[]
            for i,s in enumerate(lines):
                if FIELD.search(s):excerpts.append(' '.join(lines[max(0,i-1):i+2]))
            links=[]
            for label,href in page.links:
                target=urljoin(response.url,href)
                if KEY.search(label) and urlsplit(target).hostname==urlsplit(response.url).hostname and target not in [x['url'] for x in links]:
                    links.append({'title':label[:160],'url':target})
            r.update(status='fetched',excerpt='\n'.join(dict.fromkeys(excerpts))[:1400],links=links[:12],body_chars=len(body),raw_file=str((CACHE/(key+'.txt')).relative_to(ROOT)))
        response.close()
    except Exception as e:r['gap']=str(e)[:200]
    dump(p,r);return r
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=50);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--batch',required=True);ap.add_argument('--workers',type=int,default=8);args=ap.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',args.batch):ap.error('invalid batch')
    dest=RECORDS/args.batch
    if dest.exists():ap.error('batch exists; cached fetches are reusable, choose a new batch ID')
    with (RECORDS/'剩余未查平台_最新.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))[args.offset:args.offset+args.limit]
    known=set()
    for p in RECORDS.glob('平台核查结果_*.csv'):
        with p.open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f):known.update(r.get('来源URL','').splitlines())
    seeds={};items=[]
    for r in rows:
        urls=list(dict.fromkeys(re.findall(r'https?://[^\s]+',r.get('来源URL候选',''))))
        chosen=[u for u in urls if u not in known][:2]
        seeds.update({u:None for u in chosen})
        items.append({'id':r['平台ID'],'platform':r['平台名称原称'],'institution':r['依托机构原称'],'seeds':chosen,'source_warning':'原输入可能混合机构，需核页面主体；不是已认证官方URL','gap': '无新入口：复用旧证据或需定向搜索' if not chosen else ''})
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(fetch,seeds):seeds[r['url']]=r
        child_urls=list(dict.fromkeys(x['url'] for p in seeds.values() for x in p.get('links',[])[:3] if x['url'] not in seeds and x['url'] not in known))
        children={r['url']:r for r in pool.map(fetch,child_urls)}
    for item in items:
        item['pages']=[seeds[u] for u in item.pop('seeds')]
        item['announcements']=[children[x['url']] for p in item['pages'] for x in p.get('links',[])[:3] if x['url'] in children]
    dump(dest/'抓取证据.json',items)
    compact=[{**{k:v for k,v in i.items() if k not in ('pages','announcements')},'pages':[{k:(p[k][:650] if k=='excerpt' else p[k][:3] if k=='links' else p[k]) for k in ('url','status','gap','excerpt','links') if k in p} for p in i['pages']+i['announcements']]} for i in items]
    dump(dest/'模型初筛输入.json',compact)
    summary={'queue_records':len(rows),'unique_fetches':len(seeds)+len(children),'cache_hits':sum(p['cache_hit'] for p in list(seeds.values())+list(children.values())),'fetched':sum(p['status']=='fetched' for p in list(seeds.values())+list(children.values())),'input_chars':len(json.dumps(compact,ensure_ascii=False)),'mother_unchanged':True,'completion':'仅抓取取证，不计为平台核查完成'}
    dump(dest/'批次统计.json',summary);print(json.dumps(summary,ensure_ascii=True))
if __name__=='__main__':main()
