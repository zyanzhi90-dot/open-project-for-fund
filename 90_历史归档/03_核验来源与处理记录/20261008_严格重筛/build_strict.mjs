import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const H=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(H,'prepared_strict.json'),'utf8'));
const wb=Workbook.create();const maps={};const heights=[];
const col=n=>{let s='';while(n){s=String.fromCharCode(65+(n-1)%26)+s;n=Math.floor((n-1)/26);}return s;};
const clean=v=>typeof v==='string'?v.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,''):v??null;
const dt=v=>v&&/^20\d\d-\d\d-\d\d$/.test(v)?new Date(v+'T00:00:00Z'):v||'未取得';
function lines(v,width,font=10){return String(v??'').split('\n').reduce((n,s)=>n+Math.max(1,Math.ceil([...s].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0)/Math.max(4,(width-16)/(font*2/3)))),0);}
function base(name,rows,header,widths,tableName,defaultHeight=70,dynamic=true,font=10){
 const sh=wb.worksheets.add(name),end=rows.length,w=widths.length;
 sh.getRange(`A1:${col(w)}${end}`).values=rows.map(r=>Array.from({length:w},(_,i)=>clean(r[i])));
 sh.showGridLines=false;const all=sh.getRange(`A1:${col(w)}${end}`);
 all.format.font={name:'Microsoft YaHei',size:font,color:'#253449'};
 all.format.wrapText=true;all.format.verticalAlignment='top';all.format.rowHeight=defaultHeight;
 widths.forEach((x,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${end}`).format.columnWidthPx=x);
 const head=sh.getRange(`A${header}:${col(w)}${header}`);head.format.fill='#33465C';head.format.font={name:'Microsoft YaHei',size:10,color:'#FFFFFF',bold:true};head.format.rowHeight=30;
 if(end>header){const t=sh.tables.add(`A${header}:${col(w)}${end}`,true,tableName);t.style='TableStyleLight1';t.showBandedRows=false;t.showFilterButton=true;}
 sh.freezePanes.freezeRows(header);
 if(dynamic)for(let r=header+1;r<=end;r++){
  const needed=Math.max(...rows[r-1].slice(0,w).map((v,i)=>lines(v,widths[i],font)))*font*1.35+12;
  const h=Math.max(48,Math.min(409,needed));sh.getRange(`A${r}:${col(w)}${r}`).format.rowHeight=h;
  heights.push({sheet:name,row:r,required:needed,actual:h,clippedEstimate:needed>409});
 }
 return sh;
}
const headings=['申报状态','截止日期','依托单位·实验室','公告研究方向','资助金额','公告'];
const pm=new Map(d.projects.map(p=>[p.id,p]));
// Preserve the existing six-column widths and visual vocabulary.
function list(name,ids,tableName,extra=false){
 const rows=[extra?[...headings,'具体待核事项','联系入口']:headings];maps[name]=[];
 for(const id of ids){const p=pm.get(id);rows.push([p.status,dt(p.date),p.org+'·'+p.lab,p.topic,p.amount,p.kind==='线索'?'线索':'公告',...(extra?[p.gaps,p.contact]:[])]);maps[name].push({id,row:rows.length});}
 const sh=base(name,rows,1,extra?[133,112,344,262,257,66,660,290]:[133,112,344,262,257,66],tableName);
 for(const x of maps[name]){
  const r=x.row,p=pm.get(x.id);sh.getRange(`B${r}`).setNumberFormat('yyyy-mm-dd');
  sh.getRange(`B${r}`).format.horizontalAlignment='center';sh.getRange(`F${r}`).format.horizontalAlignment='center';
  sh.getRange(`C${r}`).format.font.color='#205C91';sh.getRange(`F${r}`).format.font.color='#205C91';
  sh.getRange(`A${r}`).format.fill=p.status==='已截止'?'#F0F0F0':name==='01申报总览'?'#FFF3DC':'#F4F1E9';
  sh.getRange(`A${r}:F${r}`).format.verticalAlignment='center';
 }
 return sh;
}
list('01申报总览',d.groups[0].ids,'CurrentCalls');
const widths=[95,190,190,330,155,115,115,115,300,270,390,390,410,230,460,420,500,380,490,300,310,220,250,460,180,260,110];
const detail=base('02项目完整详情',[d.detail_header,...d.projects.map(p=>p.details.map((v,i)=>i===6?dt(v):v))],1,widths,'CompleteDetails',115,true,10);
detail.freezePanes.freezeColumns(4);detail.getRange(`G2:G${d.projects.length+1}`).setNumberFormat('yyyy-mm-dd');
const cov=base('03机构检索覆盖',d.coverage,6,[120,210,140,260,410,390,320,300,390],'InstitutionCoverage',100);
cov.freezePanes.freezeColumns(2);
for(const r of [1,2]){cov.getRange(`A${r}:I${r}`).merge();cov.getRange(`A${r}:I${r}`).format.rowHeight=r===1?30:45;}
for(const r of [3,4,5])cov.getRange(`A${r}:I${r}`).format.rowHeight=10;
const log=base('04本轮信息核验日志',[d.log_header,...d.logs],1,[100,170,680,380,120,180,140,190],'EvidenceLog',95,true);
log.freezePanes.freezeColumns(2);
base('05剔除记录',[['原项目编号','依托单位','实验室/项目','状态','剔除依据','官方来源','核查日期'],...d.excluded],1,[100,220,330,170,610,350,120],'ExcludedRecords',90,true);
list('06历史项目',d.groups[1].ids,'HistoricalCalls');
list('07待核项目',d.groups[2].ids,'PendingCalls',true);
list('08其他资助',d.groups[3].ids,'OtherFunding',true);
base('90筛选前原始记录',[d.archive_header,...d.archive],1,Array(d.archive_header.length).fill(190),'Original199',80,false);
const baseRows=[['原工作表','原行号','原始记录1','原始记录2','原始记录3','原始记录4']];
for(const [name,rows] of Object.entries(d.base_raw))for(let i=0;i<rows.length;i++){const s=JSON.stringify(rows[i]);baseRows.push([name,i+1,...Array.from({length:4},(_,j)=>s.slice(j*28000,(j+1)*28000))]);}
base('91输入版本留档',baseRows,1,[210,100,400,400,400,400],'PriorInputRows',65,false);
wb.recalculate();
const inspected=await wb.inspect({kind:'table',sheetId:'01申报总览',range:'A1:F13',include:'id,name,range',maxChars:2000});
await fs.writeFile(path.join(H,'artifact_inspection.json'),JSON.stringify(inspected,null,2),'utf8');
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(H,'authored_strict.xlsx'));
d.list_maps=maps;await fs.writeFile(path.join(H,'prepared_strict.json'),JSON.stringify(d,null,2),'utf8');
await fs.writeFile(path.join(H,'row_height_audit.json'),JSON.stringify(heights,null,2),'utf8');
console.log(JSON.stringify({export:'authored_strict.xlsx',sheets:10,rows:d.stats,estimatedClipped:heights.filter(x=>x.clippedEstimate).map(x=>({sheet:x.sheet,row:x.row,required:x.required}))}));
