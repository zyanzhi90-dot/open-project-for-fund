import pathlib,json,re,copy,collections,hashlib,math
H=pathlib.Path(__file__).parent; B=H.parent/'20261008_最终收尾';ROOT=H.parents[2]
D=json.loads((B/'prepared_final.json').read_text(encoding='utf8'))
dec={a[0]:a[1:] for a in [x.split('\t') for x in (H/'decisions.tsv').read_text(encoding='utf8').splitlines()]}
fix=json.loads((H/'field_corrections.json').read_text(encoding='utf8'))
assert len(dec)==len(D['projects'])==166
labels=['申请资格','合作及访问','经费使用及外拨','研究周期','成果数量及署名','知识产权','材料及提交方式']
supp=json.loads((H/'sources/F004.json').read_text(encoding='utf8'))
pm={};audits=[];logs=[];prior=copy.deepcopy(D['projects']);new_excluded=[]
missing=re.compile(r'未公开|未明确|未公布|未载明|未取得|须确认|待确认|需确认|须读取|待核|须取得|尚须|仍须|未知')
def uniqtext(v):
 seen=set(); out=[]
 for line in v.splitlines():
  if not line.strip():continue
  key=re.sub(r'\s+','',line)
  if key not in seen:seen.add(key);out.append(line)
 return '\n'.join(out)
def official_sources(p):
 s=json.loads((B/'sources'/f"{p['id']}.json").read_text(encoding='utf8'))
 chosen=[];seen=set()
 for q in s['sources']:
  if not q.get('text') or q['url'] in seen:continue
  if p['id']=='M107' and '62583' in q['url']:continue
  if p['id']=='M011' and '/202506/' in q['url']:continue
  if p['id']=='M080' and '粮油' in q.get('kind',''):continue
  if p['id']=='M194' and ('2025年' in q.get('kind','') or '756848' in q['url']):continue
  seen.add(q['url']);chosen.append(q)
 if p['id']=='F004':chosen.extend(supp['sources'])
 return chosen,s
def evidence(qs,pattern):
 # Locate supporting passages, not automatic decisions or inferred requirements.
 out=[]
 for q in qs:
  t=q.get('text','');cut=t.find('正文')
  if cut>=0:t=t[cut:]
  t=re.split(r'上一篇[:：]|下一篇[:：]|上一条[:：]|下一条[:：]|上一页[:：]|下一页[:：]',t)[0]
  for m in list(re.finditer(pattern,t,re.I))[:2]:
   quote=re.sub(r'\s+',' ',t[max(0,m.start()-45):m.start()+220])
   if quote not in [x['摘录'] for x in out]:out.append({'url':q['url'],'摘录':quote})
  if len(out)>=3:break
 return out[:3]
