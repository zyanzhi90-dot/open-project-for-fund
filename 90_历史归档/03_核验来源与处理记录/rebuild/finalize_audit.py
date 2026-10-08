import json,pathlib,re,collections,copy,datetime,ast
R=pathlib.Path(__file__).parent;A=R/'audit_all'
raw=json.load(open(R/'original.json',encoding='utf8'));norm=json.load(open(R/'normalized.json',encoding='utf8'));ps={p['id']:p for p in norm['projects']}
attachments=json.load(open(A/'attachment_index.json',encoding='utf8'))
patterns={
 'amount':r'资助(?:额度|金额|强度|经费)|每(?:项|个).{0,40}(?:万元|万港元|澳門幣)|[0-9].{0,12}万(?:元|港元)|funding.{0,35}(?:HKD|MOP|RMB)|maximum.{0,45}grant',
 'qualification':r'申请(?:人|者|条件|对象|资格)|申报(?:人|资格|条件)|博士.{0,25}职称|年龄.{0,20}岁|不得.{0,20}(?:申请|申报)|限项|eligibility|applicant.{0,100}(?:doctorate|degree|professor)',
 'collaboration':r'(?:固定|本实验室).{0,35}(?:合作|联合|联系|协同)|(?:联合|合作|共同).{0,25}(?:固定|本实验室|研究人员)|每年.{0,25}(?:来室|访问|到访|客座)|共同负责人|full.time.{0,30}(?:collaborator|faculty)|at least one.{0,50}collaborator',
 'funds':r'外拨|拨付|报销|结算|经费(?:使用|管理|用于|不|应|需|只能|主要)|经费用于|专款专用|设备费|业务费|劳务费',
 'period':r'(?:研究|执行|资助|课题|项目).{0,12}(?:期限|周期|年限|起止)|起始(?:日期|时间)|完成(?:期限|时限)|资助期.{0,12}年|duration|commence',
 'outputs':r'(?:论文|成果|专利|软件著作权|验收|结题|署名|标注).{0,90}(?:篇|SCI|EI|CCF|要求|须|应|报告|实验室|不少于|至少|第一|第二|单位)|第一完成单位|第一署名单位|acknowledg',
 'ip':r'(?:知识产权|知識產權).{0,60}(?:归|共同|共有|共享|所有|权属|拥有|约定|协议|比例)|专利权人|产权归属|成果.{0,35}(?:归属|共有|共享|共同所有|归.{0,10}所有)|intellectual property.{0,80}(?:own|vest|develop)|co.owned',
 'materials':r'申请书.{0,100}(?:发送|提交|签|盖章|邮寄|纸质|份)|(?:签字|盖章|电子版|纸质|扫描件|Word|PDF).{0,90}(?:申请|寄|报送|提交|发送|份|邮箱)|(?:电子信箱|联系邮箱|电子邮箱|邮箱|联系人|邮件主题|通讯地址|邮寄地址|通信地址)|[a-z0-9._+-]+@[a-z0-9.-]+\.[a-z]{2,}',
}
labels={'amount':'资助金额','qualification':'申请资格','collaboration':'固定人员/合作要求','funds':'经费使用','period':'周期','outputs':'成果/署名','ip':'知识产权','materials':'材料与提交'}
def clean(t):
 t=re.split(r'上一篇|下一篇|上一条|下一条|最新动态',t)[0]
 t=re.sub(r'(?<=[\u3400-\u9fff0-9])\s*\n\s*(?=[\u3400-\u9fff0-9，。、；：）])','',t)
 t=re.sub(r'(?<=[0-9])\s+(?=[0-9])','',t)
 return t
def sentences(t):
 # Retain the immediately following enumerated clauses; they often contain the actual limits.
 s=[x.strip() for x in re.split(r'(?<=[。；])|\n',clean(t)) if len(x.strip())>4]
 return [x for x in s if not re.search(r'^上一篇|^下一篇|版权所有|^Copyright|^\[wordlim|Crawled:|Published:',x)]
def evidence(t,pat):
 s=sentences(t);out=[]
 for i,x in enumerate(s):
  if re.search(pat,x,re.I):
   a=x
   if re.search(r'如下|以下|：$|包括|要求',x) and len(x)<200:
    for y in s[i+1:i+5]:
     if re.match(r'^[（(]?[一二三四五六七八九十0-9]+[、.．)）]|^[-•]',y):a+=' '+y
     else:break
   if a not in out:out.append(a)
 return out
