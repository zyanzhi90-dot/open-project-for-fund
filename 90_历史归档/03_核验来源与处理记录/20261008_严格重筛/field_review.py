import json,pathlib,re
H=pathlib.Path(__file__).parent; B=H.parent/'20261008_最终收尾'
D=json.loads((B/'prepared_final.json').read_text(encoding='utf8'))
dec={a[0]:a[1:] for a in [x.split('\t') for x in (H/'decisions.tsv').read_text(encoding='utf8').splitlines()]}
patterns=[r'博士|职称|申请人|申请者|Eligibility',r'合作|联合|来室|访问|collaborat',r'外拨|拨款|划拨|经费管理|经费使用|报销|funding',r'研究周期|研究期限|执行期|两年|2年|duration',r'结题|论文|成果要求|成果管理|publication',r'知识产权|成果归|成果由|成果属|共有|共享|Intellectual',r'材料|提交|邮箱|申请书|application']
for p in D['projects']:
 if dec[p['id']][0]=='剔除':continue
 S=json.loads((B/'sources'/f"{p['id']}.json").read_text(encoding='utf8'))['sources']; seen=set(); ts=[]
 for q in S:
  t=q.get('text',''); z=re.sub(r'\s+',' ',t)
  if z in seen:continue
  seen.add(z);ts.append((q['url'],z))
 out=[]
 for i,v in enumerate(p['fields']):
  if re.search('未公开|未明确|未公布|未载明|未取得|须确认|待确认|需确认|须读取',v):
   hits=[]
   for u,t in ts:
    for m in list(re.finditer(patterns[i],t,re.I))[:3]:
     x=t[max(0,m.start()-40):m.start()+260]
     if x not in hits:hits.append(x)
   out.append((D['detail_header'][10+i],v,hits[:3]))
 if out:
  print('\n###',p['id'],p['lab']);print(json.dumps(out,ensure_ascii=False))
