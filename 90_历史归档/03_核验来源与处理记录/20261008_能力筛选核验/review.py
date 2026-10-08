import json,pathlib,re,sys
H=pathlib.Path(__file__).parent; D=json.loads((H/'input.json').read_text(encoding='utf8')); O=H.parent/'rebuild'
ids=sys.argv[1].split(',') if len(sys.argv)>1 else list(D['norm'])
ai=json.loads((O/'audit_all/attachment_index.json').read_text(encoding='utf8'))
for ident in ids:
 p=D['norm'][ident]; row=next(r for r in D['rows'] if r[0]==ident)
 print('\n###',ident,p['org'],p['lab'],'\nSHORT:',p['directions'],'\nURL:',p['url'])
 s=json.loads((O/'official'/f'{ident}.json').read_text(encoding='utf8'))
 t=s.get('text',''); t=re.sub(r'L\d+:\s*','',t)
 m=re.search(r'(?:一[、．.]|研究方向|资助方向|支持方向|指南内容|申报指南|研究内容|一、资助|主要研究)',t)
 if m:t=t[max(0,m.start()-120):]
 print(t[:int(sys.argv[2]) if len(sys.argv)>2 else 3800])
 ats=[a for a in ai if ident in a.get('ids',[]) and re.search('指南|办法|通知|管理',a.get('name',''))]
 for a in ats[:2]:
  print('ATTACHMENT:',a['name'],a['url'],a.get('status'),'\n',a.get('text','')[:3500])
