from pathlib import Path
import json,hashlib
H=Path(__file__).parent;R=H.parents[2];old='全国机器人开放课题_个人申报台账_当前申报清理版_20261010.xlsx';new='全国机器人开放课题_个人申报台账_兼容性修正版_20261010.xlsx'
v=json.loads((H/'validation.json').read_text(encoding='utf8'));assert hashlib.sha256((R/new).read_bytes()).hexdigest()==v['sha256'];assert len([p for p in R.glob('*.xlsx') if not p.name.startswith('~')])==1
for rel in ['README.md','AGENTS.md','01_项目说明与背景/项目说明.md']:
 p=R/rel;p.write_text(p.read_text(encoding='utf8').replace(old,new),encoding='utf8')
note='''# Excel兼容性与内容恢复检查（2026-10-10）

用户截图显示Excel内容修复提示。原生Excel修复日志定位04其他资助的表定义；G1为“申报主体及条件”，内部表字段仍为“具体待核事项”。此前以DisplayAlerts=false读取成功作为交付验证不充分，可能掩盖自动修复行为。

从Git提交3b01795取回完整交付基准（SHA256 e48448f9f7d3948757ffc10cb527292c9b315f0b3af726354b91846a187e89c2）。与用户点击“是”并保存后的文件对比，没有实质项目条款或超链接丢失，只有AA30说明文字的开头换行变化；修正版仍从完整原始基准恢复该说明。全部397条详情、19条首页、296条历史及2条其他当前资助保留。

修复仅涉及04表字段名一致性，以及297个日期单元格从ISO日期表示改为Excel标准数值日期（保持yyyy-mm-dd显示）。条目、日期含义、金额、条款、来源、字体、列宽和链接不变。当前两张资助表及历史页按熟悉地区组、组内日期排序通过；首页当前分布南京及周边4、北京2、重庆1、其他12，无澳门/香港/珠三角/西安当期条目。

最终使用本机Microsoft Excel、DisplayAlerts=true正常打开，不出现修复提示。原生读取35496个单元格、1248个超链接逐一对比通过，5个筛选表保留；日期实际为数值类型。变更视图渲染通过。旧版移入90_历史归档/02_旧版与输出记录/20261010_兼容性修正前，根目录只保留修正版，中间工作簿清除。

本次只检查既有文件内容一致性、恢复与兼容性，不开展新检索，不声称所有官方条款重新逐公告核验。
'''
(R/'02_检索与核验记录/Excel兼容性与内容恢复检查_20261010.md').write_text(note,encoding='utf8')
p=R/'README.md';p.write_text(p.read_text(encoding='utf8')+'\n2026-10-10兼容性修复：以Git完整397条版本恢复内容，修正筛选表字段及297个日期的存储格式。原生Excel开启提醒后正常打开，35496个单元格和1248个超链接对比通过，条目和排序保留；中间工作簿清除。[检查记录](02_检索与核验记录/Excel兼容性与内容恢复检查_20261010.md)。\n',encoding='utf8')
p=R/'AGENTS.md';p.write_text(p.read_text(encoding='utf8')+'\n交付兼容性检查：日期必须以Excel数值日期保存，保持既定显示格式；表头单元格与筛选表内部字段名须一致。最终使用本机Excel开启提醒正常打开并确认不出现修复提示；不能仅凭库读取成功或关闭提醒后的COM打开成功认定文件正常。恢复/保存后的单元格和超链接须对照完整输入基准。\n',encoding='utf8')
v.update({'output':str(R/new),'source':'Git 3b01795:'+old,'delivery':'completed','temporary_workbooks_removed':True});(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print('Delivery, documentation and native validation recorded.')
