import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile, FileBlob } from '@oai/artifact-tool';
if(process.argv.includes('--audit-only')) {
 const root=process.cwd();
 const originalName=(await fs.readdir(root)).find(x=>x.endsWith('.xlsx'));
 const book=await SpreadsheetFile.importXlsx(await FileBlob.load(root+'/'+originalName));
 const audited=JSON.parse(await fs.readFile(root+'/tmp/rebuild/audit_all/audited_original_layout.json','utf8'));
 const address=n=>{let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
 const safe=v=>typeof v==='string'?v.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,''):v;
 const linkList=[];
 for(const [name,rows] of Object.entries(audited)) {
  const fresh=name==='04本轮信息核验日志';
  const sh=fresh?book.worksheets.add(name):book.worksheets.getItem(name);
  const width=Math.max(...rows.map(r=>r.length));
  const matrix=rows.map(r=>Array.from({length:width},(_,i)=>safe(r[i]??null)));
  const first=fresh?1:7;
  // Retain source workbook order, formulas, column layout, headers and existing styling.
  if(!fresh){
   sh.getRange(`A7:${address(width)}${rows.length}`).values=matrix.slice(6);
   if(name==='01申报总览'){
    sh.getRange('A2').values=[[matrix[1][0]]];sh.getRange('J3').values=[[matrix[2][9]]];
   }
  }else{
   sh.getRange(`A1:F${rows.length}`).values=matrix;
   sh.getRange(`A1:F${rows.length}`).format.font={name:'Microsoft YaHei',size:10};
   sh.getRange(`A1:F${rows.length}`).format.wrapText=true;
   sh.getRange(`A1:F${rows.length}`).format.verticalAlignment='top';
   sh.getRange(`A1:F${rows.length}`).format.rowHeight=54;
   sh.getRange('A1:F1').format.fill='#33465C';
   sh.getRange('A1:F1').format.font.color='#FFFFFF';
   sh.getRange('A1:F1').format.font.bold=true;
   [100,170,390,450,340,110].forEach((px,i)=>sh.getRange(`${address(i+1)}1:${address(i+1)}${rows.length}`).format.columnWidthPx=px);
   sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(2);
   sh.tables.add(`A1:F${rows.length}`,true,'AuditEvidence').showFilterButton=true;
  }
  const uriColumns=fresh?[4]:name==='01申报总览'?[9]:name==='02项目完整详情'?[16,17]:[];
  for(let i=first-1;i<rows.length;i++)for(const c of uriColumns){
   const u=String(matrix[i][c]??'').match(/https?:\/\/[^\s]+/)?.[0];
   if(u){linkList.push({sheet:name,cell:address(c+1)+(i+1),url:u});sh.getRange(address(c+1)+(i+1)).format.font.color='#205C91';}
  }
 }
 const out=root+'/outputs/20261008_robot_fund_audit';await fs.mkdir(out,{recursive:true});
 const path=out+'/全国机器人开放课题_个人申报台账_信息核验版_20261008.xlsx';
 await (await SpreadsheetFile.exportXlsx(book)).save(path);
 await fs.writeFile(root+'/tmp/rebuild/audit_all/final_links.json',JSON.stringify(linkList));
 const png=await book.render({sheetName:'01申报总览',range:'A5:H10',scale:1,format:'png'});
 await fs.writeFile(root+'/tmp/rebuild/audit_all/final_preview.png',new Uint8Array(await png.arrayBuffer()));
 console.log(JSON.stringify({path,sheets:Object.keys(audited),links:linkList.length}));
 process.exit(0);
}
const wb=Workbook.create();
if(process.argv.includes('--api-help')){
 console.log(wb.help('hyperlink',{search:'hyperlink|HYPERLINK',include:'index,examples,notes',maxChars:3400}).ndjson);
 process.exit(0);
}
const data=JSON.parse(await fs.readFile(new URL('./normalized.json',import.meta.url),'utf8'));
const outDir=process.cwd()+'/outputs/20261008_robot_fund_rebuild';
await fs.mkdir(outDir,{recursive:true});
const col=n=>{let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const names=['01 重点申报','02 地域项目总览','03 项目完整详情','04 机构检索进度','90 原始申报总览','91 原始完整详情','92 原始机构覆盖'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const detailRows={};
const nativeLinks=[];
const palette={header:'#33465C',ink:'#253449',blue:'#205C91',A:'#E8F2EA',B:'#EEF3F8',C:'#F2F2F2',amber:'#FFF1D6',muted:'#667085'};
function formatBase(sheet,matrix,widths,title){
 const width=matrix[0].length,last=matrix.length+4;
 sheet.showGridLines=false;
 sheet.getRange(`A1:${col(width)}${last}`).format.font={name:'Microsoft YaHei',size:10,color:palette.ink};
 sheet.getRange('A2').values=[[title]];
 sheet.getRange('A2').format.font={name:'Microsoft YaHei',size:14,bold:true,color:palette.ink};
 sheet.getRange(`A2:${col(width)}2`).format.rowHeight=27;
 sheet.getRange(`A4:${col(width)}${last-1}`).values=matrix;
 sheet.getRange(`A4:${col(width)}4`).format.fill=palette.header;
 sheet.getRange(`A4:${col(width)}4`).format.font={name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'};
 sheet.getRange(`A4:${col(width)}4`).format.rowHeight=30;
 sheet.getRange(`A4:${col(width)}4`).format.horizontalAlignment='center';
 sheet.getRange(`A4:${col(width)}${last-1}`).format.verticalAlignment='center';
 sheet.getRange(`A4:${col(width)}${last-1}`).format.wrapText=true;
 sheet.getRange(`A5:${col(width)}${last-1}`).format.rowHeight=54;
 widths.forEach((px,i)=>sheet.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidthPx=px);
 sheet.freezePanes.freezeRows(4);
 sheet.freezePanes.freezeColumns(Math.min(width,2));
 const table=sheet.tables.add(`A4:${col(width)}${last-1}`,true,'T'+names.indexOf(sheet.name));
 table.style='TableStyleLight1';
 table.showFilterButton=true;
 return last-1;
}
function link(sheet,address,url,label){
 if(!url)return;
 sheet.getRange(address).values=[[label]];
 nativeLinks.push({sheet:sheet.name,cell:address,url});
 sheet.getRange(address).format.font.color=palette.blue;
}
function dateValue(d){return d?new Date(d+'T00:00:00Z'):null;}
function dateFmt(sheet,colLetter,last){sheet.getRange(`${colLetter}5:${colLetter}${last}`).setNumberFormat('yyyy-mm-dd');}
const fields=[
 ['机构与项目','依托机构','org'],['机构与项目','实验室/项目名称','lab'],['机构与项目','项目年度/批次','year'],['机构与项目','项目类别/计数口径','type'],['机构与项目','联合公告组ID','plan_group'],
 ['筛选判断','地域/关系网络','region'],['筛选判断','科研匹配等级','grade'],['筛选判断','重新评估依据/场景边界','fit'],['筛选判断','面上申请书依据','basis'],['筛选判断','申报状态','status'],['筛选判断','本人申报资格确认程度','eligibility'],['筛选判断','首页纳入/排除依据','home_reason'],
 ['申请规则','官方截止日期','date'],['申请规则','匹配研究方向','directions'],['申请规则','资助金额/类型','amount'],['申请规则','申请人资格与限项','qualification'],['申请规则','固定人员/实质合作要求','collaboration'],['申请规则','经费外拨/使用范围','funds'],['申请规则','执行周期','period'],['申请规则','结题成果与署名','outputs'],['申请规则','知识产权归属','ip'],['申请规则','材料/签章/提交方式','materials'],
 ['来源与核验','正式公告/机制网址','url'],['来源与核验','原附件/第二官网网址','second'],['来源与核验','正文与字段核查程度','source_status'],['来源与核验','附件全文核查程度','attachment_status'],['来源与核验','仍缺的关键核验信息','missing'],['来源与核验','本轮核查日期','check_date'],['历史保留','原始资格/来源摘要','raw_qualification'],['历史保留','来源分支与旧编号','lineage'],['历史保留','去重/年度/归属说明','raw_note'],['历史保留','本轮修复记录','changes']
];
const details=[['项目编号','机构/实验室','信息分组','字段','核实内容（未核实者明示）','证据/核查程度','官方来源']];
const extraAttachmentLinks=[];
for(const p of data.projects){
 detailRows[p.id]=details.length+4;
 for(const [group,label,key] of fields){
  let value=p[key];if(key==='changes')value=value.length?value.join('\n'):'等级与状态均重新评估；原始字段保留';
  if(key==='lineage')value=[p.lineage,p.old_id].filter(Boolean).join('；');
  if(key==='date')value=value?dateValue(value):p.id==='M056'?'滚动机制未设公开固定截止；当期须确认':'未核实/不适用，详申报状态';
  if(key==='check_date')value=dateValue(value);
  if(value===null||value===undefined||value==='')value='原表未记录/待核';
  let proof=p.field_verified.includes(key)?'已核官网正文/所读附件':key==='date'?(p.date_verified?'已核官网截止':'旧表日期/未确认，禁止视为当前受理'):key==='fit'||key==='grade'||key==='basis'?'本轮独立评估（科研匹配≠资格）':group==='历史保留'?'保留原记录/本轮修复说明':key==='check_date'?'本輪查閱日期，非所有字段均确认':'旧表/平台资料参考；未做全字段确认';
  details.push([p.id,p.org+'\n'+p.lab,group,label,value,proof,p.url||'']);
 }
 try{
  const src=JSON.parse(await fs.readFile(new URL('./official/'+p.id+'.json',import.meta.url),'utf8'));
  for(const a of src.links||[]){
   if(/\.docx?|\.pdf|\.zip|\.rar|DownloadAttach/i.test(a.url+' '+a.text)&& !/创新基金|结题报告|中期报告|年度进展|汇总/.test(a.text)){
    extraAttachmentLinks.push({row:details.length+4,url:a.url,label:a.text});
    details.push([p.id,p.org+'\n'+p.lab,'来源与核验','官方附件：'+a.text,a.url,'逐附件状态见附件全文核查字段；链接存在≠内容读完',a.url]);
   }
  }
 }catch{}
}
const ds=sheets[names[2]];
const dl=formatBase(ds,details,[94,260,110,185,560,250,125],'项目完整详情｜按编号纵向查阅');
ds.getRange('A3').values=[['点击首页编号直达项目；可按项目编号或字段筛选。金额、署名、经费、材料分别列出。']];
ds.getRange(`A5:G${dl}`).format.rowHeight=48;
for(let i=1;i<details.length;i++){
 const row=i+4,key=details[i][3],txt=String(details[i][4]??'');
 const lines=Math.max(...details[i].slice(1,6).map((v,c)=>Math.ceil(String(v??'').length/[20,8,14,42,19][c])));
 ds.getRange(`A${row}:G${row}`).format.rowHeight=Math.min(280,Math.max(48,lines*16+10));
 if(details[i][4] instanceof Date)ds.getRange(`E${row}`).setNumberFormat('yyyy-mm-dd');
 if(key==='依托机构'){ds.getRange(`A${row}:G${row}`).format.fill='#E8EDF3';ds.getRange(`A${row}:D${row}`).format.font.bold=true;}
 if(key==='科研匹配等级')ds.getRange(`E${row}`).format.fill=palette[details[i][4]];
 if(key==='正式公告/机制网址'||key==='原附件/第二官网网址'){
  const u=details[i][4];if(typeof u==='string'&&/^https?:/.test(u))link(ds,`E${row}`,u,u);
 }
 link(ds,`G${row}`,details[i][6],'官方来源');
}
for(const a of extraAttachmentLinks)link(ds,`E${a.row}`,a.url,a.url);

const short={
 M056:['柔性医疗机器人、活体组织表征、机器人控制/感知/学习','博士或高级；须实验室/合作课题组成员；重点原则上博导。先咨询当期指南与金额'],
 M078:['医疗机器人力触觉反馈、柔性控制、人机协同','博士或中级以上；必须固定合作者；≤40为鼓励。署第一/通讯作者单位，不限制单位排序'],
 M066:['混杂接触模型、非标准最优控制、多模态融合','博士或中级；一般2篇二区以上SCI；第一或唯一通讯须山科人员；排除开源期刊。重点另有奖励/重点项目'],
 M035:['柔性织物双臂操作、高自由度机器人遥操作','博士或副高；必须≥1固定合作者；10-08“日前”当日受理须确认；资金未公开'],
 M068:['点云/多模态感知、机械臂规划；无人系统场景','博士或高级；一般1篇二区/CCF B，重点一区/CCF A；实验室第一单位、固定作者；今日受理须确认'],
 M106:['医学信息处理、机器视觉/多物理场成像','国内中级以上；无博士的中级需2高级推荐；不外拨；二区1篇或三区2篇，固定作者；今日须确认'],
 M160:['非线性鲁棒/最优控制；工业装备迁移','必须固定合作者；同年/在研各1项；可外拨或报销；未设公开最低篇数；成果共有'],
 M017:['加工力—表面质量建模；制造测量迁移','非天津大学人员；必须唯一固定联系人+推荐信；10-18电子，10-25纸质到；国内可分期外拨'],
 M029:['机器人技能学习、柔顺控制；智能制造装备','在职博士或副高；否则2副高推荐；固定成员不能申请；研究2年；金额未公开'],
 M161:['动力学/机电液控制；传动制造装备','原则博士，否则1高级推荐；固定人员参与；≥2篇ESI工程学；实验室第一或第二单位'],
 M142:['柔性对象/纺织具身智能；纺织场景','校外博士或高级，否则2正高推荐；≥1固定成员；不外拨；≥1篇EI期刊，实验室第一单位']
};
const h=[['地域','匹配等级','申报状态','实验室名称 / 编号→详情','截止日期','匹配研究方向','资助金额','关键申报条件','官方公告']];
const homeAmounts={M017:'4—8万元/项',M066:'一般2万元\n重点5万元',M160:'一般3万元/项'};
for(const p of data.home){const s=short[p.id];h.push([p.region,p.grade+'类',p.status,p.org+'\n'+p.lab+'\n'+p.id,dateValue(p.date),s[0],homeAmounts[p.id]||p.amount,s[1],'官方公告']);}
const hs=sheets[names[0]];const hl=formatBase(hs,h,[138,68,174,290,106,215,143,340,95],'重点申报｜2026-10-08');
hs.freezePanes.freezeColumns(1);hs.getRange(`A5:I${hl}`).format.rowHeight=99;dateFmt(hs,'E',hl);
for(let i=0;i<data.home.length;i++){const p=data.home[i],r=i+5;hs.getRange(`B${r}`).format.fill=palette[p.grade];hs.getRange(`B${r}`).format.font.bold=true;link(hs,`D${r}`,'#\''+names[2]+'\'!A'+detailRows[p.id],h[i+1][3]);link(hs,`I${r}`,p.url,'官方公告');if(p.date===data.date)hs.getRange(`C${r}:E${r}`).format.fill=palette.amber;}
hs.tabColor=palette.header;

const overview=[['地域','编号→详情','匹配等级','申报状态','依托机构/实验室','年度/批次','截止日期','资助金额','匹配方向及场景边界','首页/储备理由','官方来源']];
for(const p of data.projects)overview.push([p.region,p.id,p.grade+'类',p.status,p.org+'\n'+p.lab,p.year,dateValue(p.date),p.amount,p.fit,p.home_reason,'官方来源']);
const os=sheets[names[1]],ol=formatBase(os,overview,[150,100,70,178,285,140,106,155,385,220,100],'地域项目总览｜全量记录与年度储备');dateFmt(os,'G',ol);
os.getRange('A3').values=[['199条原始记录全部保留；同一联合公告的多个平台用计划组ID关联，不能机械计为独立资金池。']];
for(let i=0;i<data.projects.length;i++){const p=data.projects[i],r=i+5;os.getRange(`C${r}`).format.fill=palette[p.grade];os.getRange(`A${r}:K${r}`).format.rowHeight=88;link(os,`B${r}`,'#\''+names[2]+'\'!A'+detailRows[p.id],p.id);link(os,`K${r}`,p.url,'官方来源');if(p.date===data.date)os.getRange(`D${r}`).format.fill=palette.amber;}

const cover=[['地域/优先级','机构（别名归并）','检索进度','本轮查到的结果','已建项目编号','仍需核实的内容','官网证据','核查日期','覆盖边界/原检索信息']];
for(const c of data.coverage)cover.push([c.region,c.name+(c.original_count>1?'\n原条目：'+c.aliases:''),c.status,c.outcome,c.ids,c.pending,c.url,dateValue(c.date),c.scope+'\n原证据：'+c.old_evidence+'\n已执行查询：'+c.queries]);
const cs=sheets[names[3]],cl=formatBase(cs,cover,[160,235,170,345,175,360,130,110,300],'机构检索进度｜144个原条目，归并为139个主体');dateFmt(cs,'H',cl);
cs.getRange('A3').values=[['本轮名单内定向补查已执行；“部分已查/仅平台/待查”分别保留，不能据未检出断言无开放基金。']];
cs.getRange(`A5:I${cl}`).format.rowHeight=105;
for(let i=0;i<data.coverage.length;i++){const c=data.coverage[i],r=i+5;link(cs,`G${r}`,c.url,c.url?'官网证据':'未取得');if(c.status.startsWith('待查'))cs.getRange(`C${r}`).format.fill=palette.amber;else if(c.status.startsWith('已完成'))cs.getRange(`C${r}`).format.fill=palette.A;}

const rawNames=['01申报总览','02项目完整详情','03机构检索覆盖'];
for(let k=0;k<3;k++){
 const sheet=sheets[names[k+4]],m=data.raw[rawNames[k]],n=m[0].length;
 sheet.getRange(`A1:${col(n)}${m.length}`).values=m.map(row=>row.map(v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v));
 sheet.getRange(`A1:${col(n)}${m.length}`).format.font={name:'Microsoft YaHei',size:10,color:palette.muted};
 sheet.getRange(`A1:${col(n)}${m.length}`).format.columnWidthPx=140;
 sheet.getRange(`A1:${col(n)}${m.length}`).format.rowHeight=26;
 sheet.getRange(`A6:${col(n)}6`).format.fill='#E8EDF3';sheet.getRange(`A6:${col(n)}6`).format.font.bold=true;
 sheet.freezePanes.freezeRows(6);sheet.freezePanes.freezeColumns(1);sheet.showGridLines=false;
 sheet.tables.add(`A6:${col(n)}${m.length}`,true,'Raw'+k).showFilterButton=true;
}
wb.recalculate();
console.log((await wb.inspect({kind:'sheet,table',maxChars:3500,tableMaxRows:2,tableMaxCols:4})).ndjson);
console.log((await wb.inspect({kind:'region',sheetId:names[0],range:'A4:I8',maxChars:2000,tableMaxCellChars:75})).ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(outDir+'/全国机器人开放课题_个人申报台账_重构核验版_20261008.xlsx');
for(const [name,range] of [[names[0],'A1:I9'],[names[1],'A1:K9'],[names[2],'A1:G12'],[names[3],'A1:I9'],[names[4],'A1:F9'],[names[5],'A1:F9'],[names[6],'A1:F9']]){
 const b=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(outDir+'/'+name.slice(0,2)+'_preview.png',new Uint8Array(await b.arrayBuffer()));
}
await fs.writeFile(new URL('./detail_row_map.json',import.meta.url),JSON.stringify(detailRows));
await fs.writeFile(new URL('./native_links.json',import.meta.url),JSON.stringify(nativeLinks));
console.log(JSON.stringify({output:outDir,counts:data.counts,home:data.home.map(p=>p.id),detailRows:details.length-1,coverage:data.coverage.length}));
