import json,re,pathlib,collections,urllib.parse
ROOT=pathlib.Path(__file__).parent
raw=json.load(open(ROOT/'original.json',encoding='utf8'))
rows=[r for r in raw['02项目完整详情'][6:] if r[0]]
inst=json.load(open(ROOT/'institutions.json',encoding='utf8'));domains=json.load(open(ROOT/'domains.json',encoding='utf8'))
TODAY='2026-10-08'
# Grades are independently assigned from the proposal's four research tasks, not old priority.
A='M001 M002 M004 M009 M016 M020 M027 M031 M034 M045 M050 M056 M062 M063 M064 M066 M070 M074 M076 M078 M084 M086 M092 M093 M096 M098 M108 M111 M148 M186 F001'.split()
B='M005 M006 M007 M008 M011 M012 M013 M014 M015 M017 M018 M019 M021 M022 M023 M024 M025 M026 M029 M030 M032 M033 M035 M036 M037 M038 M039 M040 M041 M042 M046 M047 M048 M049 M051 M052 M053 M054 M057 M058 M059 M060 M061 M065 M067 M068 M069 M072 M073 M075 M077 M080 M081 M082 M083 M085 M087 M088 M089 M090 M091 M094 M095 M097 M099 M100 M101 M102 M103 M104 M105 M106 M107 M109 M110 M112 M115 M116 M117 M118 M120 M121 M122 M124 M125 M126 M127 M130 M131 M132 M133 M135 M137 M138 M142 M146 M152 M154 M156 M160 M161 M162 M164 M165 M166 M175 M181 M185 M187 M189 M190 F002 F003 F004 D-CAS-001 D-GZU-001'.split()
assert not set(A)&set(B)
# General image/data keywords without the proposal's contact/feedback/planning mechanism are C.
for item in 'M019 M037 M039 M040 M058 M065 M082 M085 M087 M099 M104 M107 M110 M127 M130 M135 M152 M156 M162 M164 M165 M181'.split():
 if item in B:B.remove(item)
for item in ['M074','M092','M093']:
 A.remove(item);B.append(item)
