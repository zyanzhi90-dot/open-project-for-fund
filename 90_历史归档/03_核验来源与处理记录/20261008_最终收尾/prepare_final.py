import pathlib,json,re,collections,hashlib,ast,copy,datetime
from openpyxl import load_workbook
H=pathlib.Path(__file__).parent;P=H.parent/'20261008_能力筛选核验';ROOT=H.parents[2]
base=ROOT/'全国机器人开放课题_个人申报台账_筛选核验版_20261008.xlsx'
W=load_workbook(base,data_only=False)
raw={s.title:[[c.value.isoformat() if isinstance(c.value,(datetime.datetime,datetime.date)) else c.value for c in row] for row in s] for s in W}
I=json.loads((P/'input.json').read_text(encoding='utf8'));N=I['norm'];OLD=json.loads((P/'prepared.json').read_text(encoding='utf8'));V=json.loads((H/'verified_review.json').read_text(encoding='utf8'))
old={p['id']:p for p in OLD['projects']}; current={r[0]:r for r in raw['02项目完整详情'][6:] if r[0]}
assert len(current)==152 and len(I['rows'])==199
(H/'confirmed_base_snapshot.json').write_text(json.dumps({'source':str(base),'sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'raw':raw},ensure_ascii=False,indent=2),encoding='utf8')
# Reuse the previously read, source-linked clauses. Do not run the old evaluator.
tree=ast.parse((P/'prepare.py').read_text(encoding='utf8'));env={'re':re}
nodes=[x for x in tree.body if isinstance(x,(ast.Assign,ast.FunctionDef)) and ((isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['PAT','LABEL'] for t in x.targets)) or (isinstance(x,ast.FunctionDef) and x.name in ['clean','clauses','extract']))]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'prior_clause_reader','exec'),env)
FIELDS=['qualification','collaboration','funds','period','outputs','ip','materials']
LABELS=['申请资格','合作及访问','经费使用及外拨','研究周期','成果数量及署名','知识产权','材料及提交方式']
IDX=[10,11,12,13,14,32,15]
SOURCES={k:json.loads((H/'sources'/f'{k}.json').read_text(encoding='utf8')) for k in N}
recover=set(V['reviewed_recoveries'])|{'M079','M164','M167','M180','M182','M188','M193','M194'}
out=set(r[0] for r in OLD['excluded'])-recover|{'M038','M175'}
reasons={r[0]:r[3] for r in OLD['excluded']}
objective={
 'M140':'指南任务为凝聚态物理与量子材料研究。', 'M163':'指南任务为深地岩体、地质工程与地下工程。',
 'M141':'指南任务为光电子材料、半导体器件及相关物理机制。', 'M158':'指南限定自然资源时空数据分析和资源治理。',
 'M143':'指南限定土木结构抗灾、防灾减灾。', 'M144':'指南限定结构材料基因设计及材料制备。',
 'M145':'指南限定文化旅游影像、区域文化与文旅应用。', 'M147':'指南限定煤炭转化、煤化工与低碳工艺。',
 'M123':'指南本批任务为COF/锌碘电池材料、电解槽与钙钛矿器件。', 'M151':'指南限定中药质量、药效及作用机制。',
 'M155':'指南限定射频异质异构集成电路及器件。', 'M179':'指南限定生命分析化学及生物分析。',
 'M184':'指南限定风险治理、应急管理与政策研究。', 'M149':'指南限定特种环境复合材料制备及性能。',
 'M150':'现有计划为大健康创新创业、商业与成果转化生态研究。', 'M174':'指南四领域为干细胞材料、类器官创制、类器官功能表征及药物筛选。',
 'M183':'现有研究对象为警犬行为、训练与生物相关技术。', 'M071':'现有公告为油气勘探开发指南建议征集，并非课题资助受理。',
 'M192':'指南限定山地城镇建设及土木结构。', 'M173':'指南限定材料化学反应与材料制备。',
 'M170':'指南限定地球物质循环、成矿及地球化学。', 'M178':'指南限定射频异质集成电路及器件。',
 'M139':'指南限定金属燃料电池、电化学与能源材料。', 'M171':'指南限定生殖医学与子代健康机制。',
 'M128':'指南限定生态经济金融、数字经济管理和金融创新应用；非机器人或工业装备任务。',
 'M110':'指南研究对象为建筑及土木结构性能演化。', 'M172':'指南限定水文气象灾害机理及预警。',
 'M177':'指南限定量子功能材料与量子物理。', 'M136':'本批明确为内蒙古工业大学校内子课题征集。',
 'M138':'本批仅面向清华大学校内教师。',
 'M038':V['explicit_personal_ineligibility']['M038']['reason'],'M175':V['explicit_personal_ineligibility']['M175']['reason']}
