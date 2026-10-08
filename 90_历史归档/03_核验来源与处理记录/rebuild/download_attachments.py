import pathlib,json,concurrent.futures,urllib.request,ssl,re,zipfile,io,subprocess
from lxml import etree
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).parent; folder=ROOT/'attachments';folder.mkdir(exist_ok=True)
ids=['M078','M066','M017','M160','M007','M029','M035','M041','M077','M084','M068','M100']
jobs=[]
for i in ids:
 p=ROOT/'official'/(i+'.json')
 if not p.exists():continue
 for n,a in enumerate(json.loads(p.read_text(encoding='utf8'))['links']):
  if re.search(r'\.docx|\.doc\b|\.pdf|\.zip|\.rar|DownloadAttach',a['url']+' '+a['text'],re.I) and not re.search(r'创新基金|年度进展|结题报告',a['text']): jobs.append((i,n,a))
def extract(b,name):
 if b.startswith(b'%PDF'):return '\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(b)).pages)
 if b.startswith(b'PK'):
  z=zipfile.ZipFile(io.BytesIO(b)); ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
  if 'word/document.xml' in z.namelist():return '\n'.join(''.join(p.itertext()) for p in etree.fromstring(z.read('word/document.xml')).xpath('//w:p',namespaces=ns))
  texts=[]
  for x in z.namelist():
   if re.search(r'\.docx|\.pdf$',x,re.I):
    try:texts.append(x+'\n'+extract(z.read(x),x))
    except Exception:pass
  return '\n'.join(texts)
 return ''
def get(job):
 i,n,a=job;out={'id':i,'name':a['text'],'url':a['url'],'status':'failed','text':''}
 try:
  z=urllib.request.urlopen(urllib.request.Request(a['url'],headers={'User-Agent':'Mozilla/5.0','Referer':json.loads((ROOT/'official'/(i+'.json')).read_text(encoding='utf8'))['url']}),timeout=16,context=ssl._create_unverified_context());b=z.read()
  ext='.docx' if b.startswith(b'PK') and 'docx' in a['text'] else '.zip' if b.startswith(b'PK') else '.pdf' if b.startswith(b'%PDF') else '.rar' if b.startswith(b'Rar!') else '.doc' if b.startswith(bytes.fromhex('D0CF11E0')) else '.html'
  f=folder/(i+'_'+str(n)+ext);f.write_bytes(b);out['file']=str(f)
  out['text']=extract(b,a['text']);out['status']='read' if out['text'] else 'downloaded_unparsed' if ext!='.html' else 'html_instead_of_attachment'
  if out['text']:f.with_suffix('.txt').write_text(out['text'],encoding='utf8')
 except Exception as e:out['error']=str(e)[:200]
 (folder/(i+'_'+str(n)+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 return {k:v for k,v in out.items() if k!='text'}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for r in pool.map(get,jobs):print(json.dumps(r,ensure_ascii=False),flush=True)
