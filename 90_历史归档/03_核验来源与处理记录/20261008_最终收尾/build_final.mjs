import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const H=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(H,'prepared_final.json'),'utf8'));
const wb=Workbook.create();
const col=n=>{let s='';while(n){s=String.fromCharCode(65+(n-1)%26)+s;n=Math.floor((n-1)/26);}return s;};
const clean=v=>typeof v==='string'?v.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,''):v??null;
const date=v=>v&&/^20\d\d-\d\d-\d\d$/.test(v)?new Date(v+'T00:00:00Z'):v||'未取得';
function base(name,rows,header,widths,tableName,rowHeight=70,table=true){
 const sh=wb.worksheets.add(name),last=rows.length,w=Math.max(...rows.map(r=>r.length));
 sh.getRange(`A1:${col(w)}${last}`).values=rows.map(r=>Array.from({length:w},(_,i)=>clean(r[i])));
 sh.showGridLines=false;
 const r=sh.getRange(`A1:${col(w)}${last}`);r.format.font={name:'Microsoft YaHei',size:10,color:'#253449'};r.format.wrapText=true;r.format.verticalAlignment='top';r.format.rowHeight=rowHeight;
 widths.forEach((px,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidthPx=px);
 if(table)addtable(sh,header,last,w,tableName);
 sh.freezePanes.freezeRows(header);return sh;
}
function addtable(sh,start,end,w,name){
 if(end<=start)return;
 const h=sh.getRange(`A${start}:${col(w)}${start}`);h.format.fill='#33465C';h.format.font={name:'Microsoft YaHei',size:10,color:'#FFFFFF',bold:true};h.format.rowHeight=30;
 const t=sh.tables.add(`A${start}:${col(w)}${end}`,true,name);t.style='TableStyleLight1';t.showBandedRows=false;t.showFilterButton=true;
}
const headings=['申报状态','截止日期','依托单位·实验室','匹配方向','资助金额','公告'];
const map=new Map(d.projects.map(p=>[p.id,p])),homeRows=[],homeMap=[],sections=[];
for(let g=0;g<d.groups.length;g++){
 const group=d.groups[g];
 if(g){homeRows.push([group.name,null,null,null,null,null]);sections.push(homeRows.length);}
 const start=homeRows.length+1;homeRows.push(headings);
 for(const id of group.ids){const p=map.get(id);homeRows.push([p.status,date(p.date),p.org+'·'+p.lab,p.topic,p.amount,p.kind==='线索'?'线索':'公告']);homeMap.push({row:homeRows.length,id});}
 group.start=start;group.end=homeRows.length;
}
const home=base('01申报总览',homeRows,1,[133,112,344,262,257,66],'',62,false);
for(let g=0;g<d.groups.length;g++){const x=d.groups[g];addtable(home,x.start,x.end,6,'Calls'+g);}
for(const r of sections){home.getRange(`A${r}:F${r}`).merge();home.getRange(`A${r}:F${r}`).format.fill='#EAF0F5';home.getRange(`A${r}`).format.font.bold=true;home.getRange(`A${r}:F${r}`).format.rowHeight=30;}
for(const x of homeMap){
 const p=map.get(x.id),r=x.row;home.getRange(`B${r}`).setNumberFormat('yyyy-mm-dd');
 home.getRange(`B${r}`).format.horizontalAlignment='center';home.getRange(`C${r}`).format.font.color='#205C91';home.getRange(`F${r}`).format.font.color='#205C91';home.getRange(`F${r}`).format.horizontalAlignment='center';
 home.getRange(`A${r}:F${r}`).format.verticalAlignment='center';
 const lines=Math.max(Math.ceil((p.org+'·'+p.lab).length/24),Math.ceil(p.topic.length/19),Math.ceil(p.amount.length/17));home.getRange(`A${r}:F${r}`).format.rowHeight=Math.max(48,Math.min(110,lines*17+10));
 home.getRange(`A${r}`).format.fill=p.status==='已截止'?'#F0F0F0':p.status==='受理中·条件待核'?'#FFF3DC':p.status==='截止待确认'?'#E8F0F8':'#F4F1E9';
}
const widths=[95,190,190,330,140,115,115,115,260,270,390,390,410,230,460,420,500,380,490,300,310,165,250,360,180,260,110];
const detail=base('02项目完整详情',[d.detail_header,...d.projects.map(p=>p.details.map((v,i)=>i===6?date(v):v))],1,widths,'CompleteDetails',115);detail.freezePanes.freezeColumns(4);detail.getRange(`G2:G${d.projects.length+1}`).setNumberFormat('yyyy-mm-dd');
const cov=base('03机构检索覆盖',d.coverage,6,[120,210,140,260,410,390,210,300,390],'InstitutionCoverage',100);cov.freezePanes.freezeColumns(2);
const log=base('04本轮信息核验日志',[d.log_header,...d.logs],1,[100,170,680,310,120,180,140,170],'EvidenceLog',95);log.freezePanes.freezeColumns(2);
base('05剔除记录',[['原项目编号','依托单位','实验室/项目','状态','剔除依据','官方来源','核查日期'],...d.excluded],1,[100,220,330,150,610,350,120],'ExcludedRecords',90);
base('90筛选前原始记录',[d.archive_header,...d.archive],1,Array(d.archive_header.length).fill(190),'Original199',80);
const baseRows=[['原工作表','原行号','原始记录1','原始记录2','原始记录3','原始记录4']];
for(const [name,rows] of Object.entries(d.base_raw))for(let i=0;i<rows.length;i++){
 const s=JSON.stringify(rows[i]);if(s.length>112000)throw new Error('Archive length exceeds capacity');
 baseRows.push([name,i+1,...Array.from({length:4},(_,j)=>s.slice(j*28000,(j+1)*28000))]);
}
base('91输入版本留档',baseRows,1,[210,100,400,400,400,400],'PriorInputRows',65);
d.home_map=homeMap;d.sections=sections;
await fs.writeFile(path.join(H,'prepared_final.json'),JSON.stringify(d,null,2),'utf8');
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(H,'authored_final.xlsx'));
const b=await wb.render({sheetName:'01申报总览',range:'A1:F9',scale:1.2,format:'png'});await fs.writeFile(path.join(H,'final_home.png'),new Uint8Array(await b.arrayBuffer()));
console.log('Authored '+d.projects.length+' independent rows; six-column homepage; original input archived.');