methods={
 'M001':'柔性多体系统动力学、智能机器人自主学习及既有薄壁构件控制研究均可实质复用；选智能机电系统方向，不沿用国防振动任务。',
 'M002':'一般开放方向明确含人机交互共融和高端医疗装备，可直接采用超声机器人接触建模、图像反馈及柔顺控制。',
 'M004':'柔性触觉和医疗微创传感可复用多模态力觉/视觉融合模块；须以传感器机理或器件/系统验证为核心。',
 'M009':'指南明确医疗机器人、灵巧操作控制和多模态具身智能，与感知—规划—柔顺控制闭环直接对应。',
 'M016':'生医机械、生物摩擦学及界面粘附控制可实质复用人体软组织—探头接触模型；须突出界面力学，不仅写通用机器人。',
 'M020':'超声成像与智能医疗装备可直接复用超声图像质量评价、力—成像耦合及多模态扫描方法。',
 'M027':'数字人体与智能数字诊疗可实质复用软组织耦合建模和超声多模态数据；须围绕数字人/数字诊疗目标凝练。',
 'M031':'正式历史指南列智能医疗机器人、力触觉反馈和柔性控制，研究对象和方法均直接一致。',
 'M034':'医疗机器人、多模态实时建模、自主学习与行为优化可直接复用申请书四项研究内容。',
 'M045':'机器人系统智能控制理论、自主系统与多源感知方向可直接复用鲁棒/最优阻抗学习和扫描安全规划。',
 'M050':'图像信息处理与智能控制可实质复用图像质量反馈优化、多模态估计与学习控制；选对应指南条目。',
 'M056':'柔性医疗机器人、机器人控制感知学习、活体组织特性表征支持直接复用接触模型和柔顺扫描；合作课题组资格另核。',
 'M062':'指南含不限于运动控制技术，可直接复用非线性鲁棒运动控制、扰动补偿和最优阻抗控制基础，不必转做电力电子。',
 'M063':'机器人控制、信息感知和融合均可自由拟题，超声机器人闭环感知及柔顺控制可直接采用。',
 'M064':'灵巧操作与运动控制可实质复用接触交互、技能学习及阻抗控制；需使用人形机器人作为验证载体。',
 'M066':'混杂动态建模、反馈镇定、非标准最优控制与多模态融合可直接复用时变接触模型、力优化和阻抗学习；无医学场景排除。',
 'M070':'机器人视觉—力觉融合、自适应鲁棒控制及医疗机器人，与图像反馈力优化和柔顺控制直接一致。',
 'M074':'先进诊疗技术与装备可直接复用超声图像反馈和智能诊疗装备；原链接为立项通知，不能证明当前受理。',
 'M076':'指南明确柔性传感、人机交互、具身决策控制和医疗应用，可直接采用多模态超声扫描与柔顺控制。',
 'M078':'正式方向二明确智能医疗机器人、力触觉反馈、柔性控制及人机协同，可直接复用四项研究任务。',
 'M084':'机器人视觉、运动规划及智能控制可实质复用多模态扫描路径、安全约束与鲁棒学习控制。',
 'M086':'正式指南包含医疗机器人与康复工程、医工装备与AI，可直接复用医疗接触建模及图像反馈柔顺控制。',
 'M092':'磁控医疗机器人可复用医学影像导航、柔顺交互与鲁棒控制；执行器须调整为磁驱动，不应照搬硬件。',
 'M093':'同一医学机器人方向的后续年度记录，可实质复用影像导航与接触控制；磁驱动平台需重设计。',
 'M096':'专项明确超声成像及AI质量评价，可直接复用图像质量—接触力优化模块；临床样本和设备条件另核。',
 'M098':'医疗机器人影像融合、感知导航与控制可实质复用多模态反馈和安全交互；须针对支气管镜场景验证。',
 'M108':'医疗机器人、柔性操作、自适应预测和鲁棒控制可直接复用最优阻抗学习与扰动补偿。',
 'M111':'生物医学工程的医学图像和智能设备可实质复用超声成像反馈与多模态接触扫描，选医工装备方向。',
 'M148':'指南人因方向三明确人体背部皮肤软组织弹性形变、三维扫描和接触体压仿真，与接触建模实质一致；应用需改为坐具体压评价。',
 'M186':'康复/软体机器人及人机交互可直接复用软组织接触建模与柔顺控制；仅核到2023历史批次。',
 'F001':'公告明确支持超声及医工研究，与超声机器人图像反馈力优化直接相关；具体指南条目和个人资格尚待附件确认。',
 'M003':'本批为指定DR/MRI/CT等临床任务，含多中心临床门槛；超声机器人接触建模与柔顺控制难以直接复用，不能仅因医疗装备名称判A。',
 'M043':'正式2026方向围绕极端环境微纳测控器件，旧表“微纳机器人”不能据此成立；软组织/超声控制没有直接研究对象。',
 'M014':'2026须按指定课题名申报，包含人形多点接触/灵巧多任务/移动操作；可迁移技能学习及安全规划，但须满足规定载体和指标。',
 'M024':'正式方向以工控装备/软件为牵引；最优控制和感知有实质方法交集，但应迁移到工业控制验证。',
 'M025':'湖控为工业控制专项，控制优化可迁移，但不据实验室名称将超声机器人直接判为最相关。',
 'M035':'高自由度遥操作及柔性织物双臂操作，可复用既有弱刚性/柔软物体交互与技能学习；本年度规定任务不是超声扫描。',
 'M017':'2026指南主要限高端装备制造测量、极端服役及近极限光学测量；可基于既有薄壁加工力/表面质量建模迁移，不能直接提交医疗扫描课题。',
 'M041':'脑启发感知、知识学习与决策有方法交集，但须形成脑启发机制和验证；申请书常规ResNet/RL不等于脑启发成果。',
 'M068':'多模态点云融合、路径规划和机械臂抓取可迁移体表重建/扫描规划；须选无人系统或虚实融合等指南方向。',
 'M106':'医学信息监测/处理与机器视觉可复用图像质量评价和多模态估计；指南未直接提出软接触力优化，宜凝练感知/成像子课题。',
 'M077':'大模型/世界模型导向，现申请书主要是BLS、DMP及阻抗学习；需补大模型研究，且0.5万元与至少3篇论文义务不相称。',
 'M160':'时滞/网络系统鲁棒控制和最优化可迁移非线性建模与扰动补偿；须满足工业装备对象，不直接沿用医学扫描。',
 'M161':'机械传动与机电液控制可迁移动态建模和鲁棒/最优控制；须围绕传动或制造装备验证，并完成至少2篇ESI工程学论文。',
 'M142':'纺织具身智能/柔性制造可复用柔软对象接触和技能学习基础；申请要求纺织场景，不能用医学扫描替代。',
 'M049':'2026发布报道要求面向河南省内单位；人形机器人本体/应用可迁移方法，南京依托单位不能据报道认定符合资格。',
 'M187':'机器人强化学习团队提供方法交集，但研究团队/章程不等于当年开放课题指南，匹配暂按B而非直接A。',
 'M112':'机器人感知与控制平台具有方法交集；现网址为学院平台信息，未取得年度方向与实际资助指南，暂按B保守评估。',
 'M007':'2026重点任务限定极端固体/流动/材料界面等对象，超声软组织场景未列入；非线性接触建模只能向一般交叉方向迁移并先核范围。',
 'M157':'正式2027任务限定公安侦查、物证与公共安全，和超声机器人对象明显不同，旧表高匹配应降C。'
}
methods.update({
 'M074':'原链接仅为医学装备立项名单，尚未核到对应年度研究指南；诊疗装备有潜在方法交集，先按B，不凭平台名判直接A。',
 'M092':'磁驱动微型机器人与当前探头接触阻抗系统载体差异明显，可迁移影像导航和控制算法；须重新建立磁场/微机器人动力学，判B。',
 'M093':'后续年度磁医学批次；影像导航与控制可迁移，但需磁驱动系统建模和验证，不能直接套超声探头阻抗方案，判B。',
 'M156':'2024指南的陪伴机器人重点是异构算力、康养数据训练和交互服务，并未支持物理接触/柔顺扫描；仅有多模态/机器人关键词交集，判C。',
 'M181':'2017历史指南重点大数据安全、隐私、通信网络和数据挖掘；仅共享通用学习/视觉数据算法，不能实质复用接触控制与超声扫描，判C。'})
def canonical(name):
 name=re.sub(r'^(四川|北京|安徽|陕西|辽宁|湖北|河南|江苏|内蒙古)[·•]','',name or '')
 name=name.replace('相关平台','').replace('相关教育部工程中心','').replace('科技处转发','')
 aliases={'常熟理工学院':'苏州工学院','澳门大学各全国重点实验室':'澳门大学','澳门科技大学各全国重点实验室':'澳门科技大学','上海医疗机器人研究院及柔性医疗机器人平台':'上海交通大学','上海交通大学医疗机器人研究院/同仁医院':'上海交通大学','中科院苏州纳米技术与纳米仿生研究所':'中国科学院苏州纳米技术与纳米仿生研究所','合肥智能机械研究所':'中国科学院合肥物质科学研究院','北京师范大学—香港浸会大学联合国际学院':'北师香港浸会大学（原UIC）'}
 return aliases.get(name,name)
