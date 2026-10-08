import json,pathlib,re,sys
H=pathlib.Path(__file__).parent; B=H.parent/'20261008_最终收尾'
D=json.loads((B/'prepared_final.json').read_text(encoding='utf8'))
def sources(p):
 return json.loads((B/'sources'/f"{p['id']}.json").read_text(encoding='utf8'))
def directions(t):
 # Locate source passages for human review; never use matches as a retention decision.
 t=re.sub(r'\n{3,}','\n\n',t)
 anchors=list(re.finditer(r'重点资助领域|资助方向|研究方向|研究领域|课题指南|开放课题指南|研究内容|申报指南|征集方向',t))
 chunks=[]
 for m in anchors[:5]:
  a=max(0,m.start()-60); b=min(len(t),m.start()+1800)
  if not any(a>=x[0] and a<x[1] for x in chunks):chunks.append((a,b))
 if not chunks:chunks=[(0,min(len(t),1800))]
 return '\n[…]\n'.join(t[a:b] for a,b in chunks)[:2800]
if __name__=='__main__':
 a,b=map(int,sys.argv[1:3]);
 for p in D['projects'][a:b]:
  print('\n###',p['id'],p['org'],p['lab'],'\n原摘要:',p['topic'])
  s=sources(p)
  seen=set(); parts=[]
  for q in s['sources']:
   if q['url'] in seen:continue
   seen.add(q['url']); t=q.get('text','')
   hits=list(re.finditer(r'机器人|具身|人机|无人|自主导航|灵巧|机械臂|运动控制|柔性执行|研究方向|资助方向|重点资助领域|研究领域',t))
   excerpts=[]
   for m in hits:
    if any(abs(m.start()-z)<100 for z in excerpts):continue
    excerpts.append(m.start())
   txt=' / '.join(re.sub(r'\s+',' ',t[max(0,z-50):z+170]) for z in excerpts[:5]) or re.sub(r'\s+',' ',directions(t))[:400]
   parts.append((q['url'],txt))
  direct=[]; general=[]
  for q in s['sources']:
   t=q.get('text','');
   # Evidence snippets are only review aids; all decisions are entered explicitly.
   for m in re.finditer(r'机器人|具身|自主导航|灵巧|机械臂|人机交互|无人系统|无人装备',t):
    v=re.sub(r'\s+',' ',t[max(0,m.start()-55):m.start()+200])
    if v not in direct:direct.append(v)
   for m in re.finditer(r'(?:一、|二、|三、|1[.．、]|（一）|\(一\)).{0,12}(?:研究方向|资助方向|资助领域|研究内容)|方向[一二三四五六七八九十][:：]',t):
    v=re.sub(r'\s+',' ',t[m.start():m.start()+1100])
    if v not in general:general.append(v)
  print('TASK EVIDENCE:', (' / '.join(direct[:3])+' / '+(' / '.join(general[:1])))[:650] if direct or general else (' / '.join(txt for _,txt in parts))[:650])
  print('来源数',len(s['sources']),'缺口:',p['gaps'])

