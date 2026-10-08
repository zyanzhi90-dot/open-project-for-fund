import pathlib,json,hashlib
H=pathlib.Path(__file__).parent
rows=json.loads((H/'row_height_audit.json').read_text(encoding='utf8'))
assert not any(x['clippedEstimate'] for x in rows)
manifest=json.loads((H/'render_manifest.json').read_text(encoding='utf8'))
assert len(manifest)==17
for x in manifest:
 p=H/x['file'];assert p.exists()
 x['status']='passed';x['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 x['observations']='已逐张目视检查：文字可读、换行正常、无可见截断或相互覆盖。'
(H/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
v=json.loads((H/'validation_strict.json').read_text(encoding='utf8'))
v.update({'visual_review':'passed','visible_sheets_checked':8,'images_checked':17,'row_height_estimated_clipping':0,'visual_scope':'首页12条全部检查；详情分栏、最长经费和成果、受限附件项目；机构覆盖、日志、旧/新剔除、历史首尾、待核、其他资助代表区域。全表逐行行高估算无截断。联系人修正后重绘受影响待核图，其余16个区域显示内容未变。'})
(H/'validation_strict.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
p=H/'sources/M100.json';s=json.loads(p.read_text(encoding='utf8'))
for q in s['sources']:
 q['urllib_fetch_status']=q['status'];q['status']='未取得：网页工具已确认附件下载需要验证码'
 q['browser_result']='请输入验证码下载附件';q['checked_at']='2026-10-08'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8')
(H/'本轮处理记录.md').write_text('''# 2026-10-08 严格重筛与交付

复读此前 prepared_final.json、validation_final.json、verified_review.json，复用 sources；只补访问既有项目的官方附件入口及NSFC正式通告，不扩展地域检索。

166项人工任务判定：93保留、44方向或指南待核、29新增剔除。磁浮技术实验室M146因实际任务为磁浮交通而无机器人任务，已剔除。累计61条原记录剔除；137条详情覆盖138条原记录，另含M124/M125原编号合并映射；199条去向完整。

首页12条正式窗口公告、历史75、待核46（含5条今日截止未载时点）、其他资助4，互不重复。首页严格六列，按熟悉地区、截止时间排序。保留筛选、冻结和原生内外超链接，不添加能力结论。

逐条记录任务、公告、截止、金额及7类详细条款，共1826条字段记录。修正51项条款及3项联系人：移除往年混用和其他实验室条款，补明确的学历、年龄、固定合作者、拨款、到室交流及成果数量/署名。年度冲突、未载明、未取得、本人情况待核分开显示。南京大学M194软件商客服邮箱误提取已改正；M137及M032改用具体联系人。

重庆交通大学附件验证码导致未取得指南和管理办法；两项NSFC通告需登录GRANTS取得完整指南。上述缺口没有猜测补填，仍保留待核。旧覆盖记录混入的search?keywords无效页面已从现行展示删除，原文件/原始输入留档；机构完成程度仍只标部分检索。

artifact-tool生成新版，XML补原生链接和隐藏留档页；read-only检查日期、表格筛选、冻结、链接、排序、199条原记录去向和原始32字段完整。17张图逐张检查，首页12条全部检查、各可见表及长条款抽样检查；全表行高估算无截断。未声称逐行渲染了全部详情。

仅因本轮内容变动生成新版；验证后将上一最终核验版原样归档，根目录只留一个最新Excel。同步按现有scripts/sync-github.ps1执行，既有每小时自动同步配置不变。
''',encoding='utf8')
print('Visual and source-access records complete.')
