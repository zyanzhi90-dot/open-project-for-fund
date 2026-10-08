import json,urllib.request,lxml.html,pathlib,re
root=pathlib.Path(__file__).parent
u='https://imr.sjtu.edu.cn/hot_recommend/4483.html'
t=lxml.html.fromstring(urllib.request.urlopen(u,timeout=25).read().decode('utf8'))
s='\n'.join(x.strip() for x in t.xpath('//body//text()') if x.strip())
(root/'sjtu_call.txt').write_text(s,encoding='utf8')
print(s[s.index('上海市柔性医疗机器人重点实验室开放课题'):s.index('上一篇：')])
print('MAIL',t.xpath('//a[contains(@href,"mailto")]/@href'))
print('IMAGES',t.xpath('//img/@src'))
d=json.load(open(root/'original.json',encoding='utf8'))
for r in d['02项目完整详情'][6:]:
 if r[0] and r[0] in ['M043','M068','M106','M017','M100','M161','M026','M025','M047','M049','M075','M112','M187','M156','M009','M166','M070','M098','M159','M157','M086']:
  print('\nROW',r)
  try:
   o=json.load(open(root/'official'/f'{r[0]}.json',encoding='utf8'))
   text=o.get('text','')
   print('OFFICIAL',text[-19000:])
   print('LINKS',o.get('links'))
  except Exception as e: print(e)
