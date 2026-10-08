import pathlib,json,re,ast,copy,collections,hashlib,datetime
H=pathlib.Path(__file__).parent; O=H.parent/'rebuild'; ROOT=H.parents[2]
D=json.loads((H/'input.json').read_text(encoding='utf8')); C=json.loads((H/'decisions.json').read_text(encoding='utf8'))
manual={}; date_overrides={}; amounts={}
# Read the prior manually sourced corrections without executing the former evaluator.
tree=ast.parse((O/'finalize_audit.py').read_text(encoding='utf8'))
for node in tree.body:
 if isinstance(node,ast.Assign):
  for t in node.targets:
   if isinstance(t,ast.Name) and t.id in ['manual','date_overrides','amounts']:
    try:globals()[t.id]=ast.literal_eval(node.value)
    except:pass
for ident,v in amounts.items():manual.setdefault(ident,{})['amount']=v
for node in ast.walk(ast.parse((O/'prepare_data.py').read_text(encoding='utf8'))):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='patch':
  try:ident=ast.literal_eval(node.args[0]);vals={x.arg:ast.literal_eval(x.value) for x in node.keywords}
  except:continue
  for k,v in vals.items():
   if k in ['qualification','collaboration','funds','period','outputs','ip','materials','amount']:manual.setdefault(ident,{}).setdefault(k,v)
  if vals.get('date'):date_overrides.setdefault(ident,vals['date'])
newmanual=json.loads((H/'corrections.json').read_text(encoding='utf8')) if (H/'corrections.json').exists() else {}
for ident,v in newmanual.items():manual.setdefault(ident,{}).update(v)
date_overrides.update({'M004':'2026-07-19','M019':'2026-07-25','M055':'2026-01-31','M073':'2026-05-31','M047':'2022-10-30','D-GZU-001':'2025-06-26'})
PAT={
 'qualification':r'申请人.{0,50}(?:博士|职称|年龄|要求|条件)|申请者.{0,50}(?:博士|职称|年龄|相关)|(?:博士|副高|中级|高级).{0,60}(?:申请|人员|学位|职称)|不得.{0,30}(?:申请|申报)|限项|只能申请|同年.{0,30}申请|eligib|applicants?.{0,80}(?:degree|doctor|professor)',
 'collaboration':r'(?:固定|本实验室).{0,40}(?:联合|合作|参与|成员)|(?:联合|合作|共同|联系人员).{0,35}(?:固定|本室|实验室|研究人员|校内人员)|实验室在职.{0,20}联合|(?:每年|至少|需).{0,25}(?:来室|赴|访问|交流)|合作者|collaborator|full.time.{0,30}faculty',
 'funds':r'外拨|不划拨|划拨|拨付|报销|核销|结算|经费(?:管理|使用|支出|主要用于|用于|分配|需|应)|设备费|业务费|劳务费|funds?.{0,40}(?:use|transfer|administer)',
 'period':r'(?:研究|执行|资助|课题|项目|实施).{0,15}(?:期限|周期|年限|起止)|资助期|起始(?:日期|时间)|duration|commence',
 'outputs':r'(?:论文|成果|专利|验收|结题|署名|标注|考核指标).{0,90}(?:篇|SCI|EI|CCF|要求|须|应|报告|不少于|至少|第一|第二|单位|包括)|第一完成单位|第一署名单位|acknowledg|publications?',
 'ip':r'(?:知识产权|知識產權|专利权|成果).{0,60}(?:归属|归|共有|共同所有|共同拥有|共享|所有权)|intellectual property.{0,90}(?:own|vest)|co.owned',
 'materials':r'申请书.{0,100}(?:发送|提交|签|盖章|邮寄|纸质|份)|(?:签字|盖章|电子版|纸质|扫描件|PDF).{0,90}(?:申请|寄|报送|提交|发送|份)|邮箱|联系人|邮件主题|邮寄地址|通信地址|[a-z0-9._+-]+@[a-z0-9.-]+\.[a-z]{2,}',
 'amount':r'资助.{0,30}(?:万元|港元|澳门|澳門)|每(?:项|个).{0,30}(?:万元|万港元)|grant.{0,30}(?:HKD|MOP|RMB)|maximum.{0,45}grant',
}
LABEL={'qualification':'申请资格','collaboration':'合作与访问','funds':'经费使用及外拨','period':'周期','outputs':'成果及署名','ip':'知识产权','materials':'提交材料及方式','amount':'金额'}
def clean(t):
 t=re.sub(r'L\d+:\s*','',t);t=re.sub(r'cite[^]*','',t)
 t=re.split(r'上一篇|下一篇|上一条|下一条|版权所有|Copyright|常用链接|友情链接|快速通道',t,flags=re.I)[0]
 # Remove presentation metadata and leave original clause boundaries intact.
 t=re.sub(r'^.*?(?:Total lines: \d+|\[wordlim \d+\])\s*','',t,flags=re.S) if 'Total lines:' in t else t
 t=t.replace('&emsp;','').replace('\u3000',' ')
 starts=[m.start() for m in re.finditer(r'一[、．.]\s*(?:开放|课题|申请|资助|研究|总则|全国|实验室|主要|申报|指南|支持)',t)]
 if starts:t=t[starts[0]:]
 t=re.sub(r'([。；])',r'\1\n',t)
 t=re.sub(r'([一二三四五六七八九十]+、)',r'\n\1',t)
 return t
