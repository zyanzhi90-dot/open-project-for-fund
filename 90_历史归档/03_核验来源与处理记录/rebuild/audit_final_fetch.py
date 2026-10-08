import pathlib,json,subprocess,urllib.parse,re,io,concurrent.futures
from lxml import html
from pypdf import PdfReader
R=pathlib.Path(__file__).parent; O=R/'audit_all'/'final_fetch';O.mkdir(exist_ok=True)
jobs={'M025':'https://sklict.zju.edu.cn/2025/0311/c85587a3147856/page.htm','M025_guide':'https://sklict.zju.edu.cn/_upload/article/files/78/0c/0e0b7cb64212855ad4d1fb5eaeb6/cffa0197-6de0-47f3-bf87-72beb7a06283.pdf','M165':'https://skliotsc.um.edu.mo/wp-content/uploads/2025/08/IOTSC-Guidelines-for-ORP-2026-2027.pdf','M194':'https://vlssm.nju.edu.cn/ad/6d/c22710a830829/page.htm','M194_guide':'https://vlssm.nju.edu.cn/ad/6f/c22710a830831/page.htm','M098':'https://airs.cuhk.edu.cn/article/1429','M098_search':'https://airs.cuhk.edu.cn/search','M192_index':'https://chongjian-lab.cqu.edu.cn/','M047':'https://amit.hrbust.edu.cn/'}
def get(k,u):
 f=O/(k+'.bin');q=subprocess.run(['curl.exe','-k','-L','--max-time','18','--connect-timeout','7','-A','Mozilla/5.0',u,'-o',str(f)],capture_output=True,timeout=23)
 d={'id':k,'url':u,'status':'failed','links':[],'text':''}
 if q.returncode==0:
  b=f.read_bytes()
  if b.startswith(b'%PDF'):d['text']='\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages)
  else:
   t=html.fromstring(b);d['links']=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(u,a.get('href'))} for a in t.xpath('//a[@href]')]
   d['images']=[urllib.parse.urljoin(u,a) for a in t.xpath('//img/@src')];d['embeds']=t.xpath('//iframe/@src|//embed/@src|//object/@data')
   for x in t.xpath('//script|//style|//nav|//footer|//header'):x.drop_tree()
   d['text']='\n'.join(x.strip() for x in t.text_content().splitlines() if x.strip())
  d['status']='ok' if len(d['text'])>150 else 'empty'
 else:d['error']=q.stderr.decode(errors='replace')[-300:]
 (O/(k+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');print(k,d['status'],len(d['text']),d.get('embeds',[]),flush=True)
 if k in ['M025','M165'] and d['status']=='ok':(R/'official'/(k+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(lambda x:get(*x),jobs.items()))
