import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,R=path.resolve(H,'../../..');
const source=path.join(H,'baseline.xlsx');
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const s=w.worksheets.getItem('04其他资助');
for(const t of s.tables.items)t.delete();
const t=s.tables.add('A1:H3',true,'OtherFunding');t.style='TableStyleLight1';t.showFilterButton=true;t.showBandedRows=false;
const datePatches=JSON.parse(await fs.readFile(path.join(H,'date_plan.json'),'utf8'));
for(const p of datePatches){const c=w.worksheets.getItem(p.sheet).getRange(p.ref);c.values=[[p.serial]];c.setNumberFormat('yyyy-mm-dd');}
w.recalculate();
await fs.writeFile(path.join(H,'other_verified.png'),new Uint8Array(await (await w.render({sheetName:'04其他资助',range:'A1:H3',scale:1,format:'png'})).arrayBuffer()));
await fs.writeFile(path.join(H,'home_verified.png'),new Uint8Array(await (await w.render({sheetName:'01申报总览',range:'A1:F6',scale:1,format:'png'})).arrayBuffer()));
await(await SpreadsheetFile.exportXlsx(w)).save(path.join(H,'authored.xlsx'));
console.log('Authored matching table headers; rendered unchanged current other funding view.');
