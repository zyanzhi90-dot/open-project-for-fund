"""Install validated delivery and archive prior file. No workbook authoring."""
import pathlib,json,hashlib,shutil,re
H=pathlib.Path(__file__).parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
D=json.loads((H/'prepared_strict.json').read_text(encoding='utf8'))
v=json.loads((H/'validation_strict.json').read_text(encoding='utf8'))
assert v['visual_review']=='passed'
new=pathlib.Path(v['output']);old=pathlib.Path(D['current_input'])
dest=ROOT/new.name;folder=ROOT/'90_历史归档/02_旧版与输出记录/20261008_严格重筛前交付版';archived=folder/old.name
assert sha(new)==v['sha256'] and sha(old)==D['current_input_hash']
assert not dest.exists() or sha(dest)==sha(new)
assert not archived.exists() or sha(archived)==D['current_input_hash']
assert old.resolve().parent==ROOT.resolve() and folder.resolve().is_relative_to(ROOT.resolve())
folder.mkdir(parents=True,exist_ok=True)
if not dest.exists():shutil.copy2(new,dest)
assert sha(dest)==sha(new)
if archived.exists():old.unlink()
else:shutil.move(str(old),str(archived))
assert sha(archived)==D['current_input_hash']
assert len(list(ROOT.glob('*.xlsx')))==1
for name in ['AGENTS.md','README.md','项目说明.md']:
 p=ROOT/name;t=p.read_text(encoding='utf-8-sig').replace(old.name,new.name)
 if name=='README.md':
  start=t.index('正式项目要求见');end=t.index('## 自动上传')
  t=t[:start]+'''正式项目要求见[后续补充检索规则](后续补充检索规则.md)。按实际机器人、具身智能、人机交互及相关智能装备任务筛选，不以通用“智能、优化、控制”关键词保留，不作能力判断或推荐。首页严格六列：申报状态、截止日期、依托单位·实验室、公告研究方向、资助金额、公告。

2026年10月8日对166个独立条目逐项重筛：93条有相关任务证据、44条方向或指南待核、29条新增剔除。现有137个独立详情条目，覆盖138条原记录，累计剔除61条，199条原记录全部保留筛选去向。首页12条当前窗口内的正式公告；历史75条、待核46条、其他资助4条分别另页，互不重复。待核页含5条今日截止且时点未明确的项目。受理中不代表个人可申请。

复用既有资料，对每条记录的公告、截止、资格、合作、经费、周期、成果、权属和提交要求逐字段复读，修正51项条款。部分信息仍未核清；已取得资料未载、附件未取得、个人条件待确认分别记录。重庆交通大学指南和管理办法附件受验证码限制；两项NSFC通告的完整指南需登录GRANTS。缺口及联系人见详情与待核页，未推测补填。

筛选决定、逐字段核验、来源和验证记录位于 `90_历史归档/03_核验来源与处理记录/20261008_严格重筛`。8张可见工作表生成17张检查图，已逐张检查；199条覆盖、日期、排序、链接、筛选及冻结检查通过。机构覆盖表沿用已有证据，仍为部分检索，不宣称全国检索完成。

根目录只保留此最新Excel。上一最终核验版移至 `90_历史归档/02_旧版与输出记录/20261008_严格重筛前交付版`，原筛选核验版及六列展示版仍在此前归档目录；各原文件内容未改。无工作簿内容变化不生成新版。

'''+t[end:]
 if name=='项目说明.md':
  t=re.sub(r'：保留167条原记录、合并为166个独立条目，剔除32条；首页六列。', '：本轮重筛后137个独立详情条目；首页12条正式受理公告、历史75条、待核46条、其他资助4条；累计剔除61条原记录。',t)
  t=t.replace('用于了解机器人、人机交互、感知、建模、学习、优化和控制研究能力','仅用于了解研究方向、技术积累和科研基础，不用于限定能力或可申报范围')
  t=t.replace('20261008_能力筛选核验','20261008_严格重筛')
 p.write_text(t,encoding='utf8')
p=ROOT/'后续补充检索规则.md';t=p.read_text(encoding='utf-8-sig')
t=t.replace('本次仅明确规则，不代表已完成全国检索或已改造当前工作簿。','已按本轮要求重筛现有166条并调整工作簿，未扩展地域检索；全国机构覆盖尚未验收。')
t=t.replace('展示与机器人、人机交互、感知、建模、学习、优化、控制、工业装备及自动化有关的方向','只保留与机器人、具身智能、人机交互、机器人感知、学习、规划、控制及相关智能装备有实际联系的公告任务')
t=t.replace('保留明确相关的建模、感知、算法、测控或装备任务','仅保留有具体证据联系机器人或相关智能装备的建模、感知、算法、测控或装备任务；通用行业建模、学习、优化和控制不能据关键词保留')
t=t.replace('本次明确要求不自动启动新检索；后续执行全国补充检索时按此范围推进。','本轮只重筛及核验已有条目，不扩展地域；后续获授权补充检索时按此范围推进。')
t=t.replace('首页严格六列：申报状态、截止日期、依托单位·实验室、研究主题、资助金额、公告。“研究主题”客观概括公告任务，替代早期“匹配方向”的表述。研究主题和金额简短','首页严格六列：申报状态、截止日期、依托单位·实验室、公告研究方向、资助金额、公告。“公告研究方向”客观概括实际任务。方向和金额简短')
t=t.replace('同状态组内同机构集中，并呈现截止日期','同状态组内按熟悉地区优先、兼顾截止日期排序')
p.write_text(t,encoding='utf8')
v.update({'delivered_output':str(dest),'prior_delivery_archived':str(archived),'archived_sha256':sha(archived),'root_single_current_xlsx':True})
(H/'validation_strict.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'delivered':str(dest),'archived':str(archived),'sha256':sha(dest)},ensure_ascii=False))
