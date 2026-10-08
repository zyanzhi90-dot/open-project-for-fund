import pathlib,json,re,urllib.request,urllib.parse,ssl,concurrent.futures,io
from lxml import html
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/'audit_all'/'supplement';OUT.mkdir(exist_ok=True)
jobs=[('M033','https://slmt.cqu.edu.cn/info/10663/89610.htm'),('M189','https://sqtmqz.ecjtu.edu.cn/info/1031/3831.htm'),('M192','https://chongjian-lab.cqu.edu.cn/info/1012/2272.htm'),('M098_index','https://airs.cuhk.edu.cn/search'),('M194_guide','https://vlssm.nju.edu.cn/ad/6f/c22710a830831/page.htm'),('M117_extension','https://www.ascl.jlu.edu.cn/info/1041/1573.htm'),('M025_index','https://sklict.zju.edu.cn/'),('M112_image','https://jdgcxy.ncu.edu.cn/xwzx/tzgg/f268976adfb14c5aa8625c7930563f9f.htm'),('M194_image','https://vlssm.nju.edu.cn/ad/6d/c22710a830829/page.htm'),('M182_index','https://www.must.edu.mo/ssi')]
def get(job):
 id,u=job;f=OUT/(id+'.json')
 try:
  q=urllib.parse.quote(u,safe=':/?=&%+#');z=urllib.request.urlopen(urllib.request.Request(q,headers={'User-Agent':'Mozilla/5.0'}),timeout=15,context=ssl._create_unverified_context());b=z.read();tree=html.fromstring(b)
  links=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(u,a.get('href'))} for a in tree.xpath('//a[@href]')]
  images=[urllib.parse.urljoin(u,a.get('src')) for a in tree.xpath('//img[@src]')]
  for x in tree.xpath('//script|//style|//nav|//footer|//header'):x.drop_tree()
  text='\n'.join(x.strip() for x in tree.text_content().splitlines() if x.strip())
  d={'id':id,'url':u,'status':'ok','text':text,'links':links,'images':images}
  f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');print(id,len(text),flush=True)
 except Exception as e:f.write_text(json.dumps({'id':id,'url':u,'status':'failed','error':str(e)},ensure_ascii=False),encoding='utf8');print(id,'failed',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(get,jobs))