def geography(name,hint=''):
 n=canonical(name)
 if n in ['南京信息工程大学'] or '南京' in n or n in ['东南大学','河海大学','中国药科大学','江苏省产业技术研究院','江苏省人民医院等医学科研平台','中国农业科学院南京农业机械化研究所']:return 'P0 南京及周边',0,'南京'
 if '澳门' in n:return 'P0 澳门',1,'澳门'
 if n in ['香港理工大学']:return 'P0 香港',2,'香港'
 if n=='香港科技大学（广州）关联深圳协作平台':return 'P0 广州及周边',3,'广州'
 if n=='华南理工大学' or n in ['中山大学','暨南大学','华南师范大学','南方医科大学','广东工业大学','广州大学','广州医科大学','广东省科学院'] or '广州' in n or '广东华中科技大学' in n:return 'P0 广州及周边',3,'广州/东莞'
 if n=='中国科学院自动化研究所' or '北京' in n or n in ['清华大学','中国人民大学','中央民族大学','中国农业大学','中国科学院力学研究所','中国科学院计算技术研究所','中国科学院物理研究所','中国科学院半导体研究所','中国标准化研究院','中国铁道科学研究院集团有限公司/中国中车','国家科技信息资源综合利用与公共服务中心']:return 'P1 北京及周边',4,'北京'
 if '西北工业大学宁波' in n:return 'P2 长三角·宁波',7,'宁波'
 if n=='西北工业大学' or '西安' in n or '西北农林' in n or '长安大学' in n:return 'P1 西安及周边',5,'西安/咸阳'
 if '重庆' in n:return 'P1 重庆',6,'重庆'
 if n in ['北京理工大学、同济大学','同济大学']:return 'P2 长三角·上海',7,'上海'
 if '上海' in n or n in ['复旦大学','华东师范大学','华东理工大学','东华大学','中国科学院脑科学与智能技术卓越创新中心']:return 'P2 长三角·上海',7,'上海'
 if any(x in n for x in ['苏州','江苏大学','江苏科技大学','常州','扬州','无锡','江南大学','徐工集团','江苏省工业人工智能']):return 'P2 长三角·苏锡常镇扬',8,'苏锡常镇扬/徐州'
 if any(x in n for x in ['浙江','杭州','宁波','西湖大学']):return 'P2 长三角·浙江',9,'浙江'
 if any(x in n for x in ['安徽','合肥','江淮实验室']) or n=='中国科学技术大学':return 'P2 长三角·安徽',10,'安徽'
 if any(x in n for x in ['深圳','光明实验室','鹏城实验室','深圳湾','国家高性能医疗器械','哈尔滨工业大学（深圳）','香港中文大学（深圳）']):return 'P2 粤港澳·深圳',11,'深圳'
 if '东莞' in n or '松山湖' in n or '北师香港浸会' in n or '广东省智能机器人' in n or '美的集团' in n:return 'P2 粤港澳·其他',12,'东莞/珠海/佛山'
 if '香港' in n or 'ASTRI' in n or '岭南大学' in n:return 'P0 香港',2,'香港'
 # Specific local place names for the rest; institution domains are retained separately.
 places=[(['天津','南开'],'天津'),(['山东科技','中国海洋'],'山东·青岛'),(['山东大学','齐鲁工业'],'山东·济南'),(['潍柴'],'山东·潍坊'),(['烟台'],'山东·烟台'),(['中北'],'山西·太原'),(['大连'],'辽宁·大连'),(['沈阳','工业人工智能研究所','东北大学'],'辽宁·沈阳'),(['吉林'],'吉林·长春'),(['哈尔滨'],'黑龙江·哈尔滨'),(['武汉','湖北','华中','江汉','中南民族','精密测量'],'湖北·武汉'),(['湖南','中南大学','国防科技'],'湖南·长沙'),(['四川大学','电子科技大学','西南交通','西华'],'四川·成都'),(['四川文理'],'四川·达州'),(['泸州','四川警察'],'四川·泸州'),(['南昌'],'江西·南昌'),(['华东交通'],'江西·南昌'),(['厦门'],'福建·厦门'),(['福州','闽江'],'福建·福州'),(['河南','郑州','中原'],'河南'),(['贵州'],'贵州'),(['云南','昆明'],'云南'),(['海南','深海科学'],'海南'),(['青海'],'青海'),(['新疆','克拉玛依'],'新疆'),(['宁夏'],'宁夏'),(['兰州'],'甘肃·兰州'),(['内蒙古'],'内蒙古'),(['河北'],'河北')]
 for keys,place in places:
  if any(x in n for x in keys):return 'P2 '+place,20,place
 return 'P2 全国/地点待核',99,'地点待核'
familiar={'南京信息工程大学':0,'澳门大学':0,'香港理工大学':0,'华南理工大学':0,'中国科学院自动化研究所':0,'西北工业大学':0,'重庆大学':0}
def derive_method(r,grade):
 if r[0] in methods:return methods[r[0]]
 direction=(r[7] or '').replace('与申请书的匹配方向：','').replace('匹配研究方向：','').replace('方向/边界：','')
 if grade=='B':
  modules=[]
  if re.search('控制|动力|建模|优化',direction):modules.append('非线性建模、扰动补偿或最优控制')
  if re.search('感知|视觉|图像|多模态|融合|测量',direction):modules.append('多模态估计、图像特征或三维几何处理')
  if re.search('规划|学习|机器人|具身|决策',direction):modules.append('技能学习或约束运动规划')
  return '可迁移'+('、'.join(modules) or '部分学习/数值算法')+'；当前指南/平台主题为“'+direction+'”。须补该场景数据、验证平台与考核要求，不能直接照搬医学超声目标。'
 return '主题为“'+direction+'”。与软组织接触、图像反馈力优化、自主超声扫描和最优阻抗学习缺乏实质对应；有限通用算法交集不足以直接复用申请书。'
def load_source(id):
 return json.load(open(ROOT/'official'/f'{id}.json',encoding='utf8'))