date_overrides={
 'M001':'2025-11-14','M002':'2026-08-21','M003':'2026-10-09','M004':'2026-04-10','M005':'2026-05-06','M009':'2026-05-29','M010':'2026-06-14','M011':'2026-09-30','M012':'2026-07-28','M013':'2025-10-15','M014':'2026-08-28','M015':'2026-10-20','M018':'2026-10-05','M020':'2026-03-15','M021':'2026-04-30','M022':'2025-11-07','M023':'2026-05-22','M024':'2026-03-20','M025':'2026-04-20','M027':'2026-09-30','M028':'2025-12-20','M030':'2025-11-15','M031':'2025-08-10','M033':'2025-09-03','M034':'2025-10-31','M037':'2026-04-10','M038':'2026-06-12','M040':'2026-04-30','M042':'2025-09-03','M043':'2026-10-08','M044':'2026-10-10','M045':'2025-04-25','M046':'2024-11-30','M048':'2025-12-31','M050':'2026-09-21','M051':'2026-04-15','M052':'2025-11-21','M057':'2026-09-27','M058':'2026-07-10','M059':'2026-04-30','M060':'2026-04-30','M061':'2025-11-30','M063':'2026-08-14','M065':'2026-05-31','M067':'2026-04-22','M070':'2026-07-25','M072':'2026-04-10','M075':'2026-02-10','M076':'2026-07-31','M079':'2026-07-24','M080':'2026-05-14','M081':'2026-04-20','M082':'2026-02-28','M083':'2026-06-15','M084':'2025-11-03','M085':'2026-10-31','M086':'2026-08-15','M089':'2025-12-20','M090':'2026-04-20','M091':'2026-06-30','M092':'2025-05-31','M093':'2026-06-30','M094':'2025-10-30','M095':'2026-08-14','M096':'2026-05-17','M098':'2026-08-15','M099':'2026-06-30','M100':'2026-10-30','M101':'2026-08-20','M102':'2026-03-10','M104':'2026-05-31','M105':'2026-10-26','M106':'2026-10-08','M107':'2026-10-12','M108':'2026-01-05','M109':'2026-06-15','M110':'2026-08-31','M111':'2026-09-20','M112':'2024-09-30','M114':'2026-10-08','M115':'2025-09-20','M116':'2025-04-25','M117':'2025-03-31','M118':'2025-11-07','M119':'2026-10-30','M120':'2025-02-28','M121':'2026-01-20','M122':'2026-01-19','M123':'2026-02-28','M124':'2026-05-20','M125':'2026-05-20','M126':'2026-05-15','M128':'2026-08-20','M129':'2026-09-25','M130':'2026-06-25','M131':'2026-09-30','M133':'2026-08-15','M134':'2026-05-20','M136':'2026-06-10','M137':'2026-07-26','M138':'2026-10-18','M139':'2026-05-20','M140':'2026-10-09','M141':'2026-10-12','M142':'2026-10-15','M143':'2026-10-25','M144':'2026-10-25','M145':'2026-10-30','M146':'2026-11-10','M147':'2026-11-10','M148':'2026-09-24','M149':'2026-09-26','M150':'2026-03-26','M151':'2026-04-20','M152':'2026-10-10','M154':'2026-08-31','M155':'2026-05-17','M157':'2026-09-07','M158':'2026-10-20','M160':'2026-10-27','M161':'2026-11-15','M162':'2026-11-15','M164':'2026-02-28','M165':'2025-08-15','M167':'2026-09-25','M168':'2026-05-15','M169':'2026-06-30','M170':'2026-04-15','M171':'2026-08-14','M172':'2026-08-31','M173':'2025-11-10','M175':'2026-05-27','M177':'2026-09-30','M178':'2026-05-17','M183':'2026-04-30','M184':'2026-09-18','M185':'2026-08-17','M186':'2023-10-15','M189':'2026-06-25','M190':'2026-09-20','M191':'2026-10-16','M192':'2025-10-31','M193':'2026-10-16','M194':'2026-05-06'}