def clauses(t):
 seq=[re.sub(r'\s+',' ',x).strip() for x in clean(t).splitlines() if x.strip()]
 return [x for x in seq if len(x)>8 and not re.search('^Published:|^Crawled:|^导航|^首页|^发布时间',x)]
def extract(sources,key):
 hits=[]; refs=[]
 for s in sources:
  if re.search('上一篇|下一篇|上一条|下一条|信息公开指南|办事指南',s['kind']):continue
  # A form may contain mandatory statements; examples and blanks cannot establish an actual requirement.
  if re.search('申请表|申请书',s['kind']) and not re.search('指南|管理|通知',s['kind']):continue
  if re.search('申请书|申请表',s['text'][:350]) and not re.search('正文',s['kind']) and not re.search('指南|办法',s['text'][:350]):continue
  if '办事指南' in s['kind']:continue
  if not s.get('live') and any(x.get('live') and x['url']==s['url'] for x in sources):continue
  content=s['text']
  if re.search(r'\.pdf(?:\?|$)',s['url'],re.I):content=content.replace('\n','')
  cs=clauses(content)
  for i,c in enumerate(cs):
   if key=='outputs' and re.search('考核指标示例|证明材料|研究积累|申请人需',c):continue
   if key=='period' and '生命周期' in c and not re.search('资助|研究周期|执行期限',c):continue
   if re.search('网站首页|SKL English|顶部导航|国家知识产权局国家|浏览次数',c) and len(c)>200:continue
   if re.search(PAT[key],c,re.I):
    if key=='funds' and len(c)<32 and not re.search('外拨|不划拨|报销|拨付|用途|用于',c):continue
    # A heading is not a fact; include its immediately following substantive clause.
    if len(c)<35 and c.endswith(('要求','条件','管理','：')) and i+1<len(cs):c+=' '+cs[i+1]
    if c not in hits:hits.append(c);refs.append(s['url'])
 return hits,list(dict.fromkeys(refs))
def shortmoney(ident,s):
 compact={'M148':'一般≤10万元；重点≤15万元','M025':'≤10万元','M098':'原则10万元','M017':'普通4—8万元','M084':'校外1万元','M127':'2万元','M126':'待核','M019':'待核（单项）','M122':'6—8万港元','M007':'一般5万元；重点10万元','M106':'2—4万元','M008':'30—90万元','F002':'一般经费5—25万元；重点经费25—100万元'}
 if ident in compact:return compact[ident]
 if ident=='M142':return '一般1—2万元'
 # First use the already concise six-column value, then update from actual corrections.
 if ident in newmanual and 'home_amount' in newmanual[ident]:return newmanual[ident]['home_amount']
 if ident=='M055':return '3—5万元'
 if ident=='M073':return '≤8万元'
 oldhome=next((r for r in D['raw']['01申报总览'][1:] if r[2].startswith(D['norm'][ident]['org']+'·') and r[1]==next(x for x in D['rows'] if x[0]==ident)[4]),None)
 # ID keyed original homepage archive removes ambiguity between calls from one laboratory.
 row=next(x for x in D['rows'] if x[0]==ident)
 try:original=json.loads(row[30]);rawamount=original[6]
 except:rawamount=row[9]
 olddis=json.loads((H.parent/'display/data.json').read_text(encoding='utf8'))
 cached=next((x['row'][4] for x in olddis['records'] if x['id']==ident),'待核')
 if ident in newmanual and 'amount' in newmanual[ident]:
  v=newmanual[ident]['amount'];return re.split('；执行|；研究|；拟|；当期',v)[0].strip('。 ')
 cached=re.sub(r'（[^）]*）|\([^)]*\)','',cached)
 cached=re.sub(r'/[12]年|，拟[^；]*|，[^；]*(?:项目|评审|方向|限制)[^；]*','',cached).strip('。； ')
 return cached
