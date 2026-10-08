import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=process.cwd();
const data=JSON.parse(await fs.readFile(root+'/tmp/display/data.json','utf8'));
const book=Workbook.create();
const sh=book.worksheets.add(data.sheetnames[0]);
const rows=[data.header,...data.records.map(x=>x.row.map((v,i)=>i===1&&/^\d{4}-\d{2}-\d{2}$/.test(v)?new Date(v+'T00:00:00Z'):i===1?'待核':v))];
const last=rows.length;
sh.getRange(`A1:F${last}`).values=rows;
sh.showGridLines=false;
sh.getRange(`A1:F${last}`).format.font={name:'Microsoft YaHei',size:10,color:'#253449'};
sh.getRange(`A1:F${last}`).format.verticalAlignment='center';
sh.getRange(`A1:F${last}`).format.wrapText=true;
sh.getRange(`A1:F${last}`).format.rowHeight=45;
sh.getRange('A1:F1').format.fill='#33465C';
sh.getRange('A1:F1').format.font={name:'Microsoft YaHei',size:10,color:'#FFFFFF',bold:true};
sh.getRange('A1:F1').format.rowHeight=29;
sh.getRange('A1:F1').format.horizontalAlignment='center';
const widths=[145,112,365,320,260,64];
widths.forEach((px,i)=>sh.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${last}`).format.columnWidthPx=px);
sh.getRange(`B2:B${last}`).setNumberFormat('yyyy-mm-dd');
sh.getRange(`B2:B${last}`).format.horizontalAlignment='center';
sh.getRange(`C2:C${last}`).format.font.color='#205C91';
sh.getRange(`F2:F${last}`).format.font.color='#205C91';
sh.getRange(`F2:F${last}`).format.horizontalAlignment='center';
const table=sh.tables.add(`A1:F${last}`,true,'OpenCallsOverview');
table.style='TableStyleLight1';
table.showBandedRows=false;
table.showFilterButton=true;
sh.freezePanes.freezeRows(1);
const statuses=sh.getRange(`A2:A${last}`);
statuses.conditionalFormats.add('containsText',{text:'已截止',format:{fill:'#F0F0F0',font:{color:'#737373'}}});
statuses.conditionalFormats.add('containsText',{text:'待核',format:{fill:'#FFF3DC',font:{color:'#8B641D'}}});
statuses.conditionalFormats.add('containsText',{text:'待确认',format:{fill:'#ECF2F8',font:{color:'#205C91'}}});
statuses.conditionalFormats.add('containsText',{text:'限校内',format:{fill:'#FFF3DC',font:{color:'#8B641D'}}});
for(let i=0;i<data.records.length;i++){
 const r=data.records[i];
 // Institution and region boundaries are shown by a subtle line, without extra columns/rows.
 if(i>0&&r.org_key!==data.records[i-1].org_key)sh.getRange(`A${i+2}:F${i+2}`).format.borders={top:{style:'thin',color:'#DCE2E8'}};
 const lines=Math.max(Math.ceil(r.row[2].length/26),Math.ceil(r.row[3].length/23),Math.ceil(r.row[4].length/18));
 if(lines>2)sh.getRange(`A${i+2}:F${i+2}`).format.rowHeight=Math.min(100,lines*16+8);
}
book.recalculate();
console.log((await book.inspect({kind:'table',range:`'${sh.name}'!A1:F5`,tableMaxRows:5,tableMaxCols:6,maxChars:1600})).ndjson);
const out=root+'/tmp/display/homepage.xlsx';
await(await SpreadsheetFile.exportXlsx(book)).save(out);
for(const [label,range] of [['top','A1:F10'],['candidate',`A${data.records.findIndex(x=>x.row[0].startsWith('日期未过'))+1}:F${data.records.findIndex(x=>x.row[0].startsWith('日期未过'))+7}`]]){
 const png=await book.render({sheetName:sh.name,range,scale:1.5,format:'png'});
 await fs.writeFile(root+`/tmp/display/${label}.png`,new Uint8Array(await png.arrayBuffer()));
}
console.log(JSON.stringify({export:out,rows:last,columns:6}));