# Overrides below are concise readings of the full notices and rules, not inherited legacy values.
manual={
 'M020':{'amount':'一般课题10万元/项，拟10项；企业课题不超过100万元/项，拟1项（限儿童脑高分辨率MRI微血管成像专题）','qualification':'2026指南：实验室外博士或副高级及以上；本实验室人员不申请；同一申请人只能承担1项；既往未按期结题者不受理。通用办法另写副高以下须2名高级职称专家推荐，应与实验室确认博士但无副高者是否需推荐。','collaboration':'必须与实验室固定成员合作；未填写合作者由实验室指定。','period':'一般、企业课题均2年。','funds':'通用办法：第一年拨付50%，中期通过再拨50%；当年须完成支出额度，结余没收。允许仪器使用、材料加工、差旅住宿、发表及学术活动费用；未明确是否外拨，须确认。','outputs':'年度进展、结题报告及成果文件；考核指标以任务书为准，指南未公布统一论文数量。论文须署名医学成像科学与技术系统全国重点实验室。','ip':'基金成果由实验室与申请人原单位共同所有。','materials':'2026-03-15前，将单位盖章申请材料电子版发送guozhong_lab@siat.ac.cn。'},
 'M025':{'amount':'单项原则上不超过10万元；100万元是本批次总额，不是单项额度。','qualification':'湖州市本地高校、企业与工控全重团队合作；本年度指南未规定统一学历/职称门槛。','funds':'资金由工控全重统筹；专用设备、业务、劳务等由校内合作人员办理报销，不能据此写可外拨。','period':'一般1年；拟2026年11月中期验收、2027年4月底结题评估。','materials':'2026-04-20前在线提交https://jinshuju.com/f/o008NA；赵泽斌13216521390/zhaozebin@hiict.org.cn；吴朦晨0571-87953813/sklict@zju.edu.cn。'},
 'M047':{'org':'哈尔滨理工大学','amount':'已核官方2022历史公告：5万元/项；未取得2026正式指南，不将历史额度视为当期额度。','qualification':'2022历史公告：副高及以上，或中级且有博士学位；2026条件未核。','period':'2022历史公告称2年，起止2022-12-01至2024-11-31（原公告日期有误，11月不存在31日）；当期未核。','outputs':'历史公告：论文/专利实验室为作者第一单位；奖项、转让须列实验室主要完成单位。','materials':'历史公告：签字盖章纸质原件2份+电子版yuecaixu@hrbust.edu.cn；2026提交要求未核。'},
 'M095':{'amount':'具体课题指南单项上限分别为10、15、20、30或50万元，部分额度仅牵头单位；不是所有项目均50万元。须按所选课题核金额。'},
 'M096':{'amount':'14个具体课题的单项上限为5、10或20万元；通用申报指南100万元上限不能作为所选超声课题实际额度。'},
 'M098':{'amount':'原则10万元/项，不超过5项，实际按研究内容与评审意见；不限制各方向项目数量。','qualification':'国内高校、科研院所、医疗机构、企业等相关人员；一般博士或副高，突出工程/临床/转化能力可放宽；同一人同年度1项；既往未完成阶段任务或结题原则不重复资助。','collaboration':'鼓励与AIRS团队实质合作及医工联合申报，正文未规定必须联合固定人员。','funds':'前资助，立项后一次性拨付；允许材料、测试加工、差旅、会议、出版知识产权、咨询、劳务等，按承担单位及AIRS规定执行。','period':'原则1年。','outputs':'须交中期报告、结题总结、成果清单、经费说明和证明；成果可以论文、算法模型、样机、临床研究/伦理/数据等，不公布统一论文数；发表和宣传按协议标注AIRS。','ip':'通常不得将开放课题成果用于申请专利；确需申请，专利权人须为研究院；转化收益另约，其他成果按AIRS与承担单位协议。','materials':'单位审核盖章PDF；申请书、诚信伦理承诺、人员简历、近5年成果；涉人体/动物/临床影像等补伦理、合规或安全材料。2026-08-15截止；jiangxiaolei@cuhk.edu.cn，姜晓磊13810411418。'},
 'M107':{'amount':'每项不超过10万元。','qualification':'国内博士或高级职称教师，既往获得本室资助者不再申请。','period':'2年，2026年10月至2028年10月。','outputs':'至少2篇学术论文，其中至少1篇SCI/EI；依托单位中北大学申请者另须至少1篇以实验室为唯一单位、固定人员为通讯作者。','materials':'2026-10-12前提交电子申请材料至zhangle@nuc.edu.cn。'},
 'M122':{'amount':'每项6—8万港元（不能写人民币）。','period':'2026-04-01至2027-12-31。'},
 'M123':{'amount':'最多20万澳门元/项。','qualification':'博士或助理教授及以上；申请须所在单位同意、资料齐全；须披露利益冲突。','collaboration':'研究须与本中心科研人员合作共同完成。','period':'2026-05-01起，最多15个月。','outputs':'中期及结题报告；鼓励高质量SCI及奖项，未规定统一论文数。成果须按指南标注FDCT 0002/2024/TFP和CAM-IAPME(UM)/ORP/2026/00X资助；无标注、编号错误或开始前发表均不计。','ip':'研究记录、资料、数据集、软件、测试报告及形成知识产权由申请人单位和澳门大学共有，细节另签书面协议。','materials':'单位盖章电子申请材料2026-02-28前发iapme.orp@um.edu.mo；邮件CAM-IAPME 2026开放基金+姓名+学校；+853 8822 9928。'},
 'M164':{'amount':'不超过10万澳门元/项。','qualification':'博士或助理教授及以上，申请所在单位盖章同意。','collaboration':'每项至少1名实验室全职教师作合作者。','period':'通常24个月，2026-08-01起。'},
 'M165':{'amount':'不超过8万澳门元/项。','qualification':'国内外高校、学术机构、企业等研究人员；博士或助理教授及以上。','collaboration':'每项必须至少1名实验室全职教师作合作者。','period':'通常24个月，2026-01-01起。','funds':'按澳门大学财务规定及开放课题办法，专款专用；PI及接收机构承担财务行政责任；项目完毕须用完经费，余款由实验室统筹；具体外拨安排未明确。','outputs':'进展和结题报告（含各项开支）；鼓励合作者联合发表和转化；须标注FDCT 001/2024/SKL及SKL-IoTSC(UM)/ORPXX/2026，编号错误或开始前成果不计。','ip':'已有知识产权仍归原权人；项目共同形成成果/知识产权归完成方共有，比例书面约定；商业使用须书面授权，教学科研可免费使用。','materials':'所在单位盖章申请书以邮件提交；iotsc.enquiry@um.edu.mo，+853 8822 4200；指南明示2025-08-15截止（项目年度2026—2027）。'},
 'M185':{'amount':'本年度每项4—6万元；旧表“重点5万/一般2万”未被当年指南支持，已修正。','period':'2年。','qualification':'中国国籍、博士或副高；40岁以下优先；限1家单位申报，不支持联合申报。','ip':'研究成果知识产权双方共有。','materials':'2026-08-17前Word及PDF申请材料发jiangtaozhai@nuist.edu.cn；13770698740。'},
 'M189':{'amount':'每项6万元。','period':'2年，2027—2028。','qualification':'实验室依托单位外博士或副高；中级且硕士、成果突出者可由2名高级职称专家推荐。','funds':'不外拨，经实验室秘书报销。','ip':'成果知识产权共享。','materials':'2026-06-25前纸质申请书2份、信息汇总表和电子材料至tmqz@cqusce.com；庞老师15923774535。'},
 'M194':{'lab':'固体微结构物理全国重点实验室','period':'通知未公布统一研究周期。','amount':'2026通知及指南未公布资助金额；须问实验室。','qualification':'2026通知及指南未公布明确学历/职称门槛及校外资格；须问实验室。','collaboration':'申报邮件须抄送校内合作老师；具体合作资格需确认。','outputs':'项目结束提交总结报告；成果未标注“南京大学固体微结构物理全国重点实验室/National Lab of Solid State Microstructures, Nanjing University”不计成果；未规定统一论文数量。','materials':'2026-05-06前申请书电子版发zhangwj@nju.edu.cn并抄送校内合作老师。'},
}
amounts={'M001':'10—15万元','M002':'5万元','M004':'10万元','M005':'10—15万元','M008':'30—90万元（无人机监视反制专项）','M009':'5—10万元','M010':'10万元','M011':'10—15万元','M013':'5—8万元','M015':'需求牵引不超过25万元，前沿探索不超过15万元','M018':'重点60—100万元；一般15—20万元','M024':'单项不超过10万元','M027':'5万元','M028':'3—5万元','M033':'一般5—8万元','M037':'2—3万元','M038':'1—2万元','M042':'5万元','M043':'2—4万元','M044':'5—10万元','M045':'不超过3万元','M046':'2万元','M048':'重点5万元、一般3万元','M050':'不超过2万元','M052':'1—2万元','M054':'5万元/项，拟2项','M057':'金额按项目类别见正式指南，非所有项目统一额度','M059':'重点2—3万元、一般1—2万元（结题后拨付）','M060':'重点1—2万元、一般0.5—1万元（结题后拨付）','M061':'不超过3万元','M063':'约2万元','M065':'4万元','M067':'重点4万元、一般2万元','M070':'2—4万元','M072':'不超过2万元','M073':'不超过8万元','M076':'1—3万元','M079':'0.6万元或1.2万元','M080':'一般1—2万元、重点3—5万元','M081':'5万元','M082':'一般5—10万元、重点20—30万元','M083':'不超过1万元','M085':'1—3万元','M086':'一般2万元、重点3万元','M087':'0.5—2万元','M089':'不超过5万元','M090':'3万元','M091':'5—10万元','M092':'3—5万元','M093':'3—5万元','M097':'一般60万元、重大100万元、开放30万元','M099':'8—18万元','M101':'一般5—10万元、重点10—20万元','M102':'4万元','M104':'一般1.5万元、重点3万元','M105':'8—10万元','M108':'5—10万元','M109':'3万元（首拨1万元，中期2万元）','M110':'5万元','M111':'4万元','M112':'重点3万元、一般2万元（2024年度）','M113':'重点4万元、一般2万元、培育1万元','M114':'资助类型A/B/C分别20/15/10万元（与科研匹配等级无关）','M115':'一般5—10万元、重点20—30万元','M116':'5万元','M117':'一般5—8万元、重点20万元','M118':'2万元','M119':'重点20—50万元、一般不超过10万元','M121':'不超过10万元','M129':'1万元','M130':'重点4万元、一般2万元','M131':'重点20—30万元、一般5—10万元','M133':'重点5万元、一般2万元','M134':'重点20—30万元、探索10—15万元','M136':'不少于10万元；结题前到校科研经费须≥10万元','M137':'不超过10万元','M138':'30万元（仅清华教师）','M139':'5—10万元','M140':'一般10万元、重点30万元','M141':'5—10万元','M143':'25—30万元','M144':'重点4万元、一般2万元','M145':'重点0.8万元、一般0.4万元；原则配套≥1:1','M146':'重点6—8万元、一般4—5万元','M147':'8—12万元','M149':'60—80万元','M150':'不超过20万澳门元','M151':'不超过12万澳门元','M152':'重点20—30万元、一般10—12万元、青年5—8万元','M154':'重点≥12万元、一般≥5万元','M157':'重点15万元、一般10万元、青年5万元','M158':'3—5万元','M160':'3万元','M161':'重点3万元、一般2万元','M162':'3—5万元；正文另列初拨3万元、剩余2万元凭票，具体须按获批金额确认','M163':'开放3—4万元、预研2万元；滚动3万元/年仅面向已结题获选项目','M167':'资助类型A 5—7万元/B 8—10万元（不是科研匹配等级）','M168':'不超过2万元','M169':'重点20万元、一般10万元','M170':'约10万元','M171':'5—20万元','M172':'约2万元','M173':'3—10万元','M174':'3—10万元','M175':'不超过10万元','M176':'5—10万元','M177':'5—10万元','M180':'约2万元（年度机制，不等于当年已受理）','M181':'重点4万元、一般2万元（2017年度）','M186':'5—10万元（2023年度）','M190':'重点5万元、一般2万元','M191':'不超过10万元','M193':'10万元'}
for k,v in amounts.items():manual.setdefault(k,{})['amount']=v
for node in ast.walk(ast.parse((R/'prepare_data.py').read_text(encoding='utf8'))):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='patch':
  try:
   ident=ast.literal_eval(node.args[0]);vals={x.arg:ast.literal_eval(x.value) for x in node.keywords}
  except (ValueError,TypeError):continue
  for key,value in vals.items():
   if key in patterns:manual.setdefault(ident,{}).setdefault(key,value)
  if vals.get('date') and ident not in date_overrides:date_overrides[ident]=vals['date']
