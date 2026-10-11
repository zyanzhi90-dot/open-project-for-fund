"""从已保存的官方目录提取名称底册；关键词仅分派查阅顺序。"""
from pathlib import Path
import csv,re,json,html,zipfile,xml.etree.ElementTree as ET
import pdfplumber
P=Path(__file__).resolve().parent
rows=[];checks=[]
def norm(v):return re.sub(r'\s+','',v or '')
for file,province,url,name,year in [
 ('辽宁2023平台.pdf','辽宁','https://kjt.ln.gov.cn/kjt/attachDir/2023/03/2023032915181664879.pdf','辽宁2023省级科技创新平台目录','2023'),
 ('广东平台503027.pdf','广东','https://gdstc.gd.gov.cn/attachment/0/503/503027/4019700.pdf','广东2022考核重点实验室名单（学科及企业类）','2022')]:
    before=len(rows);numbers=[]
    with pdfplumber.open(P/'来源快照'/file) as d:
        for page_no,page in enumerate(d.pages,1):
            for table in page.extract_tables():
                for cell in table:
                    if len(cell)<3:continue
                    num=norm(cell[0])
                    if not num.isdigit():continue
                    n=norm(cell[1]);inst=norm(cell[2])
                    if not n:continue
                    numbers.append(int(num))
                    kind=norm(cell[3]) if province=='辽宁' else '省重点实验室（目录含学科及企业类）'
                    rows.append({'目录来源':name,'目录年度':year,'地域':province,'序号':num,'平台类别':kind,'平台名称':n,'依托机构':inst,'来源URL':url,'来源定位':f'{file}第{page_no}页/序号{num}','目录性质':'历史平台身份底册；不证明当期受理及现行存续','平台详情入口':'','取证日期':'2026-10-11'})
        xs=rows[before:];keys={(r['平台名称'],r['依托机构']) for r in xs}
        assert len(keys)==len(xs), '同文件平台身份重复须先核'
        checks.append({'来源':file,'总页数':len(d.pages),'提取行数':len(xs),'身份去重后':len(keys),'序号说明':'不同类别重新从1编号；不可把重复序号当重复平台','缺行限制':'已遍历全部页面表格；合并单元格/跨页内容仍须结合来源定位复核'})
s=(P/'来源快照/浙江目录.html').read_text(encoding='utf8')
for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',s,re.S|re.I):
    cs=re.findall(r'<td\b[^>]*>(.*?)</td>',tr,re.S|re.I)
    if len(cs)<3:continue
    text=lambda v:norm(html.unescape(re.sub('<[^>]+>','',v)))
    if not text(cs[0]).isdigit():continue
    m=re.search(r"window.open\('([^']+)'\)",cs[1]);entry='https://stbrain.kjt.zj.gov.cn'+m.group(1) if m else ''
    rows.append({'目录来源':'浙江科技创新云重点实验室工程中心目录首屏','目录年度':'动态页未载年度','地域':'浙江','序号':text(cs[0]),'平台类别':'重点实验室/工程研究中心','平台名称':text(cs[1]),'依托机构':text(cs[2]),'来源URL':'https://stbrain.kjt.zj.gov.cn/CarrierList.aspx?Code=SYS','来源定位':'首屏序号'+text(cs[0]),'目录性质':'首屏20条；更多入口未取得，未闭环','平台详情入口':entry,'取证日期':'2026-10-11'})
config=P/'补充目录配置.json'
if config.exists():
    for c in json.loads(config.read_text(encoding='utf8')):
        if c['download_status']!='已取得':continue
        before=len(rows);q=P/'来源快照'/c['file']
        if q.suffix=='.docx':
            with zipfile.ZipFile(q) as z:root=ET.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            tables=[]
            for ti,tb in enumerate(root.findall('.//w:tbl',ns),1):
                cells=[[''.join(t.text or '' for t in cell.findall('.//w:t',ns)) for cell in tr.findall('w:tc',ns)] for tr in tb.findall('w:tr',ns)]
                tables.append((f'表格{ti}',cells))
        else:
            with pdfplumber.open(q) as d:
                tables=[(f'第{pn}页',tb) for pn,pg in enumerate(d.pages,1) for tb in pg.extract_tables()]
        for location,table in tables:
            for ri,cell in enumerate(table,1):
                if len(cell)<=max(c['platform_col'],c['institution_col']):continue
                n=norm(cell[c['platform_col']]);inst=norm(cell[c['institution_col']])
                if not n or n in ['实验室名称','工程中心名称','平台名称']:continue
                if q.suffix!='.docx' and not norm(cell[0]).isdigit():continue
                if not inst:continue
                num=norm(cell[0]) or f'表格行{ri}（原为自动编号）'
                kind='教育部工程研究中心' if '教育部工程' in c['name'] else '省重点实验室'
                rows.append({'目录来源':c['name'],'目录年度':c['year'],'地域':c['province'],'序号':num,'平台类别':kind,'平台名称':n,'依托机构':inst,'来源URL':c['url'],'来源定位':c['file']+location+'/行'+str(ri),'目录性质':'具名平台底册；不证明当期受理；拟建设及历史身份需再核存续','平台详情入口':'','取证日期':'2026-10-11'})
        count=len(rows)-before
        if c['province']=='福建':assert count==267,f'福建应有267条，实际{count}'
        checks.append({'来源':c['file'],'提取行数':count,'整份遍历':True,'身份去重后':len({(r['平台名称'],r['依托机构']) for r in rows[before:]})})
# 只有名称线索，不等于符合实际任务。无关键词记录仍保留供目录补漏。
for r in rows:
    r['执行分组']='先看实际任务' if re.search('机器人|具身|人机|自动化|装备|机械|机电|感知|视觉|测控|控制|智能|制造|导航|信息融合|医学影像|生物医学工程|医用电子|检测|传感',r['平台名称']) else '目录留存；任务摘要补漏'
    r['来源核验限制']='旧目录须核撤销/新增/更名；未知依托单位不猜测'
with (P/'新增官方目录名称底册.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'目录提取检查.json').write_text(json.dumps({'来源检查':checks,'总行数':len(rows),'优先读任务候选':sum(r['执行分组']=='先看实际任务' for r in rows),'浙江范围':'仅20条首屏；更多入口一次访问失败'},ensure_ascii=False,indent=2),encoding='utf8')
print((P/'目录提取检查.json').read_text(encoding='utf8'))
