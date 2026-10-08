import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname;
const root=path.resolve(H,'../../..');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'全国机器人开放课题_个人申报台账_严格重筛版_20261008.xlsx')));
const b=await wb.render({sheetName:'01申报总览',range:'A1:F5',scale:1,format:'png'});
await fs.writeFile(path.join(H,'baseline.png'),new Uint8Array(await b.arrayBuffer()));
console.log('baseline.png');
