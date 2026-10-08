from pathlib import Path
import shutil,json,hashlib,re,zipfile
import openpyxl,xml.etree.ElementTree as E
H=Path(__file__).resolve().parent;R=H.parents[2]
archive=R/'90_历史归档/02_旧版与输出记录/20261009_独立复核合并前版本';archive.mkdir(parents=True,exist_ok=True)
for src,dst in [(H/'baseline.xlsx',archive/'全国机器人开放课题_个人申报台账_全国扩展版_20261009_GitHub原版.xlsx'),(H/'user_input.xlsx',archive/'全国机器人开放课题_个人申报台账_全国扩展版_20261009_用户独立复核版.xlsx')]:
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copy2(src,dst)
for name in ['独立补查与人工接力更新_20261009.md','独立补查核验记录_20261009.md','手动补充事项_20261009.md']:
 src=R/name;dst=H/('合并前_'+name)
 if not dst.exists():shutil.copy2(src,dst)
old=R/'全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx';new=H/'全国机器人开放课题_个人申报台账_独立复核合并版_20261009.xlsx';w=openpyxl.load_workbook(new)
# Independent checks against both inputs and native package content.
inp=openpyxl.load_workbook(H/'user_input.xlsx')
assert [r[0] for r in list(w['02项目完整详情'].values)[1:]]==[r[0] for r in list(inp['02项目完整详情'].values)[1:]]
assert list(w['01申报总览'].values)==list(inp['01申报总览'].values)
def links(p):
 with zipfile.ZipFile(p) as z:return sum(len(list(E.fromstring(z.read(n)).iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}hyperlink'))) for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',n))
assert links(new)==links(H/'user_input.xlsx'),(links(new),links(H/'user_input.xlsx'))
assert w['07待核项目']['F20'].hyperlink.target=='https://slmt.cqu.edu.cn/index/tzgg.htm'
detail={r[0]:r for r in list(w['02项目完整详情'].values)[1:]}
manual=(H/'合并前_手动补充事项_20261009.md').read_text(encoding='utf8')
lines=manual.splitlines();revised=[]
for line in lines:
 m=re.match(r'\|(M078|R011|R008)\|',line)
 if m:
  id=m[1];r=detail[id];url=r[19];need=r[18].replace('\n','<br>');line=f'|{id}|{r[2]}·{r[3]}／{r[5]}|{url}|{need}|'
 revised.append(line)