projects=[]
for r in rows:
 id=r[0];src=load_source(id);grade='A' if id in A else 'B' if id in B else 'C'
 text=src.get('text','');text=re.split('上一篇|下一篇|上一条|下一条|最新动态',text)[0]
 title=(text.splitlines()[0] if text else '')
 years=re.findall(r'(20\d{2})(?:[—－-](20\d{2}))?\s*年?度',title)
 year=(years[0][0]+('—'+years[0][1] if years[0][1] else '')) if years else '年度待核'
 org=canonical(r[2]);region,rank,city=geography(org)
 good=src.get('status')=='ok' and ('开放' in text) and not re.search(r'Access Denied|请求被拦截|验证您的浏览器|verify you are human',text,re.I)
 date=r[4] if re.fullmatch(r'20\d\d-\d\d-\d\d',str(r[4])) else None
 # Keep old unsupported facts explicitly labelled, rather than turning an HTTP success into verification.
 p=dict(id=id,type=r[1],org=org,lab=r[3],region=region,region_rank=rank,city=city,grade=grade,year=year,date=date,
   directions=(r[7] or '').replace('与申请书的匹配方向：','').replace('匹配研究方向：',''),fit=derive_method(r,grade),
   amount=r[9] or '未公布/待核',qualification=r[10] or '申请资格待核',collaboration=r[11] or '合作要求待核',funds=r[12] or '经费外拨与使用待核',period=r[13] or '周期待核',outputs=r[14] or '成果及署名待核',ip='知识产权归属待核',materials=r[15] or '材料及方式待核',url=r[16],second=r[17],
   source_status='已读取官网正文；字段仍须逐项核实' if good else '原链接未成功取得正式正文；继承旧表并标待核',
   attachment_status='未完成逐附件复核',check_date=TODAY,missing=r[21] or '未核字段待补',
   raw_qualification=r[22],lineage=r[23],old_id=r[24],raw_note=r[25],plan_group=id,
   field_verified=[],date_verified=False,eligibility='本人学历/职称、年龄及合作安排未逐项确认；不能据匹配度认定可申请',changes=[])
 if good and date:
  # An identical full-year deadline adjacent to a deadline word is evidence; short dates stay pending.
  for m in re.finditer('截止|申请时间|受理时间|申报时间',text):
   piece=text[max(0,m.start()-25):m.end()+125]
   dates=[f'{y}-{int(mo):02d}-{int(da):02d}' for y,mo,da in re.findall(r'(202\d)\s*[年./-]\s*(\d{1,2})\s*[月./-]\s*(\d{1,2})',piece)]
   if date in dates:p['date_verified']=True
 if id.startswith('F') or id in ['M138','M150']:p['type']='其他资助/非外部实验室开放基金'
 if id=='M112' or id=='M187':p['type']='平台/开放机制线索（年度指南未取得）'
 if id=='M135':p['type']='多平台联合线索（具体计划待核）'
 projects.append(p)
P={p['id']:p for p in projects}
def patch(id,**kw):
 p=P[id]
 for key,value in kw.items():
  if p.get(key)!=value:p['changes'].append(key+'：'+str(p.get(key))+' → '+str(value))
  p[key]=value
 verified=[x for x in kw if x in ['amount','qualification','collaboration','funds','period','outputs','ip','materials','directions','date','year','url']]
 p['field_verified']=sorted(set(p['field_verified']+verified))
 if 'date' in kw:p['date_verified']=True