patterns=[r'博士|职称|申请人|申请者|Eligibility',r'合作|联合|访问|collaborat',r'外拨|拨款|划拨|经费|报销|funding',r'研究周期|研究期限|执行期|两年|2年|duration',r'结题|论文|成果要求|成果管理|publication',r'知识产权|成果归|成果由|成果属|共有|共享|Intellectual',r'提交|邮箱|申请书|application']
for old in prior:
 p=copy.deepcopy(old);ident=p['id']; decision,reason=dec[ident];p['screen_decision']=decision;p['screen_reason']=reason
 qs,s=official_sources(p);p['sources']=[q['url'] for q in qs]
 for i,v in enumerate(p['fields']):
  v=fix.get(ident,{}).get(str(i),v)
  v=uniqtext(v).replace('官方未公开｜','公开资料未载明｜').replace('删除原混入粮油仓储实验室的条款。','')
  if v.startswith('官方明确｜') and missing.search(v):v=v.replace('官方明确｜','已核条款（仍有缺口）｜',1)
  p['fields'][i]=v
 if ident=='M100':
  blocked='资料未取得｜公告附件1指南、附件3管理办法下载入口需验证码；本轮网页工具已验证。须由实验室提供可读附件，不能据未下载判断条款未公开。'
  for i in [0,1,2,3,5]:p['fields'][i]=blocked+'\n待核字段：'+labels[i]+'。'
  p['fields'][4]='已核条款（仍有缺口）｜执行至周期一半交中期报告，研究结束后3个月内交结题报告；具体论文、专利与成果署名须取得受验证码限制的指南及办法。'
  p['fields'][6]='已核条款（仍有缺口）｜公告截止2026年10月30日17:00；具体申请材料、提交邮箱及纸质要求在受验证码限制的附件中，尚未取得。'
  p['amount']='未取得指南·金额待核';p['amountlong']=p['amount']
  p['sources']+=['https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041515','https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041517']
 if ident in ['F003','F004']:
  p['kind']='其他资助·正式指南发布通告';p['status']='完整指南/窗口待核'
  if ident=='F004':p['url']='https://www.nsfc.gov.cn/p1/3381/2824/142425.html'
  p['fields']=['资料未取得｜正式通告要求登录GRANTS查看完整指南；该字段尚未核清。字段：'+f for f in labels]
  p['fields'][6]='官方明确｜依托单位和申请人登录https://grants.nsfc.gov.cn，在“项目管理—项目指南”模块查看完整指南，按指南要求申请。具体材料未取得。'
 if decision=='保留':p['topic']=reason
 elif decision=='待核':
  p['topic']='方向待核：'+reason
  if not ident.startswith('F'):
   p['status']='方向待核·已截止' if p['date'] and p['date']<'2026-10-08' else '方向及窗口待核' if not p['date'] else '方向待核·公告已发布'
  elif ident=='F001':p['status']='方向待核·公告已发布'
 else:p['status']='已剔除·范围不符'
 p['personal']='已知背景：南京信息工程大学现职、博士。个人条件、在研限项及实际合作人尚未逐项确认；须按公告条款核对，受理窗口状态不代表可申请。'
 gaps=[]
 if decision=='待核':gaps.append('筛选/证据缺口：'+reason)
 if not p['date']:gaps.append('截止时间：未取得或未核实当期正式受理窗口；不得推算。')
 elif p['date']=='2026-10-08':gaps.append('截止时间：公告截止为核查当天，未载明北京时间时点；不能认定仍可提交，须联系确认。')
 for i,v in enumerate(p['fields']):
  if missing.search(v):
   # Keep actionable field-level gaps without copying the entire long clause again.
   text=re.split(r'｜',v,maxsplit=1)[-1]
   gaps.append(labels[i]+'：'+(text if len(text)<150 else '部分条款已核，尚有未明确项；具体缺口见对应条款列，向实验室确认。'))
 if missing.search(p['amount']):gaps.append('资助金额：'+p['amount'])
 if ident=='M032':gaps.append('依托机构：当前为高校科研处转载，实验室具体依托机构和正式原始公告尚待确认。')
 p['gaps']='\n'.join(gaps) or '本轮复读的公开公告/已取得附件中未发现新增条款缺口；个人资格及合作条件仍须逐项确认。'
 p['value']='完整经费条款见M列，成果要求见O列，知识产权见P列。\n待核：'+('、'.join(labels[i] for i in [2,4,5] if missing.search(p['fields'][i])) or '上述公开条款暂未发现缺口，具体以任务书为准。')
 if ident=='M137':p['contact']='李老师；025-84346211；kjc211@163.com'
 if ident=='M032':p['contact']='方向4：陈老师13260126003；提交：司老师19713044256，sklicmsc@163.com'
 if ident=='M194':p['contact']='zhangwj@nju.edu.cn；83592756'
 p['relation']=re.sub(r'适合承担[^。\n]*','',p.get('relation',''))
 # Preserve source category, source URLs and the prior original-ID merge.
 row=p['details'];row[1]=p['kind'];row[4]=p['status'];row[8]=p['topic'];row[9]=p['amountlong'] or p['amount'];row[10:17]=p['fields'];row[17]=p['personal'];row[18]=p['gaps'];row[19]=p['url'];row[20]='\n'.join(dict.fromkeys(p['sources']));row[21]='2026-10-08（北京时间；截止日当天时点未明示的转待核）';row[23]=p['value'];row[25]=p['contact']
 # Record every independently screened entry and all required fields, including excluded records.
 fieldvals=[('实际任务筛选',decision+'｜'+reason),('正式公告/指南',p['kind']+'｜'+('完整指南或本期公告未取得/待核' if old['kind']=='线索' or ident in ['F003','F004'] else '已复读原官方公告；附件缺口见条款列')),('截止日期',str(p['date'] or '未取得')+'；北京时间时点：'+str(p.get('time') or '未公开/未取得')),('资助金额',p['amount'])]+list(zip(labels,p['fields']))
 fa=[]
 for name,value in fieldvals:
  idx=labels.index(name) if name in labels else None
  quotes=evidence(qs,patterns[idx]) if idx is not None else []
  urls='\n'.join(dict.fromkeys([x['url'] for x in quotes])) or p['url']
  state='未核清/有缺口' if missing.search(value) else '已复读已取得证据'
  logs.append([ident,name,value,urls,'2026-10-08',state,decision,p['status']])
  fa.append({'字段':name,'最终值':value,'状态':state,'支持片段':quotes,'复用来源':[q['url'] for q in qs]})
 audit={'id':ident,'aliases':p['aliases'],'decision':decision,'reason':reason,'original_topic':old['topic'],'final_topic':p['topic'],'original_status':old['status'],'final_status':p['status'],'source_files':[str(B/'sources'/f'{ident}.json')]+([str(H/'sources'/f'{ident}.json')] if (H/'sources'/f'{ident}.json').exists() else []),'fields':fa,'contact':p['contact'],'gaps':p['gaps']}
 audits.append(audit);pm[ident]=p
 if decision=='剔除':new_excluded.append([ident,p['org'],p['lab'],'已剔除·范围不符',reason,p['url'],'2026-10-08'])
