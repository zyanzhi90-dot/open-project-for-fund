from pathlib import Path
import shutil,json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[2]
v=json.loads((H/'validation.json').read_text(encoding='utf8'));new=H/v['output'];old=R/'全国机器人开放课题_个人申报台账_独立复核合并版_20261009.xlsx'
assert new.exists() and old.read_bytes()==(H/'input.xlsx').read_bytes()
archive=R/'90_历史归档/02_旧版与输出记录/20261009_结构精简前完整工作簿';archive.mkdir(exist_ok=True)
assert archive.resolve().is_relative_to(R.resolve())
for fn in ['README.md','AGENTS.md','后续补充检索规则.md','01_项目说明与背景/项目说明.md']:
 p=R/fn;dst=H/('整理前_'+p.name)
 if not dst.exists():shutil.copy2(p,dst)
audit=R/'02_检索与核验记录/审计记录';audit.mkdir(exist_ok=True)
for x in v['removed_to_csv']:
 dst=audit/x['file'];assert not dst.exists();shutil.copy2(H/x['file'],dst)
dst=archive/old.name;assert not dst.exists()
# The verified full original is archived before installing the compact root deliverable.
shutil.move(str(old),str(dst));shutil.copy2(new,R/new.name)
assert hashlib.sha256(dst.read_bytes()).hexdigest()==hashlib.sha256((H/'input.xlsx').read_bytes()).hexdigest()
readme=f'''# 全国机器人开放项目个人申报台账

[打开最新台账]({new.name}) · [查看人工接力清单](03_人工补充/手动补充事项_20261009.md)

当前166条项目：正式受理15条、历史96条、待核51条、其他资助4条。受理状态不代表本人已满足资格与合作条件。全国逐平台年度检索仍有缺口，具体范围见检索记录。

## 日常使用

1. 在“01申报总览”查看当前正式受理项目；首页严格六列。
2. 点击实验室名称，进入“02项目完整详情”核对资格、合作、金额、外拨、周期、成果、知识产权和提交方式。
3. 需要以后参考、核实线索或查看其他资助时，分别使用历史、待核、其他资助页。
4. 缺附件或条款时，查看人工接力清单；需要了解机构已查范围时，使用机构覆盖页及检索记录。

## 文件位置

| 位置 | 内容 |
|---|---|
| 根目录 | 唯一最新Excel、本说明、AGENTS工作约定、正式检索规则 |
| [01_项目说明与背景](01_项目说明与背景/) | [工作簿与项目使用说明](01_项目说明与背景/项目说明.md)、仅本地保存的个人申请书 |
| [02_检索与核验记录](02_检索与核验记录/) | 全国、重点地区、专项及独立复核记录；[核验日志CSV](02_检索与核验记录/审计记录/项目核验日志_20261009.csv)与[剔除记录CSV](02_检索与核验记录/审计记录/项目剔除记录_20261009.csv) |
| [03_人工补充](03_人工补充/) | 当前人工操作、官方咨询及字段缺口清单 |
| [90_历史归档](90_历史归档/) | 完整旧台账、原始输入、官方来源、附件及处理记录 |
| [scripts](scripts/) | GitHub同步脚本 |

## 已有检索成果

- [全国扩展及剩余覆盖缺口](02_检索与核验记录/全国扩展检索记录_20261009.md)：52批、208条查询，追加72条机构范围记录；涉及大陆31个省级区域及港澳，未认定逐平台全覆盖。
- [七个重点地区检索记录](02_检索与核验记录/重点地区补查记录_20261008.md)：此前69个机构/平台群及具体年度证据。
- [省级平台与中央高校业务费专项记录](02_检索与核验记录/省级重点实验室与中央高校基本科研业务费专项补查_20261008.md)。
- [独立补查合并记录](02_检索与核验记录/独立补查核验记录_20261009.md)：M014、M078、R011、R008的证据修正。

## 工作约定

以[正式检索规则](后续补充检索规则.md)和[AGENTS](AGENTS.md)为依据。按公告具体任务筛选，不作能力判断、评分或申报推荐；未知条款明确标记。个人申请书只供研究背景参考，不限制申报范围。

主工作簿从10张表精简为6张，全部项目内容保留。2392条核验日志及65条剔除记录移到CSV，199条原始记录与2236条输入留档保留在[精简前完整工作簿](90_历史归档/02_旧版与输出记录/20261009_结构精简前完整工作簿/{old.name})。原有审计链接转向该完整归档中的对应位置。结构变更不代表重新检索或重新核验项目条款。

无工作簿内容变化不生成新Excel；更新时先验证，再归档旧版，根目录只留最新版。核验来源和旧记录保留，个人未公开申请书、凭据、依赖及缓存不上传。

修改完成后执行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\sync-github.ps1`，确认上传成功；不强推或改写远程历史。
'''
(R/'README.md').write_text(readme,encoding='utf8')
guide='''# 项目及工作簿使用说明

项目目标是建立全国机器人相关开放基金、开放课题和开放研究项目的个人申报台账。研究范围、筛选标准及证据要求见[正式检索规则](../后续补充检索规则.md)；当前交付、文件位置和检索入口统一见[README](../README.md)。

## 当前工作簿的六张表

| 工作表 | 用途 | 当前内容 |
|---|---|---|
| 01申报总览 | 日常查看正式受理项目；六列简洁展示，实验室名称链接详情 | 15条 |
| 02项目完整详情 | 全部项目条款的统一记录，编号、来源、具体缺口均在这里 | 166条、27个字段 |
| 03历史项目 | 保存已截止但任务相关的项目，供下一年度参考 | 96条 |
| 04待核项目 | 正式年度、任务、窗口或证据不足的项目 | 51条 |
| 05其他资助 | 与正式开放基金不同的资助项目 | 4条 |
| 06机构检索覆盖 | 已查实验室、年份、公告及剩余缺口 | 既有机构范围记录；不等同于机构查完 |

分类页便于浏览，完整详情保存全部条款，因此没有把分类页合并进一张宽表。历史、待核、其他资助仍按正式要求分开。

## 不再放在主工作簿中的四张表

- 核验日志：保存为[CSV](../02_检索与核验记录/审计记录/项目核验日志_20261009.csv)，2392条，可用Excel打开和筛选。
- 剔除记录：保存为[CSV](../02_检索与核验记录/审计记录/项目剔除记录_20261009.csv)，65条，保留编号、理由和来源。
- 筛选前原始记录、输入版本留档：在[精简前完整工作簿](../90_历史归档/02_旧版与输出记录/20261009_结构精简前完整工作簿/全国机器人开放课题_个人申报台账_独立复核合并版_20261009.xlsx)保留，日常使用不必加载。

主台账原先指向审计日志的链接已转为完整归档文件中的原位置。后续更新的核验和剔除记录应继续保存在“02_检索与核验记录/审计记录”，避免重新塞回主台账；已有快照及来源不覆盖删除。

## 人工补充及研究背景

[人工接力清单](../03_人工补充/手动补充事项_20261009.md)区分网页附件受阻、正文未载、文件冲突及本人条件；取得资料后再按证据更新，不推测未知条款。

[个人面上申请书](面上项目-正文-2026-修改版-3.18-1.pdf)仅在本地保存，只用于了解研究背景，不作为能力边界或申报范围限制。
'''
(R/'01_项目说明与背景/项目说明.md').write_text(guide,encoding='utf8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf8').replace(old.name,new.name)
s+='\n## 工作簿及审计记录位置\n\n主台账保留六张表：申报总览、项目完整详情、历史项目、待核项目、其他资助、机构检索覆盖。核验日志和剔除记录保存在 `02_检索与核验记录/审计记录/` 的CSV；原始输入和版本留档保存在归档完整工作簿中。项目条款和来源不因结构整理删减，历史、待核、其他资助仍分开。\n';p.write_text(s,encoding='utf8')
record='''# 项目结构梳理记录

结构整理于用户端2026-10-08进行；台账项目核查基准沿用2026-10-09，文件日期沿用该基准。未启动新检索，未变更166个项目条款或分类。

主Excel由10张表精简为6张，日常分类浏览与全部详情保留，机构覆盖页保留。核验日志2392条、剔除记录65条完整导出CSV，已逐字段回读核对；原始199条和2236条输入留档保留在完整旧版Excel。保留六表的单元格值、格式、表对象、筛选、冻结及公告链接均一致；166个原日志锚点改为完整归档工作簿链接。首页与机构覆盖视图检查通过。

README改为当前成果及目录入口；项目说明集中解释六张表和审计档案用途；正式筛选规则未改。根目录只保留一个新Excel。原完整Excel和整理前文档均保留，证据及处理记录在“90_历史归档/03_核验来源与处理记录/20261008_项目结构梳理”。
'''
(R/'02_检索与核验记录/项目结构梳理记录_20261008.md').write_text(record,encoding='utf8')
broken=[];checked=0
for f in list(R.glob('*.md'))+list((R/'01_项目说明与背景').glob('*.md'))+list((R/'02_检索与核验记录').glob('*.md')):
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf8')):
  if re.match(r'\w+://',target) or target.startswith('#'):continue
  checked+=1
  if not (f.parent/target.split('#',1)[0]).exists():broken.append([str(f.relative_to(R)),target])
assert not broken,broken
assert len(list(R.glob('*.xlsx')))==1
v.update({'visual_review':'passed','local_links_checked':checked,'root_excel_count':1,'old_full_workbook_archived_hash_checked':True});(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(v,ensure_ascii=False))
