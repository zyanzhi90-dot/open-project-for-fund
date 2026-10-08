import pathlib,json,sys,re
sys.stdout.reconfigure(encoding='utf-8')
H=pathlib.Path(__file__).parent/'sources'
for p in H.glob('*.json'):
 d=json.loads(p.read_text(encoding='utf8'))
 if len(sys.argv)>1 and not any(q in d['url'] for q in sys.argv[1:]):continue
 print('\nURL',d['url'],'STATUS',d['status'])
 print(d.get('text','')[:24000])
 print('KEY LINKS',json.dumps([x for x in d.get('links',[]) if re.search('开放|基金|研究|科研|平台|指南|附件|课题|实验室|lab|cent|project|fund',x['label'],re.I)],ensure_ascii=False))
