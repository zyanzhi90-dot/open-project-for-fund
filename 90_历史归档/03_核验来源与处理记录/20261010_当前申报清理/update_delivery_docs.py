from pathlib import Path
import json,hashlib
H=Path(__file__).parent;R=H.parents[2];d=json.loads((H/'plan.json').read_text(encoding='utf8'));new=d['output_name'];old=Path(d['source']).name
assert (R/new).exists()
assert hashlib.sha256((R/new).read_bytes()).hexdigest()==json.loads((H/'validation.json').read_text(encoding='utf8'))['sha256']
assert len([p for p in R.glob('*.xlsx') if not p.name.startswith('~')])==1
for rel in ['AGENTS.md','README.md','01_项目说明与背景/项目说明.md']:
 p=R/rel;s=p.read_text(encoding='utf8').replace(old,new)
 if rel=='README.md':
  s=s.replace('当前397条详情：正式受理19条、历史285条、其他资助22条；另71条窗口或任务范围未明确的线索仅保留在完整详情，不另设待核页。','当前397条详情：正式受理19条、历史296条、其他当前资助2条；另80条窗口、任务或申报入口尚不成立的记录仅保留在完整详情，不另设待核页。')
  s=s.replace('需要以后参考、核实线索或查看其他资助时，使用历史或其他资助页；窗口未知、任务范围不明的线索留在完整详情。','其他当前资助查看“04其他资助”：区分高校团队申报与省际合作参与。过期项目只看历史页；窗口未知、任务范围不明或本单位申报入口未成立的线索留在完整详情。')
 if rel.endswith('项目说明.md'):
  s=s.replace('含71条未列分类页的线索','含80条未列分类页的记录').replace('| 285条 |','| 296条 |').replace('| 04其他资助 | 其他类型科研资助 | 22条 |','| 04其他资助 | 其他当前资助：高校团队申报/省际合作参与 | 2条 |')
 p.write_text(s,encoding='utf8')
rule='\n\n2026-10-10当前申报清理要求：01及04不得混入已截止或尚未开放项目。04只展示当期窗口成立、任务相关且有高校申报或明确省外合作参与入口的其他资助；窗口、任务或省外参与入口未成立的记录仅留详情。合作参与须显著注明实际牵头单位与资金分配条件；联合项目总额和设备/平台折价不得冒充本人现金额度。不按金额大小设一刀切阈值，普通资格与结题条件不清楚的如实保留。\n'
for rel in ['AGENTS.md','后续补充检索规则.md']:
 p=R/rel;p.write_text(p.read_text(encoding='utf8')+rule,encoding='utf8')
p=R/'README.md';p.write_text(p.read_text(encoding='utf8')+'\n2026-10-10当前申报清理：04移出11条已截止与9条当期窗口、任务或本单位申报入口未成立的记录；保留2条当前其他资助，明确现金/平台支持及省际合作资金口径。01仍19条。原条款和397条详情保留，旧交付版归档至`90_历史归档/02_旧版与输出记录/20261010_当前申报清理前`。[处理记录](02_检索与核验记录/当前申报清理记录_20261010.md)。本轮未进行新检索。\n',encoding='utf8')
v=json.loads((H/'validation.json').read_text(encoding='utf8'));v['delivery']='completed';v['root_output']=str(R/new);v['output']=str(R/new);v['duplicate_intermediate_workbooks_removed']=True
(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print('Latest link, rules and single-root-workbook delivery verified.')