date_overrides['M004']='2026-07-19'
date_overrides['D-GZU-001']='2025-06-26'
date_overrides['M163']='2026-10-10'
manual['M084']['amount']='校外开放基金1万元/项，拟5项；不能混用通用管理办法的1—3万元或校内创新基金。'
manual.setdefault('M163',{})['collaboration']='校外课题以合作形式支持，须以四川大学相关学科人员为第一合作申请人；每位合作人每年最多参与1项。'
manual.setdefault('M135',{})['collaboration']='建议邀请实验室或工程研究中心固定人员参与，不是明确强制。'
special={
 'M006':'原链接为期刊论文页面，不能证明开放课题受理；本轮未取得正式申报公告。',
 'M016':'年度机制每年8月31日，未证实2026当期仍受理；原日期不作为确认截止。',
 'M049':'旧记录来源为非官方聚合页，未取得正式指南；河南地域限制与金额未获官方证实。',
 'M055':'现有来源是立项/资助成果信息，不是开放课题申报公告。',
 'M064':'该公告征集指南建议，9月24日是建议提交截止；拟10万元不是已发布申报额度。',
 'M069':'现有来源为评审新闻，不能证明受理条件/截止。',
 'M071':'该公告征集指南建议，6月5日是建议提交截止；拟3万元不能当作正式项目额度。',
 'M073':'公告发布时间2026-07-15晚于所写截止2026-05-31，日期存在官方内部矛盾，须问实验室。',
 'M074':'现有来源是获资助成果信息，未取得当年度开放课题正式申报公告。',
 'M166':'所读页面为答辩/材料安排；4月3日不等于新课题受理截止，正式申报指南仍待取得。',
 'M179':'每年10月至12月底受理的历史机制；未取得2026正式通知，不能认定当前受理。',
 'M180':'每年10月31日是通用办法规定；未取得2026当期公告，不能认定当前受理。',
 'M182':'已核澳门科技大学官方开放课题页面，显示To Be Announced；原博士招生页面不是课题公告。',
 'M187':'已核官方章程设有开放基金/主任基金机制，未取得当前正式申报指南。',
 'M188':'现有来源是获资助新闻；单个项目10万元不能推成统一资助额度；正式当年指南未取得。',
}
audit=[];data=copy.deepcopy(raw);rows=data['02项目完整详情'][6:]
for row in rows:
 id=row[0]
 if id not in ps:continue
 p=ps[id];old=copy.deepcopy(row);s=json.load(open(R/'official'/(id+'.json'),encoding='utf8'));sources=[]
 if s.get('text') and s.get('status') in ['ok','cached_official']:sources.append({'url':s['url'],'text':s['text'],'kind':'当期正文' if id not in special else '机制/其他证据'})
 # Add latest verified special sources without overwriting history.
 for key in {'M025':['M025_guide'],'M047':['M047_history'],'M194':['M194_pdf','M194_guide_pdf']}.get(id,[]):
  d=json.load(open(A/'final_fetch'/(key+'.json'),encoding='utf8'));sources.append({'url':d['url'],'text':d['text'],'kind':'官方附件' if id!='M047' else '历史公告'})
 relevant=[]
 for a in attachments:
  if id in a.get('ids',[]) and re.search(r'指南|办法|通知|条例|制度|任务书|申请书|申请表|申报要求',a['name']) and not re.search(r'创新基金|产业发展|行业报告',a['name']):
   relevant.append(a)
   if a.get('text'):sources.append({'url':a['url'],'text':a['text'],'kind':a['name']})
 # Previously read priority attachments have independent filenames.
 for f in (R/'attachments').glob('*.json'):
  try:d=json.load(open(f,encoding='utf8'))
  except:continue
  if d.get('id')==id and d.get('text') and d.get('url') not in [q['url'] for q in sources]:sources.append({'url':d['url'],'text':d['text'],'kind':'官方附件（重点核验）'})
 byfield={};refs={};verified=[];missing=[]
 for k,pat in patterns.items():
  hits=[];urls=[]
  for src in sources:
   a=evidence(src['text'],pat)
   if a:
    # Field extracts are accompanied by exact source URL in the audit log.
    for x in a:
     if x not in hits:hits.append(x)
    urls.append(src['url'])
  if k in manual.get(id,{}):v=manual[id][k];verified.append(k);urls=urls or [q['url'] for q in sources]
  elif hits:
   v='\n'.join(hits)
   if len(v)>10000:v=v[:10000]+'\n更多条款请直接查看所列官方指南。'
   verified.append(k)
  elif k in p.get('field_verified',[]) and id not in special:v=p[k];verified.append(k);urls=[p['url']]
  else:v='未在已取得的官方资料中确认；需向实验室核实。';missing.append(labels[k])
  # Do not present obsolete/unrelated source statements as annual application rules.
  if id in special and k in ['amount','qualification','collaboration','period','materials']:
   v=special[id]+'\n当期'+labels[k]+'未确认。';verified=[x for x in verified if x!=k];missing.append(labels[k])
  if re.search('未公布|未公开|未明确|待核|需.*确认|需.*核实|未取得|未确认',v) and k not in ['qualification','outputs']:missing.append(labels[k]+'未完全明确')
  byfield[k]=v;refs[k]=list(dict.fromkeys(urls))
 # Clear publication dates and dates of suggestion calls rather than perpetuating them.
 date=None;dateproof=[]
 for src in sources:
  t=re.sub(r'\s+','',src['text'])
  for m in re.finditer('截止|截至|申报时限|受理时间|申报时间|申请时间',t):
   frag=t[max(0,m.start()-40):m.end()+100]
   for y,mo,day in re.findall(r'(202\d)[年./-](\d{1,2})[月./-](\d{1,2})',frag):
    try:d=datetime.date(int(y),int(mo),int(day)).isoformat()
    except ValueError:continue
    dateproof.append((d,frag,src['url']))
 olddate=old[4] if isinstance(old[4],str) and re.fullmatch(r'20\d\d-\d\d-\d\d',old[4]) else None
 if olddate in [x[0] for x in dateproof]:date=olddate
 elif len(set(x[0] for x in dateproof))==1:date=dateproof[0][0]
 if id in date_overrides:date=date_overrides[id]
 if id=='M047':date='2022-10-30'
 if id in special:date=None
 if id=='M056':date=None
 if date:
  status='已截止（已核日期；留作历史参考）' if date<'2026-10-08' else '今日截止·受理时点及本人资格待确认' if date=='2026-10-08' else '日期未过·本人资格及是否仍受理待确认'
  row[4]=date
 else:
  status='批次/受理信息待核'
  row[4]='未确认正式截止日期'
  missing.append('正式截止/当期受理')
 if id in special:status='机制或非申报公告·未确认当期受理'
 if id=='M047':status='已核2022历史公告·2026待核'
 if id=='M056':status='滚动合作机制·具体受理及资格待确认'
 if id=='M138':status+='；仅清华校内教师'
 if id in ['M038','M175']:status+='；限指定校内/合作人员'
 row[5]=status
 for k,col in [('amount',9),('qualification',10),('collaboration',11),('funds',12),('period',13),('materials',15)]:row[col]=byfield[k]
 row[14]=byfield['outputs']+'\n知识产权：'+byfield['ip']
 # Verify the scope stated in the notice; keep former reuse notes explicitly separate.
 scope=''
 if id not in special:
  for src in sources[:3]:
   m=re.search(r'[一二三四五]、\s*(?:资助方向|指南内容|开放课题主要研究方向|重点支持方向|研究方向|重点资助领域|支持方向|主要资助方向|研究领域|开放课题的主要研究方向)(.*?)(?=[二三四五六]、|$)',clean(src['text']),re.S)
   if m and len(m.group(1).strip())>50:scope=m.group(1).strip()[:6000];break
 if id=='M165':scope='智能感知与网络通信、城市大数据与智能技术、智慧能源、智能交通、公共安全与防灾；研究须服务智慧城市物联网。'
 if id=='M164':scope='无线通信、数据转换器、电力电子、生物医学电子、人工智能、物联网电子、大面积电子、量子接口；研究须围绕模拟和混合信号微电子。'
 if id=='M150':scope='科研成果转化与创新创业生态系统相关研究；不是医疗机器人本体研发专项。'
 if id=='M194':scope='微结构物理与光声调控、量子材料、能源材料多尺度微结构、软物质微结构与功能；软物质是物理/材料研究边界，不能直接等同人体接触控制。'
 if scope:row[7]='官方指南范围：'+scope+'\n原台账可复用判断（本步不重评匹配等级）：'+str(old[7] or '')
 if s.get('status') in ['ok','cached_official']:row[16]=s['url']
 if id=='M047':row[2]='哈尔滨理工大学';row[16]='https://amit.hrbust.edu.cn/home/news/100';row[17]=old[16]
 if id=='M194':row[3]=manual[id]['lab'];row[17]=sources[-1]['url']
 if id=='M182':row[16]='https://www.must.edu.mo/cn/ssi/open';row[17]=old[16]
 if id=='M187':row[16]='https://cps.cqu.edu.cn/sysgk/syszc.htm'
 if id=='M073':row[2]='工业人工智能研究院（南京江宁）'
 if id=='M032':row[2]='煤炭智能开采与岩层控制全国重点实验室（北京；具体依托机构待核，沈阳化工为转载单位）'
 if id=='M114':row[2]='中铁大桥勘测设计院集团有限公司、中铁大桥局集团有限公司、西南交通大学（共同依托）'
 if id=='M091':row[2]='重庆建筑工程职业学院（联合交通企业共建）'
 if id=='M133':row[2]='辽宁省交通高等专科学校'
 row[18]='本轮已逐项查阅可取得的官方证据；正文'+s['status']+'；已获官方字段：'+('、'.join(labels[k] for k in verified) or '无完整申请规则')
 failed=[a for a in relevant if not a.get('text')]
 row[19]='相关附件'+str(len(relevant))+'件：已提取'+str(len(relevant)-len(failed))+'件，未取得全文'+str(len(failed))+'件；未取得不视为已读。'
 row[20]='2026-10-08；以当年度正式通知及对应指南为准；历史办法/申请表补充规则需对照。'
 notes=[]
 if id in special:notes.append(special[id])
 if id=='M047':notes.append('依托机构原填南航系公告转载误归属，现核为哈尔滨理工大学；仅找到官方2022历史公告，原2026 PDF无法取得。')
 if id=='M117':notes.append('已核官网延期通知至2025-03-31，原3月15日失效。')
 if id=='M192':notes.append('2026指南通知实际发布于2025-09-15，10月31日应为2025年；官网检索另见2027通知线索，但未取得正文，不能推断当前受理。')
 if id=='M176':notes.append('本轮所读正式公告为2027年度课题，截止2026-08-30；所附管理办法是2026修订版，不能混淆项目年度。')
 if id=='M100':notes.append('2026申报指南及管理办法官网下载需验证码，已查到入口但未取得全文；金额与资格须取得附件后确认。')
 if id in ['M062','M084','M022','M152','M114','M126']:notes.append('当年通知与通用管理办法存在额度、资格、产权或年度文字差异；按当年规则核，不混合资助类型；申报前向实验室确认冲突条款。')
 if failed:notes.append('未取得全文附件：'+'；'.join(a['name'] for a in failed))
 row[21]='；'.join(notes+(['仍缺：'+'、'.join(dict.fromkeys(missing))] if missing else ['公开规则已补；本人资格、合作落实与实际受理需申报前确认']))
 for col,v in enumerate(row):
  if v!=old[col]:
   ev=refs.get({9:'amount',10:'qualification',11:'collaboration',12:'funds',13:'period',14:'outputs',15:'materials'}.get(col,''),[])
   if col==14:ev+=refs.get('ip',[])
   audit.append([id,raw['02项目完整详情'][5][col],str(old[col] or ''),str(v or ''),'\n'.join(dict.fromkeys(ev or [q['url'] for q in sources])),'2026-10-08'])
 p.update(byfield);p['date']=date;p['date_verified']=bool(date);p['status']=status;p['source_status']=row[18];p['attachment_status']=row[19];p['missing']=row[21];p['field_verified']=verified;p['field_sources']=refs;p['url']=row[16];p['second']=row[17];p['org']=row[2];p['lab']=row[3];p['changes'].append('本轮逐项核对正文与附件，未取得内容明确待核；原始值另保留。')
 byfield['id']=id;byfield['date']=date
 p['status_rank']=4 if date and date<'2026-10-08' else 0 if date=='2026-10-08' else 1 if date else 3
 # Keep original summary order, columns and matching grades; synchronize only facts.
 sr=next(x for x in data['01申报总览'][6:] if x[10]==id)
 sr[2]=status;sr[3]=row[2]+' — '+row[3];sr[4]=row[4];sr[6]=row[9];sr[7]=row[10]+'\n'+row[11];sr[8]=row[21];sr[9]=row[16]
 sr[0]='其他资金' if str(id).startswith('F') else '历史储备' if date and date<'2026-10-08' else '近期候选' if date else '待确认批次'
 assert row[22:25]==old[22:25],id
