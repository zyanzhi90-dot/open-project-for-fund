import pathlib,json,re,collections
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/'audit_all'
data=json.load(open(ROOT/'normalized.json',encoding='utf8'))
patterns={
 'amount':r'\d\s*(?:[—–~～\-至]\s*\d+)?\s*万|资助额度|资助金额|支持强度|资助强度',
 'qualification':r'申请(?:人|者)(?:应|须|需|必须|要求|资格)|申报(?:人|者)(?:应|须|需|必须)|具有.{0,45}(?:博士|职称)|年龄.{0,30}(?:岁|周岁)|限.{0,8}(?:申报|申请)|不得.{0,15}(?:申请|申报)|(?:校内|校外|固定人员).{0,25}(?:不能|不得|不予|优先|不包括)|同期.{0,20}(?:主持|承担)|在研.{0,20}(?:不得|不超过|不能)',
 'collaboration':r'(?:固定|本实验室).{0,30}(?:合作|联合|联系|协同)|(?:联合|合作|共同).{0,20}(?:固定|本实验室|研究人员)|每年.{0,20}(?:来室|访问|到访|客座)|合作(?:制|人|者)|共同负责人',
 'funds':r'外拨|拨付|报销|结算|经费(?:使用|管理|用于|不|应|需|只能|主要)|经费用于|专款专用|不可购买设备|设备费|业务费|劳务费',
 'period':r'(?:研究|执行|资助|课题|项目).{0,10}(?:期限|周期|年限|起止)|起始(?:日期|时间)|完成(?:期限|时限)|资助期.{0,10}年',
 'outputs':r'(?:发表|录用|论文|专利|软件著作权|验收|考核|结题|标注|署名|第一完成单位|第一单位|中期|年度进展).{0,100}(?:篇|SCI|EI|CCF|要求|须|应|报告|实验室|至少|必须|不少于|科研|基金|资助|单位|专利)|研究成果.{0,40}(?:须|应|要求)',
 'ip':r'知识产权.{0,30}(?:归|共同|共有|共享|双方|属于|所有)|成果.{0,35}(?:归属|共有|共享|共同所有|归.{0,10}所有)|专利权人|产权归属',
 'materials':r'申请书.{0,100}(?:发送|提交|签|盖章|邮寄|纸质|份)|(?:签字|盖章|电子版|纸质|扫描件|Word|PDF).{0,100}(?:申请|寄|报送|提交|发送|份|邮箱)|(?:E-mail|电子信箱|联系邮箱|电子邮箱|邮箱|联系人|邮件主题|通讯地址|邮寄地址|通信地址).{0,160}',
}
result=[]
for p in data['projects']:
 s=json.load(open(ROOT/'official'/(p['id']+'.json'),encoding='utf8'))
 text=s.get('text','');sent=[x.strip() for x in re.split(r'(?<=[。；])|\n',text) if len(x.strip())>4]
 fields={}
 for k,pat in patterns.items():
  a=[]
  for x in sent:
   if re.search(pat,x,re.I) and x not in a and not re.search(r'^上一篇|^下一篇|版权所有|京ICP备|沪ICP备|^Copyright',x,re.I):a.append(x)
  fields[k]=a
 dates=[]
 for x in sent:
  if re.search('截止|受理时间|申报时限|申报时间|提交时间',x):dates.append(x)
 title=text.split('\n')[0] if text else ''
 result.append({'id':p['id'],'org':p['org'],'lab':p['lab'],'url':s['url'],'source_status':s['status'],'title':title,'dates':dates,'fields':fields,'text':text})
(OUT/'field_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
for b in range(0,len(result),8):
 blocks=[]
 for x in sorted(result,key=lambda x:x['id'])[b:b+8]:
  blocks.append(x['id']+' '+x['title']+'\n旧截止 '+str(next(p['date'] for p in data['projects'] if p['id']==x['id']))+'\n截止证据 '+json.dumps(x['dates'],ensure_ascii=False)+'\n'+ '\n'.join(k+'：'+' || '.join(v) for k,v in x['fields'].items()))
 (OUT/f'fields_{b//8:02d}.txt').write_text('\n\n'.join(blocks),encoding='utf8')
print('项目字段证据',len(result))