def state(ident,date,pending=False):
 if ident in ['M006','M049','M056','M064','M069','M074','M128','M166','M187']:return '当期受理待核'
 if ident=='M047':return '历史已截止·当期待核'
 if date and date<'2026-10-08':return '已截止'
 if pending:return '条件待核'
 if date=='2026-10-08':return '截止待确认'
 if date and date>'2026-10-08':return '日期未过·待确认'
 return '截止日期待核'
familiar=['南京信息工程大学','澳门大学','香港理工大学','华南理工大学','中国科学院自动化研究所','西北工业大学','重庆大学']
regions=['P0 南京及周边','P0 澳门','P0 香港','P0 广州及周边','P1 北京及周边','P1 西安及周边','P1 重庆']
projects=[]; logs=[]
for oldrow in D['rows']:
 ident=oldrow[0]
 if ident in C['exclude']:continue
 p=copy.deepcopy(D['norm'][ident]);record=copy.deepcopy(oldrow);bundle=json.loads((H/'sources'/f'{ident}.json').read_text(encoding='utf8'));sources=[s for s in bundle['sources'] if not re.search('上一篇|下一篇|上一条|下一条|信息公开指南|办事指南',s['kind'])]
 if ident=='M073':p['region']='P0 南京及周边'
 # Pages labelled as awards, platform/news or suggestions cannot establish current-call fields.
 mechanism=ident in ['M006','M049','M056','M064','M069','M074','M128','M166','M187']
 missing=[];facts={};byrefs={}
 for key in PAT:
  hits,refs=extract(sources,key)
  if mechanism:
   v='当期'+LABEL[key]+'待核。'
   if hits:v+='\n历史/机制资料参考：'+'\n'.join(hits)[:2200]
   missing.append(LABEL[key])
  elif key in manual.get(ident,{}):v=manual[ident][key]
  elif hits:
   v='\n'.join(hits)
   if len(v)>4500:v=v[:4500]+'\n其余条款见官方指南。'
  else:v='未在已取得官方资料中明确；待实验室确认。';missing.append(LABEL[key])
  if re.search('未明确|未公开|未公布|未确认|未取得|未明示|未说明|尚待|待核|待确认|须确认|需.*确认|需.*核实',v):missing.append(LABEL[key])
  # Treat no numerical output as unconfirmed, not as absence of a deliverable burden.
  if key=='outputs' and not re.search(r'\d+\s*篇|[一二三四五]+篇|至少|不少于|以.*任务书|统一论文|未规定统一|未公布统一|具体.*要求',v):missing.append('具体成果数量/任务书')
  if key=='funds' and not re.search('外拨|划拨|拨付|拨至|拨到|不划拨|仅限.{0,20}财务|凭.*发票|统一.*管理|拨款',v):missing.append('外拨安排')
  if key=='period' and not re.search(r'\d+\s*(?:年|个月|月)|[一二三四五两]+年',v):missing.append('具体执行起止/时长')
  facts[key]=v;byrefs[key]=refs or [s['url'] for s in sources]
  logs.append([ident,LABEL[key],v,'\n'.join(byrefs[key]),'2026-10-08','当期未核' if mechanism else '有条款；缺项待核' if LABEL[key] in missing else '官方条款/指南'])
 date=date_overrides.get(ident)
 if ident in newmanual and 'date' in newmanual[ident]:date=newmanual[ident]['date']
 if not date and isinstance(oldrow[4],str) and re.fullmatch(r'20\d\d-\d\d-\d\d',oldrow[4]):date=oldrow[4]
 if mechanism:date=None
 topic=C['themes'].get(ident,p['directions'])
 topic=re.sub(r'；但.*|；曾.*|；.*(?:申请书|超声机器人)|、.*(?:拟申请书|匹配低)|（仅算法间接）','',topic)
 topic=re.sub(r'^(?:方向/边界：|与申请书的匹配方向：)','',topic).replace('；','、')
 if len(topic)>44:topic='、'.join(re.split('[、；]',topic)[:3])[:44]
 basis=C['pending'].get(ident,'可承担'+topic+'相关的感知、建模、学习、优化或控制任务；选题须满足公告规定的应用对象与验证条件。')
 if ident in newmanual and 'basis' in newmanual[ident]:basis=newmanual[ident]['basis']
 decision='待核适合程度' if ident in C['pending'] else '适合承担（限定所列方向）'
 status=state(ident,date,ident in C['pending'])
 if ident in ['M038','M175']:status='资格待核' if status!='已截止' else '已截止·资格受限'
 if ident in ['F003','F004']:status+='（基金专项）'
 recommendation=newmanual.get(ident,{}).get('recommendation','')
 if not recommendation:
  concerns=[]
  if re.search('不外拨|不划拨|不能外拨|不允许.*外拨|经费仅限',facts['funds']):concerns.append('经费在对方结算，先确认可报销支出与流程')
  if re.search('第一(?:完成|署名|单位)|第一标注单位',facts['outputs']):concerns.append('需接受对方第一单位署名')
  if re.search('授权.{0,10}专利|专利.{0,10}授权',facts['outputs']):concerns.append('授权专利等成果要求须量力评估')
  if missing:concerns.append('补清'+ '、'.join(list(dict.fromkeys(missing))[:4]))
  recommendation=('下年度储备；' if status.startswith('已截止') else '先确认申报资格和受理；')+'；'.join(concerns or ['按合作人和任务书落实情况决定'])
 cooperation=newmanual.get(ident,{}).get('relationship','')
 if not cooperation:
  org=p['org']
  cooperation=('本校现职' if org=='南京信息工程大学' else '澳门大学博士，陈俊龙合作圈；尚未指定本室固定合作者' if org=='澳门大学' else '杨晨光合作圈；尚未指定本室固定合作者' if org=='香港理工大学' else '华南理工硕士；尚未指定本室固定合作者' if org=='华南理工大学' else '有熟人；尚未指定本室固定合作者' if org in familiar else '未提供本机构合作人；需落实')
 if not date:missing.append('正式截止/当期受理')
 if ident in C['pending']:missing.insert(0,C['pending'][ident])
 failed=[a for a in bundle.get('attempts',[]) if a.get('name') and re.search('指南|管理办法|制度|条例',a.get('name','')) and not any(s['url']==a['url'] for s in sources)]
 if failed:missing.append('未读取附件/细则：'+'、'.join(a['name'] for a in failed if not re.search('上一篇|下一篇|信息公开|办事',a['name'])))
 issues='；'.join(dict.fromkeys(missing+['合作/实验条件能否落实','本人限项与年龄条件（如适用）']))
 # Update only facts and their directly affected interpretations; preserve lineage columns.
 record[4]=date or '待核';record[5]=status;record[6]=decision;record[7]=topic;record[8]=basis
 for key,col in [('amount',9),('qualification',10),('collaboration',11),('funds',12),('period',13),('materials',15)]:record[col]=facts[key]
 record[14]=facts['outputs'];record[16]=bundle['url'];record[17]='\n'.join(dict.fromkeys(s['url'] for s in sources[1:]));record[18]='本轮正文已读取' if any(s['live'] for s in sources) else '本轮读取官方存档；在线访问受限/失败'
 record[19]='已读取'+str(sum('正文' not in s['kind'] for s in sources))+'份指南/规则资料；见核验日志'
 record[20]='2026-10-08';record[21]=issues
 record[27]=oldrow[6]
 year=p.get('year','待核')
 if ident=='M165':year='2026—2027'
 if ident=='M152':year='2027'
 if ident in ['M008','M009','M039']:year='2026'
 if ident=='M047':year='2022历史批次；当期待核'
 record += [facts['ip'],cooperation,recommendation,year,json.dumps(oldrow[:26],ensure_ascii=False),p['region']]
 region=p['region']
 if p['org']=='哈尔滨理工大学':region='P2 黑龙江·哈尔滨'
 proj={'id':ident,'org':p['org'],'lab':p['lab'],'region':region,'date':date,'status':status,'topic':topic,'amount':shortmoney(ident,facts['amount']),'url':bundle['url'],'details':record,'basis':basis,'recommendation':recommendation,'missing':issues,'sources':len(sources),'fresh':any(s['live'] for s in sources),'pendingfit':ident in C['pending']}
 if not re.search(r'\d',proj['amount']):proj['amount']='待核'
 if mechanism:proj['amount']='待核'
 projects.append(proj)
 logs.append([ident,'截止日期与受理状态',(date or '待核')+'；'+status,bundle['url'],'2026-10-08','以公告截止日期为准；资格与是否受理分别核实'])
 logs.append([ident,'承担适合程度与申报价值',basis+'\n'+recommendation,bundle['url'],'2026-10-08',decision])