# Institution coverage: every original institution had both name-based and domain-specific queries.
searches=[]
for f in R.glob('institution_searches_*.json'):searches+=json.load(open(f,encoding='utf8'))
inst=json.load(open(R/'institutions.json',encoding='utf8'));domains=json.load(open(R/'domains.json',encoding='utf8'))
querymap={x['name']:x for x in searches}
for row in data['03机构检索覆盖'][6:]:
 if not row[1] or row[1] not in querymap:continue
 q=querymap[row[1]];result=q['result'];urls=list(dict.fromkeys(re.findall(r'https?://[^\s)<>]+',result)))
 domain=next((x.get('domain','') for x in domains if isinstance(x,dict) and x.get('name')==row[1]),'') if isinstance(domains,list) else ''
 official=[u for u in urls if (domain and domain in u) or '.edu.cn/' in u or '.ac.cn/' in u or '.um.edu.mo/' in u or 'polyu.edu.hk/' in u]
 row[4]=str(row[4] or '')+'\n2026-10-08：本轮完成机构名及官网域名定向检索。证据入口：\n'+'\n'.join(official[:8] or urls[:3])
 row[5]='检索未发现≠不存在；未发布金额/资格/日期、未取得附件或仅有平台/历史机制的项目，已在对应项目待核栏列明。'
 row[6]='本轮定向检索完成；不等于所有平台穷尽核查'
 row[7]=str(row[7] or '')+'；检索记录保留，按官网证据确认。'
 row[8]='当前已查范围无需重复；后续仅跟进已列待核事项或新年度正式公告。'
