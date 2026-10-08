import pathlib,json,hashlib,shutil
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2].resolve()
V=json.loads((H/'validation_regions.json').read_text(encoding='utf8'))
assert V['visual_review']=='passed'
name='全国机器人开放课题_个人申报台账_重点地区补查版_20261008.xlsx'
old=ROOT/'全国机器人开放课题_个人申报台账_严格重筛版_20261008.xlsx'
new=ROOT/name;source=H/name
archive=ROOT/'90_历史归档/02_旧版与输出记录/20261008_重点地区补查前交付版'/old.name
for p in [old,new,source,archive]:assert p.resolve().is_relative_to(ROOT),p
assert old.exists() and not new.exists() and not archive.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==V['sha256']
archive.parent.mkdir(parents=True,exist_ok=True)
oldhash=hashlib.sha256(old.read_bytes()).hexdigest()
shutil.copy2(source,new)
assert hashlib.sha256(new.read_bytes()).hexdigest()==V['sha256']
shutil.move(str(old),str(archive))
assert hashlib.sha256(archive.read_bytes()).hexdigest()==oldhash
assert [p.name for p in ROOT.glob('*.xlsx')]==[name]
for fn in ['AGENTS.md','项目说明.md']:
 p=ROOT/fn;s=p.read_text(encoding='utf8').replace(old.name,name)
 if fn=='项目说明.md':
  s=s.replace('本轮重筛后137个独立详情条目；首页12条正式受理公告、历史75条、待核46条、其他资助4条','本轮重点地区补查后148个独立详情条目；首页13条正式受理公告、历史78条、待核53条、其他资助4条')
 p.write_text(s,encoding='utf8')
readme=f'''# 全国机器人与医工开放项目

当前交付：[{name}]({name})。

正式要求见[后续补充检索规则](后续补充检索规则.md)。按公告具体机器人、具身智能、人机交互及相关智能装备任务筛选，客观记录条件，不作能力评价、评分或申报推荐。首页严格六列，受理中不代表个人已满足申报条件。

2026年10月8日重点地区补查，以GitHub提交011208e及既有台账、来源和检索记录为输入。按南京及周边、澳门、香港、华南理工及珠三角、北京、西安、重庆顺序记录69个机构/平台群检索对象；各对象的具体已查平台、年度、公告来源、检索记录和剩余缺口见[重点地区补查记录](重点地区补查记录_20261008.md)及Excel“03机构检索覆盖”。这表示实际已查范围，不能等同于69家机构全部平台核验完成，不能宣称七地区或全国全覆盖；全国其他地区留待下一阶段。

新增11个独立年度或机制条目（R001—R011）：1条当期、3条历史、7条待核。北京交通大学2027年度开放课题截止2026年10月20日，资格、周期及纸质份数存在原文差异，详情逐项保留。重复发现沿用原编号，没有将转载或同年度公告重复计数。苏锡常镇扬及深圳等14条既有记录按本轮地区顺序前移。

当前148个独立详情条目：首页13条当前窗口内正式公告、历史78条、待核53条、其他资助4条；累计剔除61条原记录。旧137条的任务及申报条款保留；199条原记录、筛选去向及隐藏输入留档保持原样。待核页包含截止当天时点不明的既有项目，未推算截止时点。

未取得的网页或附件按用户要求直接留下具体缺口及链接，停止反复尝试。主要手动待核项包括重庆交通大学M100指南/办法验证码、华南理工R005指南年度及任务、光明实验室R006完整正文、西安交大R007常年机制的当期有效性、重庆大学R008及重庆邮电R009年度通知、北航R010公告和导航R011任务指南。个人职称、限项、实际合作者、到访安排及外拨条件仍按具体项目确认。已取得资料未载与资料未取得分别标记，未用历史条件推填新年度。

本轮核验来源、检索原文、逐机构清单及验证记录位于 `90_历史归档/03_核验来源与处理记录/20261008_重点地区补查`。已检查六列首页、唯一编号、原条目保留、隐藏档案、日期、排序、链接、筛选、冻结及新条目显示。

根目录只保留最新Excel。前严格重筛版完整归档至 `90_历史归档/02_旧版与输出记录/20261008_重点地区补查前交付版`，旧文件哈希未改。此前重筛及核验来源继续保留。

## 自动上传

遵循AGENTS.md，每次完成修改后运行以下脚本提交并推送main；远程有未合入变更时停止，不强推或改写历史。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\sync-github.ps1
```

遵守.gitignore，个人未公开面上申请书、凭据、依赖和运行缓存不上传。
'''
(ROOT/'README.md').write_text(readme,encoding='utf8')
V.update({'delivered':str(new),'archived_previous':str(archive),'previous_sha256':oldhash,'root_only_one_excel':True})
(H/'validation_regions.json').write_text(json.dumps(V,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'delivered':str(new),'previous_archived':str(archive),'root_excel_count':1},ensure_ascii=False))