manual='\n'.join(revised)+'\n'
manual=re.sub(r'^# .*', '# 当前人工接力清单与全部字段缺口（独立复核合并）',manual,count=1)
intro='''
本清单已合并用户独立复核材料。当前台账166条：当前15、历史96、待核51、其他4。R011已取得官方高校转载并转历史，不再要求人工找完整公告；其管理附件/经费/IP仍有缺口。M078第22条一般权属规则已核实，不再标为全部未知。

## 需要人工操作或咨询的三项

| 编号 | 官方入口 | 需要提供的材料或确认 |
|---|---|---|
| M100 | https://news.cqjtu.edu.cn/info/1024/68220.htm | 通过验证码下载2026申报指南和管理办法原附件；已知10月30日17:00截止。 |
| R001 | https://raolab.bjtu.edu.cn/news/3521.html | 向hrma@bjtu.edu.cn确认资格“且/或”、周期1/2年、纸质材料2/3份三处官方文件冲突；10月20日截止。 |
| S002 | https://hdldb.net/news-detail.php?id=MjQwMQ%3D%3D | 向loojourney@163.com确认跨年度指南在2026是否仍受理、实际截止、医院合作、临床数据及经费安排。 |

以下原清单仍保留其他项目逐项网址和字段缺口。缺口并不都需要立即手动搜索：正文未载条款、合作人和合同内容应由主办方或本人确认；验证码/下载受阻项才需要取得附件。N012、N014、N015、N016等历史附件可按需要补齐。M078同一URL存在年度指南与一般办法不同官方快照，周期和提交材料适用关系仍需确认；当前台账保留年度指南，未据一般办法覆盖。

## 全部既有项目的具体缺口
'''
head,tail=manual.split('\n',1);manual=head+'\n'+intro+'\n'+tail
(R/'手动补充事项_20261009.md').write_text(manual,encoding='utf8')
record='''# 独立补查材料合并核验记录

以GitHub提交5384d592f4a14cdc46cd2c7bf71a63cf92abe8eb为基线，与用户替换的同名Excel逐格比较：用户改动详情29格、待核页8格、追加5条核验日志，首页及其他工作表数值不变。输入原件和两份原始独立复核文档均已归档，未用旧台账覆盖最新成果。

## 四项证据复核与合并

| 编号 | 已确认事实及处理 | 官方来源 |
|---|---|---|
| M014 | 2026年度单项不超过20万元、1年、定期到室交流和阶段报告、周凡及zhoufan@bigai.ai。保留用户纠正的详情，并同步历史页金额；移除当前条款中混用2025资料，旧证据留档。 | https://sist.pku.edu.cn/info/2320/10785.htm |
| M078 | 官方搜索快照的管理办法第22条支持外单位成果由实验室与承担单位共有。保留该一般规则及合同待确认；当前直开同URL为2026指南，周期≤12个月、电子提交。一般办法1—2年/纸质3份与年度指南存在差异，未直接替换年度条款。 | https://dqxylib.szut.edu.cn/info/1016/27682.htm |
| R011 | 官方高校转载明确机器人/无人系统导航任务、10万元、12或24个月、6月15日截止，撤销“全文未取得”。按既有规则转历史，不新增编号；原主办方管理附件、资金、合作及IP仍未核。 | https://keyanchu.syuct.edu.cn/info/1028/2075.htm |
| R008 | 原90052.htm确为2026科技活动周/公众开放日通知，不能当基金公告。详情与待核页链接统一改为官方通知栏目，旧误链仅留在纠错证据中。 | https://slmt.cqu.edu.cn/info/10663/90052.htm ； https://slmt.cqu.edu.cn/index/tzgg.htm |

## 合并边界与验证

未新增项目，166条编号全部保留；当前15、历史96、待核51、其他4，累计剔除65条。R011由待核转历史使分类数变化，不代表新增。M066、S001、S002、R006及M018等已有成果不重复添加。独立文档中“不新增历史”的描述仅为该轮处理记录，不修改项目正式检索规则。

首页六列及15条内容未改变，机构覆盖、剔除、其他资助和两张隐藏档案数值全部一致，10个表对象保留，超链接总数未减少。改动视图已渲染检查，错误扫描无匹配；无需重建无关工作表。完整逐格差异、处理脚本和验证结果见本次核验档案。

全国及七重点地区逐平台年度检索的剩余缺口仍见《全国扩展检索记录_20261009.md》，本次整理不代表完成新一轮全国检索。人工事项统一以《手动补充事项_20261009.md》为当前入口；较早“尚未取得Excel”的交付说明已归档。

本次整理发生于用户端2026-10-08（Europe/London）；项目核查基准沿用北京时间2026-10-09，故保留09文件日期。
'''
(R/'独立补查核验记录_20261009.md').write_text(record,encoding='utf8')
early=R/'独立补查与人工接力更新_20261009.md';dst=archive/early.name
if early.exists():shutil.move(str(early),str(dst))
for fn in ['README.md','AGENTS.md','项目说明.md']:
 p=R/fn;s=p.read_text(encoding='utf8').replace('全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx',new.name)
 if fn in ['README.md','项目说明.md']:
  s=s.replace('历史95条','历史96条').replace('待核52条','待核51条')
 if fn=='README.md':
  note='\n已合并用户独立复核材料：M014、M078、R011、R008四项证据经复核保留，M014历史页金额同步，R011已截止转历史，R008误链排除。当前166条（15/96/51/4），未新增编号；详见[独立补查合并记录](独立补查核验记录_20261009.md)与[当前人工接力清单](手动补充事项_20261009.md)。两份输入台账及原始复核文档已归档。此前全国扩展阶段的15/95/52/4为当轮数量。\n'
  pos=s.find('\n\n正式要求');s=s[:pos]+note+s[pos:]
  s=s.replace('84个项目','84个项目（涵盖原待核及其他字段缺口，不全是需立即人工操作）')
 p.write_text(s,encoding='utf8')
# Only install after validation; archive the supplied root input intact.
if old.exists():
 assert old.read_bytes()==(H/'user_input.xlsx').read_bytes(),'输入在处理期间有变化'
 dst=archive/'全国机器人开放课题_个人申报台账_全国扩展版_20261009_用户独立复核版.xlsx'
 if dst.exists():assert old.read_bytes()==dst.read_bytes();old.unlink()
 else:shutil.move(str(old),str(dst))
shutil.copy2(new,R/new.name)
assert len(list(R.glob('*.xlsx')))==1
v=json.loads((H/'validation.json').read_text(encoding='utf8'));v.update({'visual_review':'passed','hyperlinks_preserved':links(new),'root_excel_count':1,'input_archives_checked':True});(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(v,ensure_ascii=False))