orgregion={}
def orgkey(org):
 return '上海交通大学' if org.startswith('上海交通大学') else org
for p in projects:
 p['org_key']=orgkey(p['org'])
 rank=(regions.index(p['region']) if p['region'] in regions else 7 if '长三角' in p['region'] else 8 if '粤港澳' in p['region'] else 9,p['region'])
 if p['org_key'] not in orgregion or rank<orgregion[p['org_key']]:orgregion[p['org_key']]=rank
def sortkey(p):
 bucket=2 if p['status'].startswith('已截止') else 0 if p['status'].startswith(('日期未过','截止待确认')) else 1
 return (*orgregion[p['org_key']],familiar.index(p['org_key']) if p['org_key'] in familiar else 99,p['org_key'],bucket,p['date'] or '9999',p['id'])
projects.sort(key=sortkey)
header=D['raw']['02项目完整详情'][5]
header[6]='研究适合程度';header[7]='适合承担的方向';header[8]='承担理由与应用限制';header[12]='经费使用及外拨';header[14]='成果数量及署名';header[27]='原匹配优先级'
header += ['知识产权','本人合作基础','申报价值与建议','项目年度','原详情记录（筛选前）','地域排序分组']
excluded=[[r[0],r[2],r[3],C['exclude'][r[0]],r[16]] for r in D['rows'] if r[0] in C['exclude']]
logs += [[x[0],'剔除理由',x[1]+'·'+x[2]+'：'+x[3],x[4],'2026-10-08','从当前候选及详情剔除；原记录保留'] for x in excluded]
coverage=copy.deepcopy(D['raw']['03机构检索覆盖'])
for row in coverage[6:]:
 if row[1] in familiar:
  org=row[1];ps=[p for p in projects if p['org']==org];es=[x for x in excluded if x[1]==org]
  row[3]='南京信息工程大学现职' if org==familiar[0] else '澳门大学博士；陈俊龙相关合作圈' if org==familiar[1] else '杨晨光相关合作圈' if org==familiar[2] else '华南理工大学硕士' if org==familiar[3] else '用户说明有熟人；尚未指定本室固定合作者'
  row[4]='本轮核验台账已有记录：保留'+str(len(ps))+'条，剔除'+str(len(es))+'条。\n'+'\n'.join(dict.fromkeys([p['url'] for p in ps]+[x[4] for x in es]))
  row[5]='保留项目的具体待核条款见完整详情；本轮未扩展机构/地域检索，全面覆盖进度沿用上轮。熟悉合作圈不等于已落实固定合作者。'
