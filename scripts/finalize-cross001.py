"""Persist reviewed cross-search facts; no network and no workbook changes."""
import csv, hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '02_检索与核验记录/第四步交叉补漏_20261011'
MOTHER = ROOT / '02_检索与核验记录/检索母表_20261011/具名平台母表.csv'
ARCHIVE = ROOT / '90_历史归档/02_旧版与输出记录/20261011_第四步001前母表'

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if (OUT/'本轮校验_001.json').exists():
        raise SystemExit('Batch 001 already persisted; inspect its audit instead of reapplying.')
    fields, rows = read_csv(MOTHER)
    before = len(rows)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    saved = ARCHIVE / MOTHER.name
    if not saved.exists():
        shutil.copy2(MOTHER, saved)
    updates = {
        'M145': ('第四步核验·窗口成立但任务未有相关装备依据',
                 '2026年度公告，截止2026-10-30 17:00；实际为影像生成修复、多模态影像处理、档案知识服务、数字文旅及文化传播；文旅装备泛词未提供机器人或相关智能装备感知决策控制任务依据。不列当前相关项目。',
                 '2026年度；同4556.htm来源补明确窗口任务，不宣称发现新批次',
                 'main001/影像线索窗口任务复核原始返回.json')
    }
    changes = []
    for row in rows:
        key = row.get('已有项目编号', '')
        if key not in updates:
            continue
        category, fact, scope, evidence = updates[key]
        if fact in row.get('已有判断依据', ''):
            continue
        changes.append({'平台ID':row['平台ID'],'项目编号':key,'原分类':row['已有核验分类'],'本轮分类':category,'事实':fact,'证据':evidence})
        row['已有核验分类'] = category
        row['已有判断依据'] += '\n2026-10-11第四步001：' + fact
        row['年度核验范围'] += '\n' + scope
        row['20261011定向补查记录'] += '\n第四步交叉补漏_20261011/' + evidence
        row['下一步'] = '本轮事实保留；不重复已截止补取或同批检索；新来源/新批次另核。'
    platform = '京东方技术策源地开放课题计划'
    if not any(row['平台名称原称'] == platform for row in rows):
        row = dict.fromkeys(fields, '')
        row.update({'平台ID':'P-'+hashlib.sha256(platform.encode()).hexdigest()[:12],
                    '依托机构原称':'京东方（BOE）','平台名称原称':platform,
                    '规范身份状态':'官方域名搜索返回确认开放课题计划；正文首次受阻',
                    '检索顺序依据':'第四步真实滚动新申请路径附带发现',
                    '已有核验分类':'第四步线索·滚动窗口搜索证据/正文及任务未取得',
                    '已有判断依据':'官方搜索返回明示2026.09至2027.06滚动接收项目申报材料。正文首次超时停止；具体任务未核清与机器人/智能装备联系，明示金额及申请条件未取得。不列当前相关正式项目。',
                    '当期可申报结论':'仅线索；任务证据未成立，不认定个人可申请',
                    '年度核验范围':'2026技术策源地计划；官方搜索返回2026-09-23发布',
                    '来源URL候选':'https://www.boe.com/directory/innovation_opening',
                    'URL使用限制':'本轮首次超时；失败不重试、不下载申请书',
                    '原记录位置':'第四步交叉补漏_20261011/main001',
                    '原证据行':'东北华北西北交叉检索原始返回.json；京东方首次正文受阻.json',
                    '下一步':'保留缺口，不重试本轮失败URL；只有实际新来源/新批次出现时增量核查',
                    '20261011定向补查记录':'第四步交叉补漏_20261011/main001/京东方首次正文受阻.json'})
        rows.append(row)
        changes.append({'平台ID':row['平台ID'],'项目编号':'','原分类':'母表未有','本轮分类':row['已有核验分类'],'事实':row['已有判断依据'],'证据':row['20261011定向补查记录']})
    write_csv(MOTHER, fields, rows)
    write_csv(OUT/'母表增量变化_001.csv',list(changes[0]) if changes else ['平台ID'],changes)
    facts = [
        ('M100/S004/M066/M160/M029/M105/T030-001','既有同批复用','全国/地区搜索再次命中，不重复新增；T030联合新增CSV核对'),
        ('M119/E153/M049','既有排除复用','网络安全任务/清华专属科研专项/河南省内入口分别复用原排除；不凭未来日期恢复'),
        ('M106/N102/M053/M057/E078','已截止或既有排除','搜索返回明确截止；不补条款'),
        ('M085','沿用既有交通智能感知边界证据','此前核验记录保留具体多模态交通感知任务；本轮摘要缺机器人字样不构成降级理由'),
        ('M056','窗口未核清','仅本轮主页入口，未取得新的明确滚动受理依据；不重复旧失败入口'),
        ('M192','截止年份不明确/既有历史同源','子代理摘录落款2025-09-15，截止10月31日未注明年份；不能推成2026-10-31，保留基准已截止及缺档边界'),
        ('云南生物资源保护与利用2026','窗口成立但无相关任务依据','2026-10-23截止；公告要求符合实验室方向，官方方向入口实际为生物资源、系统演化适应、生态功能，无明确机器人或相关智能装备任务'),
        ('京东方2026','线索及首次受阻','正式官方搜索显示真实滚动接收新材料；正文受阻，相关任务未核清，不列新增当前项目'),
        ('south001','独立整理结果/原始返回缺档','10条查询及7项整理结果，已截止/未开放/非申请；不能作为充分覆盖证明，不重新请求恢复缺档'),
        ('northwest001','独立整理及部分逐字摘录/完整原始响应缺档','23条查询，主代理仅采用独立复核/基准支持的事实；其余留整理证据层级')
    ]
    write_csv(OUT/'主代理核验与去重_001.csv',['对象','处理','依据与边界'],[dict(zip(['对象','处理','依据与边界'],x)) for x in facts])
    queries = []
    for path in sorted((OUT/'main001').glob('*检索原始返回.json')) + [OUT/'main001/全国交叉搜索原始返回.json'] + sorted((OUT/'east001').glob('原始查询结果_*.json')):
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        for query in data.get('queries', []):
            queries.append({'查询':query,'证据文件':str(path.relative_to(OUT)),'证据层级':'真实工具返回已落盘'})
    for folder, filename in [('south001','south001_检索证据.json'),('northwest001','结果与候选.json')]:
        path = OUT/folder/filename
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        for query in data.get('queries', []):
            queries.append({'查询':query,'证据文件':str(path.relative_to(OUT)),'证据层级':'子代理整理；完整原始响应缺档，不能计充分覆盖证明'})
    write_csv(OUT/'查询与证据索引_001.csv',['查询','证据文件','证据层级'],queries)
    parsed = []
    for path in OUT.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8-sig'))
        parsed.append(str(path.relative_to(OUT)))
    workbook = ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
    actual = hashlib.sha256(workbook.read_bytes()).hexdigest()
    assert actual == '086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    assert len({r['平台ID'] for r in rows}) == len(rows)
    summary = {'日期':'2026-10-11','母表更新前':before,'母表更新后':len(rows),'本轮新增当前受理相关正式项目':0,
               '新增平台线索':1,'查询记录':len(queries),'真实返回落盘查询':sum(q['证据层级']=='真实工具返回已落盘' for q in queries),
               '整理但完整原始响应缺档查询':sum(q['证据层级']!='真实工具返回已落盘' for q in queries),
               'JSON可解析文件':parsed,'ExcelSHA256':actual,'Excel未改':True,
               '全国补漏完成':False,'限制':'查询索引/JSON解析不证明地区或全国穷尽，缺档不伪造、不重搜恢复。'}
    (OUT/'本轮校验_001.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='JSON可解析文件'},ensure_ascii=True))

if __name__ == '__main__':
    main()
