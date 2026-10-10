import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,d=JSON.parse(await fs.readFile(path.join(H,'plan.json'),'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(d.source));
const sizes=[133,112,344,262,257,66];
const typed=r=>r.map((v,i)=>i===1 && typeof v==='string' && /^\d{4}-\d\d-\d\dT/.test(v)?new Date(v+'Z'):v);
const lineCount=(v,width)=>String(v??'').split('\n').reduce((n,s)=>n+Math.max(1,Math.ceil([...s].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0)/((width-16)/(10*2/3)))),0);
const heights=[];
for(const [name,entries,tname] of [['01申报总览',d.home,'CurrentCalls'],['03历史项目',d.history,'HistoricalCalls']]){
 const sh=w.worksheets.getItem(name),end=entries.length+1;
 if(name==='03历史项目'){
  for(let r=188;r<=end;r++)sh.getRange(`A${r}:F${r}`).copyFrom(sh.getRange('A2:F2'),'all');
  for(const t of sh.tables.items)t.delete();
  const t=sh.tables.add(`A1:F${end}`,true,tname);t.style='TableStyleLight1';t.showFilterButton=true;t.showBandedRows=false;
 }
 sh.getRange(`A2:F${end}`).values=entries.map(e=>typed(e.values));
 sh.getRange(`B2:B${end}`).setNumberFormat('yyyy-mm-dd');
 for(let i=0;i<entries.length;i++){
  const r=i+2,needed=Math.max(...entries[i].values.map((v,j)=>lineCount(j===5?'公告':v,sizes[j])))*13.5+12;
  const height=Math.max(48,Math.min(409,needed));sh.getRange(`A${r}:F${r}`).format.rowHeight=height;
  heights.push({sheet:name,row:r,needed,height});
 }
}
const detail=w.worksheets.getItem('02项目完整详情');
for(const p of d.patches)detail.getRange(p.col+p.row).values=[[p.value]];
w.recalculate();
await fs.writeFile(path.join(H,'inspection.json'),JSON.stringify(await w.inspect({kind:'table',range:'01申报总览!A1:F5',include:'values',tableMaxRows:5,tableMaxCols:6,maxChars:2000}),null,2));
await fs.writeFile(path.join(H,'row_heights.json'),JSON.stringify(heights,null,2));
await(await SpreadsheetFile.exportXlsx(w)).save(path.join(H,'authored.xlsx'));
console.log('Authored classifications, ordering and detail status cells; '+JSON.stringify(d.stats));