core=[r for r in coverage[6:] if r[1] in familiar]
core.sort(key=lambda r:familiar.index(r[1]))
positions=[i for i in range(6,len(coverage)) if coverage[i][1] in familiar]
for i,r in zip(positions,core):coverage[i]=r
data={'source':D['source'],'source_hash':D['hash'],'projects':projects,'detail_header':header,'coverage':coverage,'log_header':['项目编号','核验字段','已取得条款','官方证据URL','核查日期','核验状态'],'logs':logs,'excluded':excluded,'stats':{'original':len(D['rows']),'retained':len(projects),'excluded':len(excluded),'pending_fit':sum(p['pendingfit'] for p in projects),'fresh':sum(p['fresh'] for p in projects),'states':dict(collections.Counter(p['status'] for p in projects))}}
(H/'prepared.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(H/'review_retained.txt').write_text('\n\n'.join(f"{p['id']} {p['org']} {p['lab']}\n{p['status']} {p['date']} {p['topic']} {p['amount']}\n资格：{p['details'][10][:250]}\n合作：{p['details'][11][:180]}\n经费：{p['details'][12][:350]}\n周期：{p['details'][13][:150]}\n成果：{p['details'][14][:400]}\nIP：{p['details'][32][:180]}\n待核：{p['missing']}" for p in projects),encoding='utf8')
print(json.dumps(data['stats'],ensure_ascii=False))