patch('M078',year='2026',date='2026-10-31',amount='1—3万元/项',qualification='实验室以外科研人员；博士学位或中级以上职称；在研课题不得重复；鼓励青年（一般≤40岁，并非硬性上限）',collaboration='须联合本实验室固定研究人员申报；申请书至少列1名实验室成员',funds='按苏州工学院财务制度；设备费、业务费、知识产权费用；是否外拨未明示',period='不超过12个月',outputs='论文第一作者或通讯作者单位须标注实验室（不限制完成单位排序）；标注基金和编号；论文/专利/软著等数量以管理办法或任务书为准，指南未规定最低篇数',materials='申请书经所在单位同意、单位盖章和负责人签章；按模板要求合成PDF，发送liqiaoshan@szut.edu.cn；2026-10-31前',missing='固定合作者和个人资格；经费是否外拨；管理办法/任务书的最低成果指标；知识产权条款',attachment_status='申请书DOCX已全文读取')
patch('M066',year='2026',date='2026-10-15',amount='一般2万元/项（1—2项）；重点5万元/项（2—3项）',qualification='国内高校、科研院所或企事业科研人员；博士或中级及以上；同年1项，在研最多1项',collaboration='正文未规定必须联合固定人员申请；结题论文第一作者或唯一通讯作者必须为山东科技大学人员，实质合作不可缺',period='2026-10-24—2027-10-23（1年）',funds='按实验室开放基金管理办法；公告及所读模板未明示外拨方式',outputs='一般：2篇中科院二区及以上SCI；重点：2篇SCI且至少1篇一区，并获省部级科技进步二等奖及以上1项或国家级重点项目1项。均排除预警期刊和开源期刊；第一作者或唯一通讯作者须山东科技大学人员，署山东科技大学和实验室。奖励须山东科技大学为完成单位且实验室成员参与',materials='双面打印申请书签字盖章原件4份+申请书电子版+汇总表电子版；邮件主题单位-姓名-课题名称；邮箱sdzngzkfkt2026@126.com；青岛市前湾港路579号266590，陈老师',missing='山东科技大学论文合作/署名安排；本人资格；完整管理办法外拨/IP规则；重点奖励/国家重点项目能否满足',attachment_status='ZIP内申请模板已读取；完整管理办法未取得')
patch('M160',year='2026',date='2026-10-27',amount='一般项目3万元/项，拟1—3项',qualification='国内外科研院校科研人员；实验室固定人员不能申请；须有研究基础；同年限1项、在研限1项。指南未明示学历/职称硬门槛',collaboration='必须至少1名实验室固定研究人员作为合作者；鼓励短期来室合作',period='2026-10—2028-09（2年）',funds='可一次性外拨负责人所在单位，或凭发票来实验室核销；外拨收到经费15日内寄普通增值税发票/事业单位往来票据。支出材料、测试计算分析、能源动力、交流差旅、出版/IP及咨询等',ip='研究成果归本实验室和项目负责人共有（管理办法第十七条）',outputs='成果须署实验室中英文名称；指南/管理办法未规定最低论文篇数；次年6月中期报告，期满1个月内结题报告和证明',materials='申请书本人亲笔签字、单位盖章，双面纸质2份；电子申请书及汇总表发送hujingtumu@dlut.edu.cn；大连理工大学海山楼B1110；立项通知后15日内任务书',missing='固定合作者；个人在研/限项；工业装备选题和最终任务书指标',attachment_status='管理办法、申请书DOCX已全文读取；汇总表XLS未逐格复核')
patch('M017',year='2026',date='2026-10-18',amount='普通开放课题4—8万元（本轮通知优先于2021管理办法的5—10万元）',qualification='实验室固定人员以外相关科研人员/博士后；天津大学教职工和学生不能申请；优先实质合作并提供推荐信。博士/高级为优先条件，不把优先条件写成硬门槛',collaboration='必须指定实验室固定研究人员联系人；每人仅能联系1项，同时为多项联系人则涉及课题均无效',period='2026-12-01起，不超过3年',funds='经费分期拨到国内承担单位；每次拨款须先提供对应金额发票；中期与结题提交经费说明及单位财务公章；研究材料、测试加工、差旅会议、出版/IP等',outputs='按申请书承诺完成；年度/结题报告；论文标注开放基金资助或实验室完成单位。2026指南/所附管理办法未规定最低篇数',ip='所附管理办法要求专利等在进展/总结报告汇报；未明确产权划分，需合同核实',materials='10-18前：WORD/PDF申请书+签字盖章推荐信电子版发pilab@tju.edu.cn。10-25前寄到：申请书原件3份+推荐信原件1份，天津大学第五教学楼215王明方，022-27406643；国内申请单位须法人级盖章',directions='2026指南限高端装备制造测量、极端服役测量、仪器核心部件/近极限测量。较可迁移：加工力—表面粗糙度在线模型（既有薄壁制造基础）；非医疗机器人专项',missing='有效固定联系人及推荐信；制造测量选题适配；知识产权合同',attachment_status='RAR完整解包；申请通知、2026指南、2021管理办法PDF及申请/推荐信DOCX已取得，PDF全文已读')
patch('M056',year='滚动机制（正文落款2025-04-23；页面2026-07-20）',date=None,url='https://imr.sjtu.edu.cn/hot_recommend/4483.html',amount='未公开，须向实验室取得当期指南',qualification='高级职称或博士学历学位；申请人为实验室课题组或合作课题组的科研/临床人员；重点负责人原则上为博导；有相关前期基础',collaboration='须属于实验室课题组或合作课题组；可独立申请或医工联合。非简单“全体校外人员自由申请”',period='滚动支持；项目期限及当期窗口须咨询',funds='经费构成和是否外拨未公开',outputs='页面仅说明结题优秀可优先下一周期；篇数、署名、产权须取正式指南/合同',materials='先发送基本信息、联系方式、学习工作经历及主要学术成就，邮件主题姓名-单位-市重点实验室开放课题咨询。徐老师18917129802；页面邮箱未显示，需电话索取',missing='当期是否接收、合作课题组资格、正式指南、金额/周期/经费/成果/IP、完整邮箱',source_status='已读正式开放课题页面；页面发布时间与正文落款跨年，保留冲突，不认定2026新批次',attachment_status='正式页面未提供可下载指南；需向联系人索取')
patch('M035',year='2026',date='2026-10-08',amount='金额未公布，评审确定',qualification='博士或副高及以上；实验室固定人员以外优先；同年限1项、在研限1项',collaboration='至少1名实验室固定研究人员参与合作',period='2027-01-01—2028-12-31（2年）',materials='申请书经单位同意签字盖章后电子发送stu_keylab.sist@shanghaitech.edu.cn；正文写“2026年10月8日前”，当日受理边界须确认；获批后1个月内任务书签章纸质4份',missing='今日是否仍受理；固定合作者；资助金额、经费外拨与最终考核/IP',attachment_status='申请书DOCX已读取')
patch('M068',year='2026',date='2026-10-08',amount='一般2万元；重点4万元',qualification='高级职称或相关学科博士学位（正文为“高级”，不擅自改成仅正高）',collaboration='成果作者必须至少1名固定研究人员；申请正文未写必须联合申报',funds='报销经办公室审核、主任和负责人签字；明确实验室报销流程，外拨未明示',period='2026-09-01—2028-08-31（2年）',outputs='一般≥1篇SCI中科院大类二区/CCF B；重点≥1篇SCI一区/CCF A；本人第一或通讯，实验室第一完成单位，至少1名固定人员作者，并标基金447-110103',materials='电子申请书hhy980344@163.com +纸质2份；韩慧妍13703516841，太原学院路3号软件实验大楼508；截止10-08',missing='今日受理/邮寄边界；固定作者合作；申请附件需验证码；产权与外拨',attachment_status='附件下载返回验证码网页，未读附件')
patch('M106',year='2026',date='2026-10-08',amount='2—4万元/项，拟5—8项',qualification='国内科研人员，须中级及以上；副高及以上或有博士的中级直接申报；其他中级须2名高级职称人员推荐',collaboration='与固定工作人员联合申请优先（不是强制）；成果至少署1名固定研究人员',funds='经费仅限中北大学财务结算，不外拨；差旅、材料、服务器租赁、版面、专利、试验等',period='2026-10—2028-10（2年）',outputs='SCI二区及以上1篇或三区2篇；成果同时署负责人单位和实验室，至少1名实验室固定作者，并标资助编号；未明示实验室必须第一单位',materials='申请书单位同意签字盖章，电子1份+纸质3份；guhao@nuc.edu.cn；顾灏18435119916；太原学院路3号；10-08前',missing='今日是否还收；个人职称/推荐信；固定作者合作；知识产权归属')
patch('M161',year='2026',date='2026-11-15',amount='一般2万元；重点3万元',qualification='原则上博士；无高级职称且无博士须1名高级同行推荐；校外负责人优先',collaboration='原则上本实验室固定人员为项目组成员，并参与论文署名',period='2027-01-01—2028-12-31',outputs='≥2篇ESI工程学领域论文，以武汉科技大学给定目录为准；实验室列第一或第二单位，并标基金编号；原则上至少1名固定作者',materials='签字盖章页扫描合入PDF申请书发pozhang@wust.edu.cn，无纸化申报；获批签任务书。张老师15623558895；正文前段“一式两份”与后段无纸化不同，以专门材料要求为准',missing='经费是否外拨、产权；固定合作者；ESI指定目录；任务书')
patch('M029',year='2027',date='2026-11-30',amount='公告未公布资助强度，需咨询',qualification='在职科研人员，博士或副高及以上；否则需2名副高及以上同行推荐；实验室固定人员不能申请',period='2年',materials='按2027附件模板填写申请书，单位盖章，申请表发imet@hust.edu.cn；11-30前；周佳卉/吴昊027-87559416。公告未明示申请纸质份数，不推测',missing='资助金额；完整经费/IP/成果条款；制造装备具体合作方向及是否另收纸质',attachment_status='申请书DOCX已全文读取')
patch('M041',year='2026',date='2026-10-31',amount='5万元/项',qualification='博士学历或副高及以上；年龄不超过40周岁；校外优先；每人1项、每单位最多2项；成员不能同时参与2项以上',collaboration='资助后设实验室内部项目联系人；正文未规定申报前必须固定合作者',funds='不外拨，由中国科学技术大学按财务规定报销',period='1—2年',ip='知识产权由实验室与申请人所在单位共同拥有',materials='签字盖章申请书纸质4份及电子版niant209@ustc.edu.cn；年度指南要求按附件格式',missing='年龄和单位推荐/限项；脑启发选题可行性；申请书DOC解析失败；最终成果数量',attachment_status='任务书DOC已读取；申请书DOC未成功提取文字')
patch('M077',year='2026',date='2026-11-10',amount='0.5万元/项',qualification='副高及以上；或中级职称并由高级专家推荐',period='2年',outputs='至少3篇规定论文（SCI或CCF推荐国际会议/指定中文刊）；实验室作为第一作者单位，标资助编号',ip='成果/知识产权与实验室共享',missing='个人资格；大模型选题与3篇成果负担；申请DOC未解析；经费外拨',attachment_status='申请DOC已下载但未完成全文提取')
patch('M031',year='2025',date='2025-08-10',amount='5—10万元/项',qualification='沈阳自动化所以外科研人员；博士或中级及以上；鼓励一般≤40岁的青年；在研未结题不能重复',collaboration='须联合实验室固定研究人员',period='2025-09-01—2027-08-31',outputs='合作发表1—2篇SCI论文；论文第一作者或通讯作者单位标实验室（不限制单位顺序）；共享相关程序接口/数据集，标基金编号',materials='电子申请书签章扫描+≤8分钟PPT录音汇报等至zhangchan@sia.cn，纸质1份；沈阳市南塔街114号',missing='2026/下一年度新指南；本人资格和固定合作者；产权/外拨')
patch('M007',year='2026',date='2026-09-30',amount='一般5万元/1年；重点10万元/2年',qualification='实验室以外，博士或副高及以上；同年1项、在研最多1项',collaboration='≥1名固定人员；每位固定人员同年仅参与1项外部合作课题',period='一般1年；重点2年',outputs='至少1篇合作SCI，按规范署名/标基金；至少1次来室访问和学术报告',materials='签字盖章申请书纸质2份由合作者提交；电子版office@lnm.imech.ac.cn；9-30前',missing='下一年度方向；软组织模型能否进入一般交叉范围；经费外拨/IP',attachment_status='2026指南PDF和申请书DOCX已全文读取')
patch('M075',year='2026',date='2026-02-10',amount='2—3万元/项，每方向拟2—3项，另提供算力',qualification='欢迎国内外学者，在四类康养指南范围内自拟；正文未规定统一职称/年龄硬门槛',collaboration='建议与固定人员合作（不是强制）',period='2026-03-01—2027-06-30',funds='按苏州城市学院报销规则；外拨未明示',materials='签章申请扫描件邮件wx31@szcu.edu.cn；获批7日内签章合同纸质3份；王老师0512-66556473',missing='新年度指南；产权和具体结题指标；个人/选题条件')
patch('M156',year='2024',date='2024-10-30',amount='平均2万元/项，拟5项（校内≤2项）',qualification='博士或副教授/副研究员及以上或相应水平；仅校内申请人要求35岁以下',collaboration='公告未明示必须固定合作者',period='1—2年',funds='江南大学运行专项，按校财务制度专款专用，外拨未明示',ip='工程中心与研究者所在单位共享',outputs='理工论文路线1年：中心前2单位，≥1篇SCI三区以上或2篇中文EI或1篇CCF/CAAI C以上会议；2年专利路线：中心前2申请人授权中国发明/PCT≥1项；2年标准路线：中心前7起草单位标准≥1项。具体路线适用须任务书确认',materials='签章申请纸质2份+电子qianpjiang@jiangnan.edu.cn；无锡蠡湖大道1800号人工智能与计算机学院',missing='新年度申报窗口；成果路线与经费外拨')
patch('M084',year='2025',date='2025-11-03',amount='校外开放基金1万元/项，拟5项；校内创新基金不同计划',period='2026-01起，2年',funds='可外拨，立项50%+中期通过50%；剩余经费可于结题后1年内继续用于原课题',missing='新年度指南；个人资格与成果数量/署名适用规则',attachment_status='开放基金管理办法DOCX已全文读取；申请/任务DOC未解析')
patch('M115',year='2025',date='2025-09-20',amount='一般5—10万元（1年）；重点20—30万元（2年）',qualification='本校/本实验室固定人员以外；博士或高级职称；中级需2名高级推荐；退休、兼职、研究生、博士后不能作负责人',period='一般1年；重点2年',materials='签章电子申请pingama@yeah.net；截止2025-09-20 17:00',missing='新年度指南；固定合作/产权/外拨与成果要求')
patch('M116',year='2025',date='2025-04-25')
patch('M117',year='2025',date='2025-03-15')
patch('M028',year='2026',date='2025-12-20')
patch('M032',year='2026',date='2026-05-06')
patch('M044',year='2026',date='2026-10-10',missing='矿山场景及申请条件；不优先医学机器人申报')
patch('M151',year='2026',date='2026-04-20')
patch('M181',year='2017',date='2017-12-05',amount='2017历史：重点平均4万元、一般平均2万元',qualification='非南京邮电大学在职科研人员，博士；在读博士生/在站博士后视为本校；同年1项含在研',period='2018-01-01—2019-12-31',funds='2017机制：外拨申请人单位，合同50%、年度通过30%、结题余额；境外申请需本室联系人',ip='实验室与承担人所在单位共有',outputs='2017重点≥3篇CCF C类且其中≥1篇B类以上；一般≥2篇CCF C类以上；第一/通讯作者第一或第二单位署实验室并标资助',missing='新年度指南，不能把2017机制标为2026在受理')
P['M166']['date']=None;P['M166']['date_verified']=False;P['M166']['missing']='原4-3是答辩材料截止，非首次申报截止；已进入2026-4-7答辩，首次正式指南与下一年度待核';P['M166']['changes'].append('原2026-04-03属于答辩材料截止，清除为申报截止的错位记录')
patch('M155',year='2026',date='2026-05-17',amount='上海交大/深圳大学分室≤10万元，2年；中兴一般10—20万元，重点≥50万元，0.5—2年',qualification='上海交大/深圳分室及中兴一般：博士或中级以上；中兴重点副高及以上可适当放宽；在研≤1项',materials='电子hi-rfskl@szu.edu.cn；签章纸质4份；上海交大分室另列商老师shangmengnan@sjtu.edu.cn，021-34204301',period='高校分室2年；中兴0.5—2年',outputs='公开成果署相应分室或致谢实验室，标基金编号；1年中期、2年结题',missing='分室受理归属及IP/经费外拨；和M178同联合指南，勿重复计计划')
P['M155']['plan_group']=P['M178']['plan_group']='G-RF-2026'
P['M124']['plan_group']=P['M125']['plan_group']='G-XHU-AUTO-2026'
for id in ['M124','M125']:P[id]['raw_note']+='；保留两个平台条目，按同一联合公告组计数，不认定两个独立资金池'
P['M178']['raw_note']+='；与M155为同一2026联合指南不同高校分室，归G-RF-2026'
P['M115']['org']=P['M101']['org']='同济大学（与北京理工大学共建）'
for id in ['M115','M101']:P[id]['region'],P[id]['region_rank'],P[id]['city']=geography('同济大学');P[id]['raw_note']+='；同一联合实验室统一上海地域，分别保留2025和2026年度，不跨地域重复展示'
patch('M148',amount='最匹配人体背部接触体压方向10万元/2年；其他一般≤10万、重点≤15万',qualification='博士或高级职称；国内固定受聘于非实验室承担单位且聘期覆盖项目；45岁以下优先；同实验室同年1项',period='人体背部接触体压模型2年',outputs='目标方向：体压模型误差<15%；中文核心或SCI≥1篇、受理发明专利≥1项、研究报告1部。成果第一完成单位原则上实验室并标资助',ip='实验室与负责人所在单位共有',materials='签章纸质申请2份+Word和签章扫描电子版；人因联系人赵朝义/丁文兴，zhaochy@cnis.ac.cn / dingwx@cnis.ac.cn，010-58811661/58811693',missing='新年度窗口；人因合作者、外拨与实验验证条件')
patch('F001',year='2026',date='2026-11-06',amount='每课题总支持不低于10万元（研究经费+软硬件），研究经费≥总经费50%；不需额外购配套软硬件',period='2027-01-01—2027-12-31',ip='资助方与课题承担单位共同所有',materials='签章PDF上传http://cxjj.cutech.edu.cn；纸质1份寄北京中关村大街35号1005室教育部高等学校科学研究发展中心新技术应用研究处',missing='迈瑞附件具体超声/医工选题、个人资格及临床合作门槛；其他资助类型，单列备选')

