import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const root=process.cwd();
const f=(await fs.readdir(root)).find(x=>x.endsWith('.xlsx'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(root+'/'+f));
console.log((await w.inspect({kind:'sheet',include:'id,name',maxChars:1200})).ndjson);
const b=await w.render({sheetName:'01申报总览',range:'A1:H10',scale:1,format:'png'});
await fs.writeFile(root+'/tmp/rebuild/original_preview.png',new Uint8Array(await b.arrayBuffer()));
