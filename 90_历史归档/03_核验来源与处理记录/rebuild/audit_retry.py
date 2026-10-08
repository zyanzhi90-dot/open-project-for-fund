import pathlib,json,re,concurrent.futures,urllib.request,urllib.parse,ssl,io
from lxml import html
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).parent
ps=json.load(open(ROOT/'normalized.json',encoding='utf8'))['projects']
extra={
 'M013':'https://raolab.bjtu.edu.cn/wp-content/uploads/2025/09/%E5%85%88%E8%BF%9B%E8%BD%A8%E9%81%93%E4%BA%A4%E9%80%9A%E8%87%AA%E4%B8%BB%E8%BF%90%E8%A1%8C%E5%85%A8%E5%9B%BD%E9%87%8D%E7%82%B9%E5%AE%9E%E9%AA%8C%E5%AE%A4%E5%BC%80%E6%94%BE%E8%AF%BE%E9%A2%98%E7%94%B3%E8%AF%B7%E6%8C%87%E5%8D%972026-20250928.pdf',
 'M123':'https://iapme.um.edu.mo/wp-content/uploads/2026/01/1.-IAPME-ORP-%E6%8C%87%E5%8D%97-2026.pdf',
 'M056':'https://imr.sjtu.edu.cn/hot_recommend/4483.html',
 'M025':'https://sklict.zju.edu.cn/2025/0704/c85587a3067831/page.htm',
 'M021':'https://keysoftlab.nju.edu.cn/1609/list.htm',
}
def get(p):
 file=ROOT/'official'/(p['id']+'.json');s=json.load(open(file,encoding='utf8'))
 if s['status']=='ok' and p['id'] not in extra:return None
 urls=list(dict.fromkeys([extra.get(p['id']),p['url'],p['second']]))
 urls=[x for x in urls if x]
 for u in list(urls):
  if '/www.' in u:urls.append(u.replace('/www.','/'))
  if u.startswith('https:'):urls.append(u.replace('https:','http:',1))
 errors=[]
 for u in urls:
  try:
   z=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=12,context=ssl._create_unverified_context());b=z.read()
   links=[]
   if b.startswith(b'%PDF'):text='\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages)
   else:
    m=re.search(rb'charset\s*=\s*[\"\x27]?([a-zA-Z0-9-]+)',b[:5000]);enc=m.group(1).decode() if m else 'utf-8';tree=html.fromstring(b.decode(enc,errors='replace'))
    links=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(z.url,a.get('href'))} for a in tree.xpath('//a[@href]') if re.search(r'附件|申请|指南|办法|\.doc|\.pdf|\.zip|\.rar|\.xls|download',a.text_content()+' '+a.get('href'),re.I)]
    for x in tree.xpath('//script|//style|//nav|//footer|//header'):x.drop_tree()
    text='\n'.join(x.strip() for x in tree.text_content().splitlines() if x.strip())
   if len(text)<150:raise ValueError('空页/正文不足')
   d={'id':p['id'],'url':u,'status':'ok','text':text,'links':links,'final_url':z.url,'http':z.status,'retry_errors':errors}
   if p['id']=='M021':(ROOT/'audit_all'/'M021_management.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
   else:file.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
   return p['id']+' OK '+str(len(text))
  except Exception as e:errors.append(u+' '+str(e)[:160])
 (ROOT/'audit_all'/(p['id']+'_retry.json')).write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf8')
 return p['id']+' STILL FAILED'
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
 for r in pool.map(get,ps):
  if r:print(r,flush=True)