home_ids=set('M078 M056 M066 M035 M068 M106 M160 M017 M029 M161 M142'.split())
for p in projects:
 if p['id']=='M056':p['status']='滚动支持·当期与合作资格待确认';p['status_rank']=1
 elif p['id'] in ['M138']:p['status']='校内人员限定·非当前外部可申请';p['status_rank']=5
 elif p['date']:
  if p['date']<TODAY:p['status']='已截止·留作下一年度储备'+('（旧日期未复核）' if not p['date_verified'] else '');p['status_rank']=4
  elif p['date']==TODAY:p['status']='今日截止·受理与资格待确认';p['status_rank']=0
  elif p['date_verified']:p['status']='公告窗口未过·个人资格待核';p['status_rank']=1
  else:p['status']='日期待复核·未确认受理';p['status_rank']=2
 else:p['status']='年度/日期待核·未确认受理';p['status_rank']=3
 if p['id']=='M049':p['status']='省内单位限定·南京依托暂不适用';p['status_rank']=5
 if p['id']=='M166':p['status']='已进入评审·原日期为答辩材料截止';p['status_rank']=4
 if p['id'] in ['M112','M187','M135']:p['status']='仅平台/历史机制·年度申报待核';p['status_rank']=3
 p['homepage']=p['id'] in home_ids and p['grade'] in 'AB' and p['status_rank']<3
 p['relationship']='当前单位' if p['org']=='南京信息工程大学' else '熟悉合作网络' if p['org'] in familiar else ''
 if p['grade']=='C':p['home_reason']='C类，仅保留总览/详情'
 elif p['homepage']:p['home_reason']='首页候选；不等于确认本人可申请'
 elif p['status_rank']>=4:p['home_reason']='已截止或资格限制，保留年度储备'
 elif p['id'].startswith('F'):p['home_reason']='其他资助，保留总览单列备选'
 elif p['id']=='M077':p['home_reason']='0.5万元/≥3篇论文，当前申请价值低'
 else:p['home_reason']='未确认年度窗口，或需较大场景/方法迁移，暂不占首页'
 p['check_date']=TODAY
 p['source_status']=p['source_status']+'；核实字段：'+('、'.join(p['field_verified']) if p['field_verified'] else '未做全部字段确认，旧表值保留为参考')
 # Fix mixed legacy qualification strings, preserving them in raw qualification and original sheets.
 if not ('qualification' in p['field_verified']) and re.search('万元|万/|第一作者|署名|纸质|邮箱|官网显示|具体申报日期|经费/',p['qualification']):
  p['raw_qualification']=p['qualification'];p['qualification']='未核实具体资格；原始混合摘要在本项目“原始资格/来源摘要”字段保留'
 p['basis']='面上申请书：研究内容/方案PDF第7—23页；研究基础第24—30页。四主线为软组织接触建模、图像反馈力优化、多模态扫描规划、学习最优阻抗/鲁棒柔顺控制。'
 p['sort_key']=(p['region_rank'],p['region'],familiar.get(p['org'],9),p['grade'],p['status_rank'],p['date'] or '9999',p['org'],p['id'])
