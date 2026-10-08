import json,pathlib,sys,re
H=pathlib.Path(__file__).parent;D=json.loads((H/'prepared.json').read_text(encoding='utf8'))
mode=sys.argv[1] if len(sys.argv)>1 else 'current'
for p in D['projects']:
 if mode=='current' and not p['status'].startswith(('日期未过','截止待确认')):continue
 if mode=='others' and p['status'].startswith(('日期未过','截止待确认')):continue
 if mode not in ['current','others','all'] and p['id'] not in mode.split(','):continue
 print('\n'+p['id'],p['org'],p['lab'],p['date'],p['amount'],p['status'])
 for col,title,length in [(10,'资格',220),(11,'合作',200),(12,'经费',330),(13,'周期',120),(14,'成果',380),(32,'IP',150)]:print(title,p['details'][col][:length])
 print('待核',p['missing'])