assert out==set(objective)
topics={'M079':'地质监测装备、多源协同感知','M164':'微电子人工智能、生物医学电子、物联网电子','M167':'无线网络资源优化、信道建模','M180':'生态纺织','M182':'月球与行星科学','M188':'光电成像与传感','M193':'极限环境光电传感、光子成像','M194':'软物质、固体微结构物理',
 'M152':'结构动力学、模型辨识、自适应控制','M017':'装备测量、加工力测量、精密仪器','M041':'脑启发感知、视觉理解与决策','M066':'混合动态建模、最优控制、反馈镇定','M166':'医学智能、健康工程','M162':'医学人工智能、影像分析','M113':'多模态评估、医学人工智能','M153':'高阶网络、脑功能网络与认知','M077':'具身智能、多模态感知、世界模型','F001':'医疗器械、超声技术','F002':'先进测控、具身智能','F003':'机器人关键技术','F004':'空间智能、世界模型','M029':'智能制造、技能学习、多模态感知','M135':'流体动力装备、控制与优化','M132':'复杂智能体协同、共融机器人控制','M036':'工业混合建模、感知与协同控制'}
topics.update({k:v['topic'] for k,v in V['reviewed_recoveries'].items()})
known_lines={'M006','M049','M056','M064','M069','M074','M166','M180','M182','M187','M188','M194','F003','F004'}
dates={'M003':'2026-10-09','M103':'2026-09-01','M016':'2026-08-31','M036':'2022-12-31','M132':'2025-04-30','M174':'2026-03-31','M124':'2026-05-20','M125':'2026-05-20'}
dates.update({k:v['deadline'][:10] for k,v in V['reviewed_recoveries'].items() if re.match(r'20\d\d-\d\d-\d\d',v.get('deadline',''))})
times={'M003':'18:00','M119':'12:00','M191':'18:00','M100':'17:00'}
years={'M152':'2027','M036':'2023','M132':'2025','M176':'2027','M167':'2027','M165':'2026—2027'}
def tidy(v):
 if not v:return ''
 t=str(v).replace('\\n','\n');t=re.sub(r'L\d+:\s*','',t);t=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',t)
 t=re.split(r'上一篇|下一篇|版权所有|Copyright|友情链接|免责声明',t,flags=re.I)[0]
 segments=re.split(r'(?<=[。；])|\n',t); kept=[]
 for s in segments:
  s=s.strip()
  if not s or re.search('旧表|旧记录|已修正|误填|替换|改为|更正|原记录|本轮|适合承担|可承担|最匹配|高度匹配|优先选|本人首选|申请书未|并非超声|无需重复|定向检索完成',s):continue
  if re.search('网站首页|导航|信息公开|网站管理|扫一扫|浏览次数|Crawled:|Published:|wordlim|您所在的位置',s):continue
  if s not in kept:kept.append(s)
 return '\n'.join(kept).strip()
def usable(ident):
 seq=[];seen=set()
 for s in SOURCES[ident]['sources']:
  if s['url'] in seen:continue
  if re.search('投稿指南|工作指南|签证|信息公开|上一篇|下一篇',s['kind']):continue
  if re.search('申请书|申请表|申报表|摘要|信息表',s['kind']) and not re.search('指南|管理|通知',s['kind']):continue
  if ident=='M194' and '2025' in s['kind']:continue
  if s.get('text'):seen.add(s['url']);seq.append(s)
 return seq
