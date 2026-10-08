import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(here,'prepared.json'),'utf8'));
const original=JSON.parse(await fs.readFile(path.join(here,'input.json'),'utf8'));
const wb=Workbook.create();
const col=n=>{let s='';while(n){s=String.fromCharCode(65+(n-1)%26)+s;n=Math.floor((n-1)/26);}return s;};
const safe=v=>typeof v==='string'?v.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,''):v??null;
function base(name,rows,header,widths,tableName,rowHeight=65){
 const sh=wb.worksheets.add(name);const last=rows.length,w=Math.max(...rows.map(r=>r.length));
 sh.getRange(`A1:${col(w)}${last}`).values=rows.map(r=>Array.from({length:w},(_,i)=>safe(r[i])));
 sh.showGridLines=false;
 const range=sh.getRange(`A${header}:${col(w)}${last}`);
 range.format.font={name:'Microsoft YaHei',size:10,color:'#253449'};
 range.format.wrapText=true;range.format.verticalAlignment='top';range.format.rowHeight=rowHeight;
 widths.forEach((px,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidthPx=px);
 const head=sh.getRange(`A${header}:${col(w)}${header}`);
 head.format.fill='#33465C';head.format.font={name:'Microsoft YaHei',size:10,color:'#FFFFFF',bold:true};head.format.rowHeight=32;
 const t=sh.tables.add(`A${header}:${col(w)}${last}`,true,tableName);t.style='TableStyleLight1';t.showBandedRows=false;t.showFilterButton=true;
 sh.freezePanes.freezeRows(header);return sh;
}
const date=v=>v&&/^20\d\d-\d\d-\d\d$/.test(v)?new Date(v+'T00:00:00Z'):v||'待核';
const home=base('01申报总览',[
 ['申报状态','截止日期','依托单位·实验室','匹配方向','资助金额','公告'],
 ...d.projects.map(p=>[p.status,date(p.date),p.org+'·'+p.lab,p.topic,p.amount,'公告'])
],1,[150,112,360,290,220,66],'RetainedCalls',48);
home.getRange(`B2:B${d.projects.length+1}`).setNumberFormat('yyyy-mm-dd');
home.getRange(`B2:B${d.projects.length+1}`).format.horizontalAlignment='center';
home.getRange(`C2:C${d.projects.length+1}`).format.font.color='#205C91';
home.getRange(`F2:F${d.projects.length+1}`).format.font.color='#205C91';
home.getRange(`F2:F${d.projects.length+1}`).format.horizontalAlignment='center';
home.getRange(`A2:F${d.projects.length+1}`).format.verticalAlignment='center';
const statuses=home.getRange(`A2:A${d.projects.length+1}`);
statuses.conditionalFormats.add('containsText',{text:'已截止',format:{fill:'#F0F0F0',font:{color:'#737373'}}});
statuses.conditionalFormats.add('containsText',{text:'待核',format:{fill:'#FFF3DC',font:{color:'#8B641D'}}});
statuses.conditionalFormats.add('containsText',{text:'待确认',format:{fill:'#ECF2F8',font:{color:'#205C91'}}});
for(let i=0;i<d.projects.length;i++){
 const p=d.projects[i];
 if(i&&p.org_key!==d.projects[i-1].org_key)home.getRange(`A${i+2}:F${i+2}`).format.borders={top:{style:'thin',color:'#DCE2E8'}};
 const lines=Math.max(Math.ceil((p.org+'·'+p.lab).length/25),Math.ceil(p.topic.length/20),Math.ceil(p.amount.length/15));
 home.getRange(`A${i+2}:F${i+2}`).format.rowHeight=Math.max(48,Math.min(88,lines*17+9));
}
const detailRows=[['保留项目完整详情'],['核查日期：2026-10-08。适合承担、本人资格、受理状态分别判断；未公开及未取得条款均待核。'],[],[],[],d.detail_header,...d.projects.map(p=>p.details.map((v,i)=>i===4?date(v):v))];
const widths=[82,115,185,290,112,150,205,310,420,250,370,350,400,230,460,470,280,310,250,290,110,460,...Array(10).fill(180),360,300,450,150,300,150];
const detail=base('02项目完整详情',detailRows,6,widths,'RetainedDetails',120);
detail.getRange('A1').format.font={name:'Microsoft YaHei',size:14,bold:true,color:'#33465C'};
detail.getRange('A2').format.font={name:'Microsoft YaHei',size:10,color:'#667085'};
detail.getRange('A1:H1').merge();detail.getRange('A2:M2').merge();detail.getRange('A2:M2').format.wrapText=true;detail.getRange('A2:M2').format.rowHeight=32;
detail.getRange(`E7:E${d.projects.length+6}`).setNumberFormat('yyyy-mm-dd');
detail.freezePanes.freezeColumns(4);
const coverage=base('03机构检索覆盖',d.coverage,6,[110,210,310,160,350,350,350,150,250],'InstitutionCoverage',72);
coverage.freezePanes.freezeColumns(2);
const audit=base('04本轮信息核验日志',[d.log_header,...d.logs],1,[90,190,680,490,110,310],'EvidenceAudit',100);
audit.freezePanes.freezeColumns(2);
const ex=new Map(d.excluded.map(x=>[x[0],x[3]]));
const archive=base('90筛选前原始记录',[
 [...original.raw['02项目完整详情'][5],'本轮筛选结论','剔除理由'],
 ...original.rows.map(r=>[...r,ex.has(r[0])?'剔除':'保留',ex.get(r[0])??''])
],1,Array(34).fill(200),'OriginalRecords',85);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'01申报总览'!A1:F7",tableMaxRows:7,tableMaxCols:6,maxChars:2000})).ndjson);
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(here,'authored.xlsx'));
for(const [name,sheetName,range] of [
 ['homepage','01申报总览','A1:F15'],
 ['details','02项目完整详情','A6:H10'],
 ['coverage','03机构检索覆盖','A6:F10'],
 ['evidence','04本轮信息核验日志','A1:C5']
]){
 const png=await wb.render({sheetName,range,scale:1.2,format:'png'});
 await fs.writeFile(path.join(here,name+'.png'),new Uint8Array(await png.arrayBuffer()));
}
console.log(JSON.stringify(d.stats));
