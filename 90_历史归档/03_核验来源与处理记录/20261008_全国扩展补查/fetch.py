import pathlib,json,urllib.request,urllib.parse,hashlib,concurrent.futures,html.parser,sys,zipfile,io,xml.etree.ElementTree as E
H=pathlib.Path(__file__).parent; S=H/'sources';S.mkdir(exist_ok=True)
class P(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.links=[];self.skip=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ('script','style'):self.skip+=1
  if t=='a' and d.get('href'):self.links.append(d['href'])
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
def fetch(u):
 k=hashlib.sha256(u.encode()).hexdigest()[:16];f=S/(k+'.json')
 if f.exists():return json.loads(f.read_text(encoding='utf8'))
 r={'url':u,'date':'2026-10-08','status':'','text':'','links':[]}
 try:
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  x=opener.open(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=12);b=x.read(10000000);ct=x.headers.get('Content-Type','');r['status']=str(x.status);r['content_type']=ct
  if b.startswith(b'%PDF'):
   from pypdf import PdfReader
   r['text']='\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages);(S/(k+'.pdf')).write_bytes(b)
  elif b.startswith(b'PK'):
   (S/(k+'.zip')).write_bytes(b)
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    if 'word/document.xml' in z.namelist():r['text']='\n'.join(E.fromstring(z.read('word/document.xml')).itertext())
    else:r['members']=z.namelist()
  else:
   enc='utf8' if b'utf-8' in b[:4000].lower() else 'gb18030' if b'gb' in b[:4000].lower() else 'utf8'
   s=b.decode(enc,errors='replace');p=P();p.feed(s);r['text']='\n'.join(p.parts);r['links']=[urllib.parse.urljoin(u,t) for t in p.links];(S/(k+'.html')).write_text(s,encoding='utf8')
 except Exception as e:r['status']='FAIL: '+str(e)
 f.write_text(json.dumps(r,ensure_ascii=False),encoding='utf8');return r
if __name__=='__main__':
 us=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf8'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for r in pool.map(fetch,us):print(r['status'],len(r['text']),r['url'])
