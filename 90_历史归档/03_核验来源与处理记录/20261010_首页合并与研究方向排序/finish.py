from pathlib import Path
from openpyxl import load_workbook
import json,hashlib
H=Path(__file__).parent;R=H.parents[2];d=json.loads((H/'plan.json').read_text(encoding='utf8'));v=json.loads((H/'validation.json').read_text(encoding='utf8'));new=d['output_name'];old=Path(d['source']).name
assert hashlib.sha256((R/new).read_bytes()).hexdigest()==v['sha256'];assert len([p for p in R.glob('*.xlsx') if not p.name.startswith('~')])==1;assert not list(H.glob('*.xlsx'))
for rel in ['AGENTS.md','README.md','01_项目说明与背景/项目说明.md']:
 p=R/rel;s=p.read_text(encoding='utf8').replace(old,new)
 if rel=='AGENTS.md':
  s=s.replace('主台账保留五张表：申报总览、项目完整详情、历史项目、其他资助、机构检索覆盖。','主台账保留四张表：申报总览、项目完整详情、历史项目、机构检索覆盖。原其他资助两项并入首页；不再单设其他资助页。')
  s=s.replace('历史项目及其他基金放独立工作表','历史项目放独立工作表；相关且受理窗口成立的其他课题按用户要求并入首页，合作参与渠道须明确牵头及资金口径')
  s=s.replace('首页按南京及周边、澳门、香港、珠三角、北京、西安、重庆、其他地区排序，同组截止日期从近到远，不以金额或评分排序。','首页按用户最新要求，对照面上申请书的研究内容与研究基础，实际任务联系优先排序；联系相当时再考虑熟悉地区与截止日期。不以金额、能力判断或数值匹配分数排序。')
 if rel=='README.md':
  s=s.replace('当前397条详情：正式受理19条、历史296条、其他当前资助2条；另80条窗口、任务或申报入口尚不成立的记录仅保留在完整详情，不另设待核页。','当前397条详情：首页21条（原开放课题19条及原其他资助2条），历史296条；另80条窗口、任务或申报入口尚不成立的记录仅保留在完整详情，不另设待核页。')
  s=s.replace('其他当前资助查看“04其他资助”：区分高校团队申报与省际合作参与。','原04两项已并入“01申报总览”，省际合作参与明确标记；不再单设其他资助页。')
  s=s.replace('主工作簿保留5张表','主工作簿保留4张表')
 if rel.endswith('项目说明.md'):
  s=s.replace('当前工作簿的五张表','当前工作簿的四张表').replace('| 19条 |','| 21条，含高校专项与明确标记的省际合作参与 |')
  s=s.replace('| 04其他资助 | 其他当前资助：高校团队申报/省际合作参与 | 2条 |\n','').replace('| 05机构检索覆盖 |','| 04机构检索覆盖 |')
  s=s.replace('首页先按熟悉地区分组，同组截止日期从近到远。','首页现按用户最新要求，对照申请书研究内容与研究基础，实际任务联系优先排序；熟悉地区和截止仅作联系相当时的参考。')
 p.write_text(s,encoding='utf8')
priority='''

## 2026-10-10用户最新：首页合并与研究任务排序（优先适用）

原04两项并入首页，共21条；取消独立其他资助页。F022为青海牵头的省际合作参与渠道，不能写成个人可独立申报或把总额当个人额度。首页仍六列。02保留全部既有397条及原字段，用户明确“新补的2项不需要在02中补充完整信息”，不得为此新增补查、扩写条款。

用户授权对照面上申请书的研究内容和研究基础调整任务先后：医疗机器人力觉及人机交互、机器人学习操控、多模态感知与系统建模反馈控制等联系较直接的靠前；须服务特定行业的应用边界照实保留。研究任务联系优先，联系相当时再考虑熟悉地区与截止日期。申请书仍不作为能力边界或剔除范围，不制作数值匹配评分或获批概率。此条替代此前首页严格地域优先、其他资助独立成页的约定；历史记录保留原日期含义。
'''
for rel in ['AGENTS.md','后续补充检索规则.md']:
 p=R/rel;p.write_text(p.read_text(encoding='utf8')+priority,encoding='utf8')
p=R/'README.md';p.write_text(p.read_text(encoding='utf8')+'\n2026-10-10按用户最新要求：首页由19条合并为21条，原04两项移入，空页取消；对照申请书按实际任务联系重排，02全部397条记录及字段不扩写。首页前列为医疗机器人力触觉/人机协同、机器人学习控制、多模态建模反馈控制等。旧版归档至`90_历史归档/02_旧版与输出记录/20261010_首页合并排序前`。[实际顺序与此前20项移出明细](02_检索与核验记录/首页合并与研究方向排序记录_20261010.md)。\n',encoding='utf8')
v.update({'output':str(R/new),'delivery':'completed','temporary_workbooks_removed':True});(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print('Latest link, four-sheet structure and research-task sorting rules updated.')