# Keep a separate entry for each attachment so the evidence URL remains individually clickable.
for a in attachments:
 for ident in a.get('ids',[]):
  if ident not in ps:continue
  if not re.search(r'指南|办法|通知|条例|制度|任务书|申请书|申请表|申报要求|汇总表',a['name']):continue
  audit.append([ident,'官方附件入口',a['name'],a['status']+'；有链接不等于成功读取',a['url'],'2026-10-08'])
for u,name in [('https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041515','2026申报指南'),('https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041517','管理办法')]:
 audit.append(['M100','官方附件入口',name,'需验证码，未取得全文',u,'2026-10-08'])
# Fixed title information only; no presentation redesign and no new nationwide project list.
data['01申报总览'][1][0]='核查日2026-10-08｜保持原展示顺序；已截止保留；日期未过≠本人已确认可申请；缺失或无法取得的信息明确待核。'
data['01申报总览'][2][9]='199条（全部保留）'
data['04本轮信息核验日志']=[['项目编号','修正/补充字段','原始值（历史保留）','本轮值','对应官方证据URL','核查日期']]+audit
(A/'audited_original_layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(R/'normalized.json').write_text(json.dumps(norm,ensure_ascii=False,indent=2),encoding='utf8')
report={'original_projects':len(rows),'audited_projects':len(ps),'field_changes':len(audit),'institution_queries':len(searches),'attachments':dict(collections.Counter(a['status'] for a in attachments))}
(A/'completion_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(report)
