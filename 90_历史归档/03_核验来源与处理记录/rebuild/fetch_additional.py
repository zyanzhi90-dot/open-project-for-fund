import pathlib,urllib.request,json,lxml.html,urllib.parse,ssl
root=pathlib.Path(__file__).parent
for id,u in [('M100','https://news.cqjtu.edu.cn/info/1024/68220.htm'),('M056','https://imr.sjtu.edu.cn/hot_recommend/4483.html'),('M025','https://sklict.zju.edu.cn/85587/list.htm')]:
 b=urllib.request.urlopen(u,timeout=20,context=ssl._create_unverified_context()).read().decode('utf8')
 t=lxml.html.fromstring(b);s='\n'.join(x.strip() for x in t.xpath('//body//text()') if x.strip())
 links=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(u,a.get('href'))} for a in t.xpath('//a[@href]')]
 o={'id':id,'url':u,'final_url':u,'status':'ok','text':s,'links':links}
 if id=='M025':
  a=next(x for x in links if '2026-2027年度工业控制技术全国重点实验室开放基金-湖控专项申报' in x['text'])
  print('ZJU CALL',a)
  b=urllib.request.urlopen(a['url'],timeout=20).read().decode('utf8');t=lxml.html.fromstring(b)
  o.update(url=a['url'],final_url=a['url'],text='\n'.join(x.strip() for x in t.xpath('//body//text()') if x.strip()),links=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(a['url'],a.get('href'))} for a in []])
 (root/'official'/f'{id}.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
 print(id,o['text'][-10000:] if id=='M025' else 'saved')
