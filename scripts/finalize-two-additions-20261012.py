"""Finalize verified two-row update; no research or workbook rewriting."""
from pathlib import Path
import csv,json,hashlib,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
old='全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
new='全国机器人开放课题_个人申报台账_检索补充版_20261012.xlsx'
source=root/old;staged=root/'.sync/excel_20261012'/new;target=root/new
record=root/'02_检索与核验记录/第四步交叉补漏_20261011/main006_20261012'
check=json.loads((record/'Excel补入内容校验.json').read_text(encoding='utf-8'))
native=json.loads((record/'Excel原生打开校验.json').read_text(encoding='utf-8-sig'))
assert native['normal_open_without_repair_prompt'] and native['all_original_values_equal']
assert hashlib.sha256(source.read_bytes()).hexdigest()==check['source_sha256']
assert hashlib.sha256(staged.read_bytes()).hexdigest()==check['output_sha256']
assert not target.exists()
archive=root/'90_历史归档/02_旧版与输出记录/20261012_已核两项补入前'
assert archive.resolve().is_relative_to(root.resolve())
archive.mkdir(parents=True,exist_ok=True)
for name in ['README.md','AGENTS.md','02_检索与核验记录/handoff_20261012.md']:
 p=root/name;shutil.copy2(p,archive/p.name)
# The formal-rule addition already exists; its preceding committed version remains in Git history.
mother=root/'02_检索与核验记录/检索母表_20261011/具名平台母表.csv'
shutil.copy2(mother,archive/mother.name)
with mother.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert len(rows)==1319
for row in rows:
 if row['已有项目编号'] in ['T030-001','T4-002-001']:
  row['已有判断依据']+='\n2026-10-12：按用户最新机器人算法范围，将既有核实记录补入最新交付Excel；条件未知如实保留。'
  row['原记录位置']+='；'+new+'，新增详情及首页'
with mother.open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
assert not (archive/old).exists()
source.replace(archive/old)
staged.replace(target)
readme=root/'README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('('+old+')','('+new+')')
prefix='# 全国机器人开放项目个人申报台账\n'
latest='\n## 当前交付：已核实两项补入（2026-10-12）\n\n[打开最新台账]('+new+')。按用户最新要求：与机器人算法相关，记录来源、截止日期、具体方向、金额、申请条件及结题条件；保留原表头、四表结构、六列首页、样式和既有内容。T030-001、T4-002-001已由Excel外记录补入：首页24→26条、详情401→403条；此前21/397是过时快照。两项均10月20日截止，具体时刻未载；缺失条款如实保留。本机Excel开启提醒正常打开、既有值/样式/链接对照通过。旧版已归档。[补入及校验记录](02_检索与核验记录/已核实两项补入Excel_20261012.md)。母表仍1319条；005仍为最新全批完成回填，006未统一完成，全国补漏未完成。以下交接和批次记录为历史状态，暂不改Excel、不整理结题及更宽泛行业范围的旧要求以用户本次纠正为准。\n'
assert text.startswith(prefix);readme.write_text(prefix+latest+text[len(prefix):],encoding='utf-8')
agents=root/'AGENTS.md';text=agents.read_text(encoding='utf-8');text=text.replace('当前交付文件为《'+old+'》。','当前交付文件为《'+new+'》。',1);text+='\n## 2026-10-12用户最新补入范围（优先适用）\n\n与机器人算法相关；记录来源、截止日期、具体方向、金额、申请条件及结题条件。按已有Excel写法补入项目，原表头、结构、格式不自行改动。当前交付已补入T030-001/T4-002-001，首页26条、详情403条，旧21/397为历史快照。\n';agents.write_text(text,encoding='utf-8')
handoff=root/'02_检索与核验记录/handoff_20261012.md';text=handoff.read_text(encoding='utf-8');title='# 最新 handoff：全国机器人与医工开放项目\n';assert text.startswith(title)
note='\n> 2026-10-12后续用户纠正及实际交付：只收与机器人算法相关项目，记录来源、截止日期、具体方向、金额、申请条件和结题条件；已授权将整理到的两项补入Excel，保留原表头/结构/格式。T030-001及T4-002-001现已补入20261012版：首页26条、详情403条。原20261010文件实际24/401，旧21/397说法过时。此次未把氢储运行业线索列为相关项目；母表1319未新增平台。005仍是最新全批统一完成，006仍未统一回填，全国未完成。详情见[本次补入记录](已核实两项补入Excel_20261012.md)。下文暂不改Excel及不整理结题等为旧授权快照，已被用户最新要求替代。\n'
handoff.write_text(title+note+text[len(title):],encoding='utf-8')
check['native_excel_verification']='passed; DisplayAlerts=true; normal readonly open; no repair prompt'
check['final_output']=str(target);check['old_archived']=str(archive/old)
(record/'Excel补入内容校验.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
hydrogen=record/'已核实新增项目.json'
if hydrogen.exists():
 data=json.loads(hydrogen.read_text(encoding='utf-8'))
 for r in data:r['20261012用户纠正后分类']='未证实与机器人算法的具体联系，不列新增相关项目、不补入Excel；旧判断仅保留为过程记录。'
 hydrogen.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert len([p for p in root.glob('*.xlsx') if not p.name.startswith('~$')])==1
print('finalized',new,'overview 26; details 403; old archived; headers unchanged')
