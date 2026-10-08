import pathlib,json,re,urllib.request,urllib.parse,ssl,concurrent.futures,io,zipfile,hashlib,subprocess
from lxml import etree
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'audit_all'/'attachments';OUT.mkdir(exist_ok=True)
def extract(b):
 if b.startswith(b'%PDF'):return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages)
 if b.startswith(b'PK'):
  z=zipfile.ZipFile(io.BytesIO(b))
  if 'word/document.xml' in z.namelist():return '\n'.join(''.join(p.itertext()) for p in etree.fromstring(z.read('word/document.xml')).xpath('//*[local-name()="p"]'))
  return '\n'.join(n+'\n'+extract(z.read(n)) for n in z.namelist() if re.search(r'\.pdf$|\.docx$',n,re.I))
 return ''
jobs={}
for file in (ROOT/'official').glob('*.json'):
 s=json.loads(file.read_text(encoding='utf8'))
 for a in s.get('links',[]):
  if re.search(r'\.docx?\b|\.pdf\b|\.zip\b|\.rar\b|downloadAttach|\.xlsx?\b|clientDf.do|download.jsp',a['url'],re.I):
   if a['url'] not in jobs:jobs[a['url']]={'url':a['url'],'name':a['text'],'ids':[],'referer':s['url']}
   jobs[a['url']]['ids'].append(s['id'])
 if s['status']!='ok' and re.search(r'\.pdf\b',s['url'],re.I):jobs[s['url']]={'url':s['url'],'name':'正式指南PDF','ids':[s['id']],'referer':s['url']}
def get(a):
 key=hashlib.sha256(a['url'].encode()).hexdigest()[:16];dest=OUT/(key+'.json')
 if dest.exists():return json.loads(dest.read_text(encoding='utf8'))
 d=dict(a,status='failed',text='')
 try:
  target=OUT/(key+'.download')
  url=urllib.parse.quote(a['url'],safe=':/?=&%+#')
  z=subprocess.run(['curl.exe','-k','-L','--max-time','18','--connect-timeout','7','--max-filesize','25000000','-A','Mozilla/5.0','-e',a['referer'],'-sS','-o',str(target),url],capture_output=True,timeout=23)
  if z.returncode:raise ValueError(z.stderr.decode(errors='replace')[:160])
  b=target.read_bytes();target.unlink()
  if len(b)>25_000_000:raise ValueError('附件超过25MB，须单独读取')
  ext='.pdf' if b.startswith(b'%PDF') else '.docx' if b.startswith(b'PK') and b'word/' in b else '.zip' if b.startswith(b'PK') else '.rar' if b.startswith(b'Rar!') else '.doc' if b.startswith(bytes.fromhex('D0CF11E0')) else '.html'
  f=OUT/(key+ext);f.write_bytes(b);d['file']=str(f);d['text']=''
  d['status']='全文已提取' if d['text'].strip() else '待解析二进制附件' if ext!='.html' else '服务器返回网页/验证码'
  if d['text']:f.with_suffix('.txt').write_text(d['text'],encoding='utf8')
 except Exception as e:d['error']=str(e)[:220]
 dest.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');return d
print('需要处理的附件URL数',len(jobs),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
 result=list(pool.map(get,jobs.values()))
(ROOT/'audit_all'/'attachment_index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print('附件URL数',len(result),'状态',dict(Counter(a['status'] for a in result)))
