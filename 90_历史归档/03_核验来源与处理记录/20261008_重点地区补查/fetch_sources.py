"""Cache official source text/links; reuse prior evidence; do not author Excel."""
import pathlib,json,re,urllib.request,urllib.parse,ssl,html,hashlib,concurrent.futures,sys,zipfile,io,datetime
from pypdf import PdfReader
H=pathlib.Path(__file__).parent; ROOT=H.parents[2]; O=H/'sources'; O.mkdir(exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
old={}
for folder in [H.parent/'20261008_最终收尾/sources',H.parent/'20261008_严格重筛/sources']:
 for p in folder.glob('*.json'):
  try:
   d=json.loads(p.read_text(encoding='utf8'))
   for s in d.get('sources',[]):
    if s.get('text') and len(s['text'])>150:old[s['url']]=(p,s)
  except Exception:pass
def fetch(url):
 key=hashlib.sha256(url.encode()).hexdigest()[:16]; p=O/(key+'.json')
 if p.exists():return json.loads(p.read_text(encoding='utf8'))
 d={'url':url,'checked_at_beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'links':[]}
 if url in old:
  p0,s=old[url];d.update(s);d['reuse_path']=str(p0.relative_to(ROOT));d['status']='复用已取得来源（未重新访问）'
 else:
  try:
   with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as r:
    b=r.read(12000000);d.update({'http_status':r.status,'final_url':r.url,'content_type':r.headers.get('Content-Type','')})
   if b.startswith(b'%PDF'):
    (O/(key+'.pdf')).write_bytes(b);d['text']='\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages);d['status']='PDF全文已取得'
   elif b.startswith(b'PK'):
    (O/(key+'.docx')).write_bytes(b)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
     raw=z.read('word/document.xml').decode('utf8');d['text']=html.unescape(re.sub('<[^>]+>','\n',raw));d['status']='DOCX全文已取得'
   else:
    try:raw=b.decode('utf8')
    except UnicodeDecodeError:raw=b.decode('gb18030','replace')
    for m in re.finditer(r'<a\b[^>]*href\s*=\s*[\"\x27]([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>',raw,re.I|re.S):
     u=urllib.parse.urljoin(d['final_url'],html.unescape(m.group(1))); label=html.unescape(re.sub('<[^>]+>','',m.group(2))).strip()
     if u.startswith(('http://','https://')):d['links'].append({'label':label,'url':u})
    raw=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',raw,flags=re.I|re.S)
    d['text']='\n'.join(x.strip() for x in html.unescape(re.sub('<[^>]+>','\n',raw)).splitlines() if x.strip())
    d['status']='正文已取得' if len(d['text'])>100 else '正文不完整'
    if '验证码' in d['text'] and len(d['text'])<1000:d['status']='验证码限制，附件未取得'
  except Exception as e:d.update({'text':'','status':'访问失败：'+str(e)})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');(O/(key+'.txt')).write_text(d.get('text',''),encoding='utf8')
 return d
if __name__=='__main__':
 urls=json.loads((H/sys.argv[1]).read_text(encoding='utf8'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for d in pool.map(fetch,dict.fromkeys(urls)):print(d['url'],d['status'],len(d.get('text','')))
