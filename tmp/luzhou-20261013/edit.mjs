import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const source='D:/桌面/全国机器人与医工开放项目/02_检索与核验记录/特殊科研资助清单_20261013/机器人相关特殊科研资助清单_20261013.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
console.log((await wb.inspect({kind:'sheet,table',maxChars:1500})).ndjson);
const preview=await wb.render({sheetName:'科研资助清单',range:'A9:H11',scale:1,format:'png'});
await fs.writeFile(new URL('./before.png',import.meta.url),new Uint8Array(await preview.arrayBuffer()));
if(process.argv.includes('--edit')){
 const data=JSON.parse(await fs.readFile(new URL('./row.json',import.meta.url),'utf8'));
 const s=wb.worksheets.getItem('科研资助清单');
 s.getRange('A10:H10').values=[data];
 s.getRange('B10').setNumberFormat('yyyy-mm-dd');
 s.getRange('A10:H10').format.rowHeight=409;
 wb.recalculate();
 await (await SpreadsheetFile.exportXlsx(wb)).save(fileURLToPath(new URL('./edited.xlsx',import.meta.url)));
 const after=await wb.render({sheetName:'科研资助清单',range:'A10:H10',scale:1,format:'png'});
 await fs.writeFile(new URL('./after.png',import.meta.url),new Uint8Array(await after.arrayBuffer()));
}
