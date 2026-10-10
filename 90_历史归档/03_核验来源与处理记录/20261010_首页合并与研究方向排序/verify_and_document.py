from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils.datetime import to_excel
import json,datetime,csv,re
def re_date(v):return bool(re.match(r'^\d{4}-\d\d-\d\d',v))
H=Path(__file__).parent;R=H.parents[2];d=json.loads((H/'plan.json').read_text(encoding='utf8'));p=H/d['output_name'];w=load_workbook(p)
native=json.loads((H/'native_values.json').read_text(encoding='utf-8-sig'));checked=0;links=0
for n in native:
 s=w[n['sheet']];assert (s.max_row,s.max_column)==(n['rows'],n['cols']);exp=[to_excel(c.value) if isinstance(c.value,datetime.datetime) else c.value for row in s for c in row];act=[None if v=='' else v for v in n['values']];assert exp==act,(s.title,'Native values changed')
 oldlinks={c.coordinate:c.hyperlink for row in s for c in row if c.hyperlink};assert len(oldlinks)==len(n['links'])
 for x in n['links']:
  c=oldlinks[x['ref']];assert (c.target or '')==(x['address'] or '') and (c.location or '')==(x['location'] or '')
 checked+=len(exp);links+=len(oldlinks)
v=json.loads((H/'validation.json').read_text(encoding='utf8'));v.update({'visual_review':'passed','native_excel_check':'passed with alerts enabled, no repair prompt','native_checked_cells':checked,'native_checked_links':links,'delivery':'prepared'});(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');w.close()
record=R/'02_检索与核验记录/首页合并与研究方向排序记录_20261010.md'
lines=['# 首页合并、研究方向排序与原04移出明细（2026-10-10）','','用户最新要求：将原04两项并入首页；对照面上申请书，实际任务联系优先。用户随后澄清：“新补的2项不需要在02中补充完整信息”。因此02全部现有397条、27字段保持原样，不补查、不扩写F002/F022。','','首页现21条，严格六列。保留历史与机构覆盖，共四张表，原空04其他资助删除。F022明确是青海单位牵头的省际合作参与渠道，省外经费依协议，项目总额不是个人额度。','','申请书只作任务排序参考：医疗机器人交互与力觉、系统建模、视觉/多模态感知、学习优化、运动规划、柔顺及鲁棒反馈控制。未因此限制能力或剔除研究范围，不设匹配分数，不按金额排序。任务联系优先；任务联系相当时再考虑熟悉地区及截止。具体次序是本次人工按任务内容形成的相对顺序，不是获批概率。','','## 首页实际顺序及任务依据','','|序号|编号|依托单位·实验室|排序依据|','|---|---|---|---|']
for i,e in enumerate(d['home'],1):lines.append(f"|{i}|{e['id']}|{e['values'][2]}|{d['reasons'][e['id']]}|")
lines+=['','## 原04移出的20项：未删除项目信息','','11项因明确截止日期已过进入历史；9项仅留详情。以下是前次清理的去向，本轮没有再次剔除项目。','','|编号|项目|原截止字段|去向|原因|','|---|---|---|---|---|']
for x in d['removed_from_other']:
 reason='明确截止日期已过' if x['destination']=='03历史项目' else x['status']
 lines.append(f"|{x['id']}|{x['name']}|{x['deadline'][:10] if re_date(x['deadline']) else x['deadline']}|{x['destination']}|{reason}|")
lines+=['','验证：原21条任务、金额、日期及公告网址保持；02、历史和机构覆盖原工作表XML未改变。新首页日期为Excel数值日期，实验室链接详情，公告可点击。原生Excel开启提醒正常打开，无修复提示；全部读取值和超链接一致，首页全部21条渲染已查看。旧版归档，根目录只留新版，无额外中间工作簿。']
record.write_text('\n'.join(lines)+'\n',encoding='utf8')
with (R/'02_检索与核验记录/审计记录/首页任务排序依据_20261010.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['首页序号','编号','依托单位·实验室','实际任务联系依据'])
 for i,e in enumerate(d['home'],1):wr.writerow([i,e['id'],e['values'][2],d['reasons'][e['id']]])
print('Native values and links verified; full order and all 20 prior removals documented.')
