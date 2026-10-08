import pathlib,json,sys,subprocess,concurrent.futures,hashlib,datetime
sys.stdout.reconfigure(encoding='utf-8')
H=pathlib.Path(__file__).parent;O=H/'sources';O.mkdir(exist_ok=True)
def one(url):
 p=O/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.json')
 if p.exists():return json.loads(p.read_text(encoding='utf8'))
 try:
  subprocess.run([sys.executable,'-c','import sys,fetch_sources;fetch_sources.fetch(sys.argv[1])',url],cwd=H,timeout=25,check=True,capture_output=True)
  return json.loads(p.read_text(encoding='utf8'))
 except Exception as e:
  d={'url':url,'checked_at_beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'访问未取得（25秒请求总时限）：'+str(type(e).__name__),'text':'','links':[]};p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');return d
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for d in pool.map(one,dict.fromkeys(json.loads((H/sys.argv[1]).read_text(encoding='utf8')))):print(d['url'],d['status'],len(d.get('text','')),flush=True)
