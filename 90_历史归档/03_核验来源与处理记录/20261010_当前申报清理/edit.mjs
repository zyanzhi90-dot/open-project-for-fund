import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,d=JSON.parse(await fs.readFile(path.join(H,'plan.json'),'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(d.source));
await fs.writeFile(path.join(H,'before_other.png'),new Uint8Array(await (await w.render({sheetName:'04其他资助',range:'A1:H3',scale:1,format:'png'})).arrayBuffer()));
const sizes6=[133,112,344,262,257,66],sizes8=[133,112,344,262,257,66,420,300];
const typed=r=>r.map((v,i)=>i===1&&typeof v==='string'&&/^\d{4}-\d\d-\d\dT/.test(v)?new Date(v+'Z'):v);
const lines=(v,width)=>String(v??'').split('\n').reduce((n,s)=>n+Math.max(1,Math.ceil([...s].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0)/((width-16)/(10*2/3)))),0);
for(const [name,entries,widths] of [['03历史项目',d.history,sizes6],['04其他资助',d.others,sizes8]]){
 const sh=w.worksheets.getItem(name),end=entries.length+1,last=widths.length===6?'F':'H';
 for(const t of sh.tables.items)t.delete();
 sh.getRange(`A2:${last}${Math.max(end,name==='04其他资助'?23:286)}`).clear('contents');
 for(let n=2;n<=end;n++)sh.getRange(`A${n}:${last}${n}`).copyFrom(sh.getRange(`A2:${last}2`),'all');
 sh.getRange(`A2:${last}${end}`).values=entries.map(e=>typed(e.values));
 sh.getRange(`B2:B${end}`).setNumberFormat('yyyy-mm-dd');
 if(name==='04其他资助')sh.getRange('G1').values=[['申报主体及条件']];
 const t=sh.tables.add(`A1:${last}${end}`,true,name==='03历史项目'?'HistoricalCalls':'OtherFunding');t.style='TableStyleLight1';t.showFilterButton=true;t.showBandedRows=false;
 for(let i=0;i<entries.length;i++)sh.getRange(`A${i+2}:${last}${i+2}`).format.rowHeight=Math.min(409,Math.max(48,Math.max(...entries[i].values.map((v,j)=>lines(j===5?'公告':v,widths[j])))*13.5+12));
}
for(const p of d.patches)w.worksheets.getItem('02项目完整详情').getRange(p.col+p.row).values=[[p.value]];
w.recalculate();
await fs.writeFile(path.join(H,'inspection.json'),JSON.stringify(await w.inspect({kind:'table',range:'04其他资助!A1:H3',include:'values',tableMaxRows:3,tableMaxCols:8,maxChars:3000}),null,2));
await(await SpreadsheetFile.exportXlsx(w)).save(path.join(H,'authored.xlsx'));
console.log('Authored current other funding and historical classification.');