def fieldvalue(ident,key,index):
 if ident in current:v=tidy(current[ident][index])
 else:v=tidy(N[ident].get(key,''))
 if ident in recover:
  hits,_=env['extract'](usable(ident),key)
  if hits:v=tidy('\n'.join(hits))
 if re.search('未在|未明确|尚未明确|待.*确认|需.*核实',v) and not re.search('博士|中级|副高|至少|不得|必须|须|不外拨|共有|共享|归|[0-9].{0,4}(?:年|月|篇)|报销|电子|提交',v):v=''
 return v
# Concise, reviewed final clauses overwrite contaminated snippets directly.
manual={
 'M095':{'qualification':'海内外博士或副高以上学者；单位审查、推荐并盖章；鼓励临床医学学者。','materials':'2026-08-14 18:00截止；签字盖章纸质3份及电子文档；提交资格证明、相关伦理/科技安全批准或备案、知识产权声明和科研诚信承诺。李老师13510019066，ke.li@nmed.org.cn。'},
 'M003':{'qualification':'固定工作单位；申请内容有前期工作基础。','collaboration':'须与本实验室固定成员合作申请；临床验证资源按所选方向落实。DR方向须不少于15家临床分中心。','period':'不超过3年。','materials':'2026-10-09 18:00前，所在单位同意签字盖章的PDF发research.bme@shanghaitech.edu.cn；主题：开放课题申请方向名称-姓名-单位。张老师zhangjf4@shanghaitech.edu.cn，021-20680814。'},
 'M119':{'qualification':'国内高校、研究院所等副高或博士在职人员；实际负责人；只能申请1项。','collaboration':'鼓励多个团队联合申请；客座研究期间至少作1次报告。未规定须联合固定成员申报。','funds':'设备费、业务费、劳务费；劳务费不超过总经费50%；依托单位为经费管理责任主体；结余留归依托单位；拨款流程及批次未在已取得办法明确。','period':'重点3年；面上2年。','outputs':'面上至少1篇、重点至少2篇指定或同档次期刊/会议论文（含已录用）；第一或通讯作者为课题组成员，实验室第一或第二署名单位并致谢；按任务书验收。','ip':'实验室与依托单位共享，方式按任务书约定；资产由依托单位依法管理。','materials':'2026-10-30北京时间12:00前申请书发hlwgzbgs@mailoa.tsinghua.edu.cn，邮件注明重点方向；批准后另交盖章纸质材料；010-62795462。'},
 'M191':{'qualification':'境内独立法人高校、医疗机构或科研院所；负责人博士或副高，从事相关临床及科研工作，拥有主持同类项目经验。','collaboration':'可与境内相关单位联合申报；未规定必须联合本室固定成员；须具备所选任务临床数据和伦理条件。','funds':'签署任务书后按获批金额划拨资助经费；预算模板含材料、业务、设备、协作、人员、管理等科目；拨款账户、外拨流程需取得管理办法/任务书。','outputs':'方向2：研究报告、预测模型；重点项目另有论文要求；未统一规定论文篇数。','materials':'2026-10-16 18:00前签字盖章扫描件发stilab@stilab.ac.cn；主题2026第2批—单位—负责人。杨/梁老师010-63082702/2703。'},
 'M164':{'qualification':'博士或助理教授及以上；单位盖章同意。','collaboration':'至少1名实验室全职教师作为合作者。','period':'24个月，2026-08-01开始。','ip':'已有知识产权仍归原权利人；共同完成的成果由完成各方共有；商业使用须先取得各方书面确认并另签许可协议。'},
 'M193':{'qualification':'相关学科博士或副高及以上；非依托单位人员；年龄45岁及以下；单位同意。','collaboration':'须与实验室固定人员联合申报。','period':'2年。','outputs':'至少2篇SCI论文，实验室第一完成单位；标注基金及编号。','ip':'实验室与负责人所在单位共有。','materials':'2026-10-16截止；纸质3份签字盖章；Word和盖章PDF发skl-dmt@nuc.edu.cn。张老师13834680208，凡老师13700546579。'},
 'M103':{'qualification':'工程中心合作单位人员及中心相关人员；博士可申报重点；每人主持1项、参与不超过2项。','period':'一般1年；重点2年。','ip':'共同成果知识产权共有，转让须双方同意。'},
 'M036':{'qualification':'非本室高校、科研机构研究人员；高级、在站博士后或控制优化领域研究人员可申报；中级人员需1名高级同行推荐。','funds':'每项2—4万元，按年度拨款、单独核算；仅文献、材料、测试、差旅、版面等，不得提取劳务酬金；外拨对象未载明。','period':'一般2年。','outputs':'实验室第一或第二完成单位，标注资助。','materials':'2023年度申报2022-11-01至2022-12-31；纸质3份并发acocp-lab@ecust.edu.cn。'},
 'M132':{'qualification':'正在主持一、二、三类纵向项目2项及以上者不得申报；同一内容不得重复申报纵向项目。','period':'重点2—3年；一般2年。','outputs':'重点至少2篇、一般至少1篇二类以上期刊论文；实验室署名并标基金。全额资助项目实验室第一单位。','funds':'按安徽工业大学财务审批报销，开票安徽工业大学；具体外拨未规定。','ip':'实验室全额资助成果归实验室；自带经费合作成果共有。','materials':'2025-04-30截止；纸质3份，电子发chenbinahut@163.com；陈老师0555-2315107。'},
 'M185':{'qualification':'中国国籍；博士或副高；40岁以下优先；限1家单位，不支持联合申报。','collaboration':'不支持联合申报；未明确必须联合本室固定人员。'},
 'M175':{'qualification':'本批仅面向常州大学机械学院及大数据学院。'}
}
extras={'M079':('一般0.6万元；重点1.2万元','不超过1年。'),'M164':('不超过10万澳门元','24个月。'),'M167':('A类5—7万元；B类8—10万元','2年。'),'M193':('10万元','2年。')}
specific_personal={'M003':'须确认固定人员合作者、所选方向临床研究协作及数据资源。','M119':'须确认本人是否已有本室申请/在研项、依托单位认定及客座安排。','M191':'须确认主持同类项目经历，及所选方向的临床数据与伦理安排。','M193':'须确认年龄不超过45岁、相关学科资格及固定人员合作者。','M103':'須向中心确认南信大/本人是否在合作单位或相关人员范围。','M106':'博士学位已知；中级及以上职称或两名高级专家推荐情况待确认。','M043':'须确认中级及以上职称；访问安排及成果合作。','M068':'博士学位满足学历分支；须确认成果合作作者和限项。','M185':'博士学位满足学历分支；中国国籍待本人确认。','M077':'须确认中级/副高职称及相应专家推荐。','M190':'须确认副高及以上职称与固定成员合作者。','M008':'须按所选专向与联系人确认任务指标及协作。','M164':'博士学位满足学历分支；须确认本室全职教师合作者。','M152':'博士学位满足学历分支；固定人员合作者及本人在研/重复资助情况待确认；青年类别另需确认年龄≤35岁。','M175':'本人为南信大现职，不属于本批校内限定范围。','M038':'本人为南信大现职，不属于本校在职教师范围。'}
def personal(k,vals):
 if k in specific_personal:return specific_personal[k]
 q,c=vals[0],vals[1]; seq=[]
 if re.search('博士(?:学位|学历)?或|博士.*(?:或|及以上)|或.*博士',q):seq.append('博士学位已知，满足学历分支')
 if re.search(r'(?:年龄|周岁|岁以下|不超过.{0,3}岁|≤\d\d|未满\d\d)',q) and not re.search(r'(?:\d\d岁以下|年龄).*优先|鼓励.*\d\d',q):seq.append('年龄限制待本人确认')
 if re.search('副高|中级|高级职称',q) and not re.search('博士.*或|或.*博士|博士学位.*申请|博士学历',q):seq.append('职称分支及推荐要求待本人确认')
 if re.search('不得.{0,25}申报|在研|未结题|限.{0,3}项|已获|再次资助|每年.{0,10}申请',q):seq.append('本室在研/既往资助及适用限项待本人确认')
 if re.search('须|必须|至少|应.*合作|需',c) and re.search('固定|本室|联合|合作者|团队成员',c):seq.append('固定人员合作者/强制合作尚未确认')
 return '；'.join(seq) if seq else '未发现须核实的年龄/职称硬门槛；所选任务条件由本人核对。'
