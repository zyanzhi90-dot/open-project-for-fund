import pathlib,json,hashlib,shutil,re
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2].resolve();D=json.loads((H/'prepared_regions.json').read_text(encoding='utf8'));V=json.loads((H/'validation_regions.json').read_text(encoding='utf8'))
name='全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx';source=H/name;target=ROOT/name
assert V['stats']==dict(current=15,historical=95,pending=52,other=4,total=166,excluded=65)
assert hashlib.sha256(source.read_bytes()).hexdigest()==V['sha256']
manifest=json.loads((H/'render_manifest.json').read_text(encoding='utf8'));assert all((H/x['file']).exists() for x in manifest)
for x in manifest:x['status']='passed'
(H/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');V['visual_review']='passed'
oldfiles=[ROOT/'全国机器人开放课题_个人申报台账_重点地区补查版_20261008.xlsx',ROOT/'全国机器人开放课题_个人申报台账_重点地区补查版_20261008-网页修改版.xlsx']
archive=ROOT/'90_历史归档/02_旧版与输出记录/20261009_全国扩展前交付及网页修改版'
if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==V['sha256']
assert hashlib.sha256(pathlib.Path(D['current_input']).read_bytes()).hexdigest()==D['current_input_hash']
for p in [source,target,archive,*oldfiles]:assert p.resolve().is_relative_to(ROOT),p
assert all(p.exists() for p in oldfiles)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in oldfiles}
archive.mkdir(parents=True,exist_ok=True)
for p in oldfiles:
 if (archive/p.name).exists():assert hashlib.sha256((archive/p.name).read_bytes()).hexdigest()==hashes[p.name]
shutil.copy2(source,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==V['sha256']
for p in oldfiles:
 shutil.move(str(p),str(archive/p.name));assert hashlib.sha256((archive/p.name).read_bytes()).hexdigest()==hashes[p.name]
assert [p.name for p in ROOT.glob('*.xlsx') if not p.name.startswith('~$')]==[name]
for fn in ['AGENTS.md','项目说明.md']:
 p=ROOT/fn;s=p.read_text(encoding='utf8').replace(oldfiles[0].name,name)
 if fn=='项目说明.md':
  s=re.sub(r'本轮重点地区补查后148个独立详情条目；首页13条正式受理公告、历史78条、待核53条、其他资助4条；累计剔除61条原记录', '本轮全国扩展后166个独立详情条目；首页15条正式受理公告、历史95条、待核52条、其他资助4条；累计剔除65条原记录',s)
  s=s.replace('全国其他地区留待下一阶段。','本轮全国扩展已开展31个大陆省级区域及港澳地区发现/补漏检索，机构完整覆盖仍未完成；详见[全国扩展记录](全国扩展检索记录_20261009.md)和[手动补充事项](手动补充事项_20261009.md)。')
 p.write_text(s,encoding='utf8')
readme=f'''# 全国机器人与医工开放项目

当前交付：[{name}]({name})。

正式要求见[后续补充检索规则](后续补充检索规则.md)。按公告实际机器人、具身智能、人机交互、感知、规划、学习、控制及相关智能装备任务筛选，客观展示资格和条款，不作能力评价、评分或申报推荐。首页严格六列，当前受理不代表个人已满足条件。

本轮在GitHub提交06753b6及本地网页修改版150条上合并七个重点地区剩余补查与全国扩展，保留S001、S002和M066的本地修改。执行时间为北京时间2026年10月8—9日；最终截止基准10月9日，10月8日截止相关项目已转历史，不推算缺失的时点。

当前166个独立项目详情：首页15条、历史95条、待核52条、其他资助4条；累计剔除65条记录。新增16条N001—N016，其中11条历史公告、5条待核年度线索或长期机制；本轮没有新增已核当前受理公告。R006光明实验室首轮完整正文/模板补齐，3月31日18:00电子截止、30—100万元，移历史，未套第二批。M035、M043、M068、M106、M114截止日期已过移历史；M041补齐正文中的资格、报销不外拨和共享权属，具体机器人任务适用仍待核。150条输入记录全部保留，仅7条有记录的更新；199条原记录及隐藏输入档案保持原样。

保存52批搜索、208条查询，并追加72条具体机构范围记录。大陆31个省级区域及澳门、香港均有发现/补漏记录；台湾相关检索尚不足以形成机构级记录。复用前轮69个重点地区机构/平台群，所查平台、年份、公告和未查范围见[全国扩展检索记录](全国扩展检索记录_20261009.md)、[重点地区前轮记录](重点地区补查记录_20261008.md)及Excel机构覆盖页。数字表示查询/范围记录，不表示72家机构已经查完；全国及七地区的完整平台名录逐室年度覆盖仍未完成。

[手动补充事项](手动补充事项_20261009.md)按84个项目列精确网址及缺口，区分附件/网页未取得、正文未载和个人条件。当前主要受限项包括M100重庆交通大学附件验证码、R005华南理工年度不一致指南、R008重庆大学/R009重庆邮电/R010北航正式年度页、N012吉林工程仿生/N014江西飞行/N015湖南工学院/N016天津水利的管理或年度附件。S002跨年度指南的2026实际受理仍未核。已取得的R006正文不再交人工重复获取。

全国扩展来源、下载附件、逐字段记录、处理脚本和验证记录位于 `90_历史归档/03_核验来源与处理记录/20261008_全国扩展补查`。已通过唯一编号/分类、日期、六列首页、链接、排序、筛选、冻结、旧条款保留、隐藏档案和显示效果检查；网页修改版的表格关系异常通过重新生成修复，原输入完整归档。

根目录只保留最新版；前重点地区版和网页修改版完整归档至 `90_历史归档/02_旧版与输出记录/20261009_全国扩展前交付及网页修改版`，两份输入哈希未变。前[省级平台和业务费样本记录](省级重点实验室与中央高校基本科研业务费专项补查_20261008.md)保留，其“不新增历史”描述不限制本轮用户最新授权的历史机制补查。

## 自动上传

遵循AGENTS.md，每次完成修改后执行以下脚本提交并推送main；远程有未合入变更则停止，不强推或改写历史。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\sync-github.ps1
```

遵守.gitignore，个人未公开申请书、凭据、依赖及运行缓存不上传。
'''
(ROOT/'README.md').write_text(readme,encoding='utf8')
V.update(delivered=str(target),archived_inputs=[str(archive/p.name) for p in oldfiles],archived_input_hashes=hashes,root_only_one_excel=True)
(H/'validation_regions.json').write_text(json.dumps(V,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'delivered':str(target),'archived_input_count':2,'root_excel_count':1,'stats':D['stats']},ensure_ascii=False))