projects.sort(key=lambda p:p['sort_key'])
home=sorted([p for p in projects if p['homepage']],key=lambda p:(p['region_rank'],p['region'],familiar.get(p['org'],9),p['grade'],p['status_rank'],p['date'] or '9999',p['id']))

# Preserve every coverage entry, consolidate only proven aliases in display; not count keywords as a full platform audit.
searches=[]
for f in ROOT.glob('institution_searches_*.json'):searches+=json.load(open(f,encoding='utf8'))
S={x['index']:x for x in searches}
targeted=[]
for f in ROOT.glob('targeted_*.json'):targeted+=json.load(open(f,encoding='utf8'))
T={item['index']:batch['result'] for batch in targeted for item in batch['items']}
coverage=[];groups={}
for index,x in enumerate(inst):groups.setdefault(canonical(x['name']),[]).append((index,x))
core_overrides={
 '南京信息工程大学':('部分已查','已补查大数据分析、自动化/医工、复杂环境保障及既有风险/水文项目；未找到可确认当前申请的机器人/超声开放指南','https://df.nuist.edu.cn/kypt/list.htm','江苏省大数据分析平台；复杂环境保障2026历史指南；气象/材料开放方向不能升级为机器人A类'),
 '华南理工大学':('仅平台/历史机制','找到大数据与智能机器人、粤港澳机器人联合平台及导师合作基础；本轮未取得其当前开放基金指南','https://www2.scut.edu.cn/sse/2018/0615/c16788a270751/page.psp','大数据与智能机器人/自主系统控制平台；年度开放与外校合作申请规则须向平台确认'),
 '澳门大学':('部分已查','核查机器人实验室及与港理工机器人联合平台；既有中药/芯片/智慧城市基金不直接支持超声控制，未发现当前机器人开放指南','https://www.fst.um.edu.mo/research/laboratories/robotics-laboratory/','机器人平台与合作联系；年度资助机制、固定人员及是否对外受理'),
 '香港理工大学':('部分已查','已查超精密加工历史开放基金和机器人合作平台；机器人研究/联合实验室新闻不是开放基金公告','https://www.gov.mo/zh-hans/news/889235/','超精密加工下一年度；医疗/软体机器人平台外部基金、个人资格与资金流向'),
 '中国科学院自动化研究所':('已完成（本轮既定平台）','2026多模态AI正式指南已全文核实，含医疗机器人，5—10万元，5-29已截止；另一认知决策批次无人机反制须迁移场景','https://www.ia.cas.cn/qtgn/tzgg/202605/t20260515_8202627.html','后续年度新指南、固定人员联合与来室每年原则上≥2个月；不声称全所所有平台穷尽'),
 '西北工业大学':('部分已查','已补查机电科研平台/人机共融制造、无人系统、凝固与大数据历史条目；本轮未取得当前医工/柔顺机器人开放指南','https://jidian.nwpu.edu.cn/info/1073/4704.htm','人机共融/康复机器人相关平台当期开放指南；无人系统与控制平台具体名单'),
 '重庆大学':('部分已查','已查高端传动、生物感知/CPS、智能控制及土木等；CPS仅机制线索，现有明确2026批次均截止；不把科研团队当申报公告','https://accu.cqu.edu.cn/kxyj/yjs/gyznjsyxtyjs.htm','复杂系统安全与控制教育部平台及CPS年度指南；既有项目附件/下一年度窗口')
}
for name,items in groups.items():
 index,x=items[0];region,rank,city=geography(name,x['region']);related=[p for p in projects if canonical(p['org'])==name or (name=='同济大学' and '同济大学' in p['org'])]
 result=str(S.get(index,{}).get('result',''))+'\n'+str(T.get(index,''))
 official_domain=domains[index] if index<len(domains) else ''
 urls=re.findall(r'https?://[^\s()<>，；、。]+',result)
 official=[]
 for u in urls:
  host=urllib.parse.urlparse(u).netloc
  if official_domain and (host==official_domain or host.endswith('.'+official_domain)) and u not in official:official.append(u.rstrip('.,;'))
 source=official[0] if official else (related[0]['url'] if related else '')
 if name in core_overrides:
  status,outcome,source,pending=core_overrides[name]
 elif related:
  verified=[p for p in related if p['date_verified']]
  status='部分已查'
  outcome=f'已补查机构定向网页；保留{len(related)}条既有项目/机制记录，{len(verified)}条截止日期有本轮官网证据。'
  pending='未成功附件/字段及未建档相关平台；下一年度窗口。检索完成仅指本轮定向任务，不代表机构全部实验室查全。'
 elif official:
  status='仅平台/历史机制'
  outcome='已完成本轮机构定向补查，取得官网平台/历史或其他领域公告线索；未取得已核实的当前机器人/医工开放基金。'
  pending='逐平台定位具体年度指南、对外资格、金额、截止和附件；此处线索不能当作当前可申请项目。'
 else:
  status='待查（无可核实指南）'
  outcome='本轮机构名与官网域名定向查询已执行；未取得可核实相关指南。未检出不能等于无开放基金。'
  pending='平台清单/更名、非索引网页和负责人咨询；必要时继续逐平台核查。'
 if name in ['中国科学院无锡相关物联网研究机构','中国科学院上海生命科学有关研究机构','江苏省人民医院等医学科研平台','香港科技园的公开研究资助平台','香港科技大学（广州）关联深圳协作平台']:
  status='待查（机构/平台边界待定）';pending='原条目是机构集合或协作平台泛称，具体主体未明确；需要先定平台范围。定向补查已执行，不能标整组查全。'
 coverage.append(dict(name=name,aliases='；'.join(a['name'] for _,a in items),original_count=len(items),region=region,rank=rank,status=status,outcome=outcome,ids='、'.join(p['id'] for p in related) or '未建确认项目',pending=pending,url=source,urls=official[:5],date=TODAY,old_evidence='；'.join(str(a['old'][4] or '') for _,a in items),old_pending='；'.join(str(a['old'][5] or '') for _,a in items),relationship=x['region'] if name in familiar else '',queries='\n'.join(str(S.get(i,{}).get('q','')) for i,_ in items),scope='本轮名单内机器人/控制/医工方向定向补查；逐平台未穷尽'))
coverage.sort(key=lambda x:(x['rank'],x['region'],familiar.get(x['name'],9),x['name']))

data={'date':TODAY,'projects':projects,'home':home,'coverage':coverage,'raw':raw,'counts':dict(collections.Counter(p['grade'] for p in projects)),'coverage_counts':dict(collections.Counter(p['status'] for p in coverage)),'original_count':len(rows),'original_coverage_count':len(inst),'unique_coverage_count':len(coverage)}
(ROOT/'normalized.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('COUNTS',data['counts'],'HOME',[p['id'] for p in home],'COVERAGE',len(inst),len(coverage),data['coverage_counts'])
print('ALL ORIGINAL IDS KEPT',set(P)=={r[0] for r in rows})