def evidence(k,key,val):
 if (k=='M193' and key=='funds') or (k=='M191' and key in ['period','ip']):return '资料未取得｜当期管理办法/任务书未取得，须向公告联系人索取'+LABELS[FIELDS.index(key)]+'条款。'
 if k=='M194':return '资料未取得｜2026年度公告及指南主体为图片，尚未取得完整可读条款；不得沿用2025年条款。'
 if k in ['M006','M049','M064','M069','M074','M166','M180','M182','M187','M188'] and not val:return '资料未取得｜尚无当期正式受理指南，未取得'+LABELS[FIELDS.index(key)]+'。'
 if val and not re.search('未在|未取得|尚无|未公开|待核实|需确认',val):return '官方明确｜'+val
 docs=usable(k);fail=[x for x in SOURCES[k].get('attempts',[]) if re.search('管理|指南|附件',x.get('name','')) and not re.search('全文|网页正文',x.get('status',''))]
 if not docs or (fail and not val):return '资料未取得｜'+(val or LABELS[FIELDS.index(key)]+'；相关指南/管理资料访问受限或未取得。')
 return ('官方明确｜'+val+'\n' if val else '')+'官方未公开｜已取得公开资料未载明'+LABELS[FIELDS.index(key)]+'的完整条款。'
projects=[];excluded=[];logs=[];home_map=[]
for k,n in N.items():
 if k in out:
  status='资格不符' if k in ['M038','M175','M136','M138'] else ('已截止' if n.get('date') and n['date']<'2026-10-08' else '线索待核')
  excluded.append([k,n['org'],n['lab'],status,objective[k],n['url'],'2026-10-08'])
  logs.append([k,'筛选与资格',objective[k],n['url'],'2026-10-08','官方明确','剔除',status]);continue
 r=current.get(k);prev=old.get(k,{})
 date=dates.get(k,prev.get('date',n.get('date')))
 if k in ['M194','M180','M182','M188']:date=None
 date=date[:10] if isinstance(date,str) and re.match(r'^20\d\d-\d\d-\d\d',date) else None
 status='线索待核' if k in known_lines else ('已截止' if date and date<'2026-10-08' else '截止待确认' if date=='2026-10-08' else '受理中·条件待核' if date and date>'2026-10-08' else '线索待核')
 topic=topics.get(k,prev.get('topic',n.get('directions','研究任务未取得')))
 topic=re.sub(r'与申请书的匹配方向：|较可迁移：|可以直接申报|高度方法匹配|不直接支持[^，；]*|与机器人控制弱相关|偏大模型研究|需[^，；]*|官网有专门研究团队|[，、]?(?:部分科学技术交集|直接关联[^，；]*|必须[^，；]*|[^，；、]{0,8}场景限定|[^，；、]{0,8}应用限定|[^，；、]{0,8}领域限定)','',topic)
 topic=re.split('；|。',topic)[0].strip('，、 ')
 vals=[fieldvalue(k,key,idx) for key,idx in zip(FIELDS,IDX)]
 for j,key in enumerate(FIELDS):
  if k in manual and key in manual[k]:vals[j]=manual[k][key]
 amount=prev.get('amount',tidy(n.get('amount','')) or '未公布')
 if k in V['reviewed_recoveries'] and V['reviewed_recoveries'][k].get('amount'):amount=V['reviewed_recoveries'][k]['amount']
 if k in extras:amount=extras[k][0];vals[3]=extras[k][1]
 if k in ['M188','M180','M182','M194']:amount='未取得当期资助标准'
 if k=='M036':amount='2—4万元'
 if k=='M058':amount='一般≥2万元；重点≥3万元'
 if k=='M132':amount='评审确定'
 if k=='F001':amount='总支持≥10万元；现金≥总支持50%'
 if k=='F002':amount='科研经费5—25/25—100万元（一般/重点）；另有软硬件支持'
 year=years.get(k,prev.get('details',[None]*36)[35] if prev else n.get('year',''))
 if not year or '待核' in str(year):year= '2026' if date and date.startswith('2026') else date[:4] if date else '资料未取得'
 if k=='M073':region='P0 南京及周边'
 else:region=prev.get('region',n.get('region','P2 其他地区'))
 sourcekind='其他资助' if k.startswith('F') else '线索' if k in known_lines else '正式开放课题公告'
 if k in ['M194']:sourcekind='线索'
 if k in ['M036','M132']:sourcekind='历史正式开放课题公告'
 docs=usable(k);refs=list(dict.fromkeys(s['url'] for s in docs));url=n['url']
 pf=personal(k,vals);gaps=[]
 ev=[evidence(k,key,val) for key,val in zip(FIELDS,vals)]
 for lab,s in zip(LABELS,ev):
  if '官方未公开' in s:gaps.append('官方未公开：'+lab)
  if '资料未取得' in s:gaps.append('资料未取得：'+lab)
 if status=='截止待确认':gaps.insert(0,'官方未公开：截止当天具体受理时点；须向公告联系人确认当前是否仍接收。')
 if status=='线索待核':gaps.insert(0,'资料未取得：当期正式受理公告/完整指南或受理窗口。')
 if k in V['other_verified_corrections']:gaps.append(V['other_verified_corrections'][k].get('missing',V['other_verified_corrections'][k].get('reason','')))
 if k in V['reviewed_recoveries'] and V['reviewed_recoveries'][k].get('public_gaps'):gaps.append(V['reviewed_recoveries'][k]['public_gaps'])
 relation='南信大现职' if '南京信息工程大学' in n['org'] else '澳门大学博士；陈俊龙合作圈' if n['org']=='澳门大学' else '华南理工硕士' if '华南理工大学' in n['org'] else '杨晨光合作圈' if '香港理工大学' in n['org'] else '有熟人' if any(x in n['org'] for x in ['自动化研究所','西北工业大学','重庆大学']) else ''
 contact=V['other_verified_corrections'].get(k,{}).get('contact','') or V['reviewed_recoveries'].get(k,{}).get('contact','')
 if not contact:
  em=list(dict.fromkeys(re.findall(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',vals[6])))
  contact='；'.join(em) or '公告联系入口'
 amountlong=tidy(r[9] if r else n.get('amount',''))
 if not amountlong:amountlong=amount
 if k in recover or k in ['F001','F002','M036','M132']:amountlong=amount
 value='；'.join(x for x in [amount, '明确外拨至承担单位' if re.search('外拨.*单位|划拨.*所在单位|拨至.*单位|一次性外拨',vals[2]) else '经费不外拨' if '不外拨' in vals[2] else '',re.sub(r'\n','；',vals[4])[:180]] if x)
 p={'id':k,'aliases':[],'org':n['org'],'lab':n['lab'],'region':region,'year':year,'date':date,'time':times.get(k,''),'status':status,'topic':topic or '研究任务未取得','amount':amount,'url':url,'kind':sourcekind,'fields':ev,'personal':pf,'gaps':'\n'.join(dict.fromkeys(x for x in gaps if x)),'contact':contact,'relation':relation,'sources':refs,'value':value,'amountlong':amountlong}
 projects.append(p)
 for key,lab,val,s in zip(FIELDS,LABELS,vals,ev):logs.append([k,lab,s,'\n'.join(refs) or n['url'],'2026-10-08','官方明确' if s.startswith('官方明确') else '资料未取得' if '资料未取得' in s else '官方未公开','保留',status])
 logs.append([k,'本人条件',pf,n['url'],'2026-10-08','本人情况待确认','保留',status])
 logs.append([k,'受理与截止',f'年度{year}；截止{date or "未取得"} {times.get(k,"")}；{sourcekind}',n['url'],'2026-10-08','官方明确' if date and k not in known_lines else '资料未取得','保留',status])
 if k in recover:logs.append([k,'筛选复核',V['reviewed_recoveries'].get(k,{}).get('reason','保留公开列明研究任务或未取得完整任务的线索，供本人选择。'),n['url'],'2026-10-08','官方明确' if docs else '资料未取得','保留',status])
# One shared annual guide is one funding call; keep both stable original numbers.
mp={p['id']:p for p in projects};mp['M124']['aliases']=['M125'];mp['M124']['lab']+=' / '+mp['M125']['lab'];mp['M124']['topic']='汽车测控、安全控制、仿真测试';projects.remove(mp['M125'])
logs.append(['M125','共享公告去重','与M124共享2026年度联合申报公告；编号M125保留并映射到M124详情。',N['M125']['url'],'2026-10-08','官方明确','保留（并入M124）',mp['M124']['status']])
srank={'可申请':0,'受理中·条件待核':1,'截止待确认':2,'线索待核':3,'已截止':4,'资格不符':5}
regions=['P0 南京及周边','P0 澳门','P0 香港','P0 广州及周边','P1 北京及周边','P1 西安及周边','P1 重庆']
familiar=['南京信息工程大学','澳门大学','香港理工大学','华南理工大学','中国科学院自动化研究所','西北工业大学','重庆大学']
def orgkey(p):return re.sub(r'^.*?·','',p['org'])
def reg(p):
 t=p['region'];return next((i for i,x in enumerate(regions) if x in t),7)
def fk(p):return next((i for i,x in enumerate(familiar) if x in p['org']),20)
def valuerank(p):return 0 if '明确外拨' in p['value'] else 2 if '经费不外拨' in p['value'] else 1
groupsort={}
for p in projects:
 key=(p['status'],orgkey(p));v=(reg(p),fk(p),valuerank(p),p['region'],p['date'] or '9999-12-31',orgkey(p))
 groupsort[key]=min(groupsort.get(key,v),v)
def sk(p):return (srank[p['status']],*groupsort[(p['status'],orgkey(p))],p['date'] or '9999-12-31',p['id'])
projects.sort(key=sk)
active=[p for p in projects if not p['id'].startswith('F') and p['status'] in ['可申请','受理中·条件待核','截止待确认']]
lines=[p for p in projects if not p['id'].startswith('F') and p['status']=='线索待核']
closed=[p for p in projects if not p['id'].startswith('F') and p['status']=='已截止']
other=[p for p in projects if p['id'].startswith('F')]
projects=active+lines+closed+other
dh=['项目编号','项目类别/证据性质','依托单位','实验室/项目','申报状态','项目年度','截止日期','北京时间截止时点','研究主题','资助金额及类别','申请资格','合作及访问','经费使用及外拨','研究周期','成果数量及署名','知识产权','材料及提交方式','本人条件确认','缺失条款及联系事项','公告/线索来源URL','官方指南/办法/附件URL','核查基准（北京时间）','合作关系线索','经费与成果条款摘要','地域排序组','联系入口','其他原编号']
for p in projects:p['details']=[p['id'],p['kind'],p['org'],p['lab'],p['status'],p['year'],p['date'],p['time'],p['topic'],p['amountlong'],*p['fields'],p['personal'],p['gaps'],p['url'],'\n'.join(p['sources']),'2026-10-08 17:57',p['relation'],p['value'],p['region'],p['contact'],'、'.join(p['aliases'])]
allmap={p['id']:p for p in projects}
for p in projects:
 for a in p['aliases']:allmap[a]=p
assert set(allmap)|out==set(N) and not set(allmap)&out and len(allmap)+len(out)==199
# Preserve the institution mother table, replace its fabricated completion statements.
cov=copy.deepcopy(raw['03机构检索覆盖']);cov[0][0]='机构检索进度';cov[1][0]='仅列现有199条记录覆盖范围；本轮未扩展地域。平台全面覆盖未验收。';cov[2]=[None]*9
cov[5]=['覆盖层次','单位/平台','地域优先组','合作关系/地区','已查实验室及年度','未查平台/后续事项','检索进度','已查官方证据','下一轮补查范围']
for row in cov[6:]:
 org=str(row[1] or '');ids=[k for k,n in N.items() if org==n['org'] or (len(org)>4 and org in n['org'])]
 if ids:
  row[4]='\n'.join(dict.fromkeys(N[k]['lab']+'｜'+str(allmap[k]['year'] if k in allmap else N[k].get('year') or '年度未取得')+'｜'+k for k in ids))
  pending=[k for k in ids if k in allmap and allmap[k]['status']=='线索待核']
  row[5]=('继续取得正式指南：'+','.join(pending)+'；' if pending else '')+'该机构其他相关平台未逐一检索，范围尚未列全；下轮先核官网科研平台目录。'
  row[6]='部分已查（范围见本行）';row[7]='\n'.join(dict.fromkeys(N[k]['url'] for k in ids));row[8]='核所列平台下一年度公告；补查该校机器人、智能装备、控制、医工相关未覆盖平台。'
 else:
  text=str(row[4] or '')+' '+str(row[7] or '')
  row[6]='部分已查（历史线索）' if 'http' in text else '未查（无可追溯检索证据）'
  row[5]='尚无实验室及公告年度逐项证据，需核官网平台目录后列明。';row[8]='按地域顺序补查机器人、智能装备、控制及医工平台；不视为本轮完成。'
cov[6:]=sorted(cov[6:],key=lambda r:(str(r[2] or 'P2'), next((i for i,x in enumerate(familiar) if x in str(r[1])),20),str(r[1])))
archive=[];exmap={r[0]:r for r in excluded}
for r in I['rows']:
 k=r[0];p=allmap.get(k);state=p['status'] if p else exmap[k][3]
 archive.append(r+['保留（并入M124）' if k=='M125' else '保留' if p else '剔除',state,p['id'] if p else '',exmap[k][4] if not p else ''])
stats={'原记录':199,'保留原记录':len(allmap),'有效独立条目':len(projects),'剔除':len(out),'状态':dict(collections.Counter(p['status'] for p in projects)),'剔除资格不符':sum(r[3]=='资格不符' for r in excluded),'正式开放课题公告':sum('正式开放' in p['kind'] for p in projects),'线索记录':sum(p['kind']=='线索' for p in projects),'其他资助':len(other)}
d={'source':str(base),'source_hash':hashlib.sha256(base.read_bytes()).hexdigest(),'projects':projects,'detail_header':dh,'coverage':cov,'log_header':['项目编号','核验字段','最终条款/缺失信息','证据URL','核查日期','证据分类','保留/剔除','最终状态'],'logs':logs,'excluded':excluded,'archive_header':I['raw']['02项目完整详情'][5]+['本轮清单结论','最终状态','详情主编号','剔除理由'],'archive':archive,'base_raw':raw,'groups':[{'name':'当前公告','ids':[p['id'] for p in active]},{'name':'线索与受理窗口待核','ids':[p['id'] for p in lines]},{'name':'已截止（历史参考）','ids':[p['id'] for p in closed]},{'name':'其他资助（独立区域）','ids':[p['id'] for p in other]}],'stats':stats}
(H/'prepared_final.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(stats,ensure_ascii=False))