rank={'P0 南京及周边':0,'P0 澳门':1,'P0 香港':2,'P0 广州及周边':3,'P1 北京及周边':4,'P1 西安及周边':5,'P1 重庆':6}
key=lambda p:(rank.get(p['region'],7),p['date'] or '9999-99-99',p['org'],p['id'])
survivors=[p for p in pm.values() if p['screen_decision']!='剔除']
home=sorted([p for p in survivors if p['screen_decision']=='保留' and p['kind']=='正式开放课题公告' and p['date'] and p['date']>'2026-10-08' and not p['id'].startswith('F')],key=key)
hist=sorted([p for p in survivors if p['screen_decision']=='保留' and p['date'] and p['date']<'2026-10-08' and not p['id'].startswith('F')],key=key)
other=sorted([p for p in survivors if p['id'].startswith('F')],key=key)
used={p['id'] for p in home+hist+other};pending=sorted([p for p in survivors if p['id'] not in used],key=key)
survivors=home+pending+hist+other
assert len({p['id'] for p in survivors})==len(survivors)
for p in home:p['status']='受理中·条件待核';p['details'][4]=p['status']
for r in D['coverage'][6:]:
 if isinstance(r[4],str):
  r[4]='\n'.join(x for x in r[4].splitlines() if '/search?keywords=' not in x)
 ids=[i for i in dec if re.search(r'(?<![A-Z0-9])'+re.escape(i)+r'(?![0-9])',str(r[4]))]
 if ids:r[6]=str(r[6])+'；本轮：'+'、'.join(i+' '+dec[i][0] for i in ids)
D['coverage'][1][0]='沿用199条原记录的机构检索证据；本轮严格重筛不扩展地域，已检索不等于保留或可申请，机构全面覆盖仍未验收。'
all_excluded=D['excluded']+new_excluded
for r in D['archive']:
 ident=r[0]
 if ident in pm or ident=='M125':
  p=pm['M124' if ident=='M125' else ident];r[-4]='剔除' if p['screen_decision']=='剔除' else '待核' if p['screen_decision']=='待核' else '保留';r[-3]=p['status'];r[-2]=None if p['screen_decision']=='剔除' else p['id'];r[-1]=p['screen_reason'] if p['screen_decision']=='剔除' else ''
for a in audits:
 p=pm[a['id']];a['final_sheet']='05剔除记录' if p['screen_decision']=='剔除' else '01申报总览' if p in home else '06历史项目' if p in hist else '08其他资助' if p in other else '07待核项目'
stats={'重筛独立条目':166,'任务证据保留':sum(a['decision']=='保留' for a in audits),'方向/指南待核':sum(a['decision']=='待核' for a in audits),'本轮新增剔除':len(new_excluded),'累计剔除原记录':len(all_excluded),'详情独立条目':len(survivors),'首页当前正式公告':len(home),'历史项目':len(hist),'待核项目':len(pending),'其他资助':len(other),'原记录覆盖':199}
out={**D,'projects':survivors,'all_reviewed':list(pm.values()),'excluded':all_excluded,'logs':logs,'groups':[{'name':'01申报总览','ids':[p['id'] for p in home]},{'name':'06历史项目','ids':[p['id'] for p in hist]},{'name':'07待核项目','ids':[p['id'] for p in pending]},{'name':'08其他资助','ids':[p['id'] for p in other]}],'stats':stats,'current_input':str(ROOT/'全国机器人开放课题_个人申报台账_最终核验版_20261008.xlsx'),'current_input_hash':hashlib.sha256((ROOT/'全国机器人开放课题_个人申报台账_最终核验版_20261008.xlsx').read_bytes()).hexdigest()}
(H/'prepared_strict.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(H/'review_166.json').write_text(json.dumps({'stats':stats,'reviews':audits,'note':'人工逐项判定；关键词仅用于定位原文片段，不决定保留。已取得来源优先复用；明确区分未取得与资料未载明。'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(stats,ensure_ascii=False));print('Homepage IDs:',','.join(p['id'] for p in home));print('Longest surviving clause:',max((len(v),p['id'],i) for p in survivors for i,v in enumerate(p['fields'])))
