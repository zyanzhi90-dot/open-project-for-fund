import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname;
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,'全国机器人开放课题_个人申报台账_结构精简版_20261009.xlsx')));
// This workbook contains no formulas; use imported static values for visual verification.
await fs.writeFile(path.join(H,'inspection.jsonl'),(await w.inspect({kind:'sheet',include:'id,name',maxChars:3500})).ndjson);
await fs.writeFile(path.join(H,'home_inspection.jsonl'),(await w.inspect({kind:'table',range:'01申报总览!A1:F5',include:'values',tableMaxRows:5,tableMaxCols:6,maxChars:1800})).ndjson);
await fs.writeFile(path.join(H,'after.png'),new Uint8Array(await (await w.render({sheetName:'01申报总览',range:'A1:F5',scale:1,format:'png'})).arrayBuffer()));
await fs.writeFile(path.join(H,'coverage.png'),new Uint8Array(await (await w.render({sheetName:'06机构检索覆盖',range:'A6:I8',scale:1,format:'png'})).arrayBuffer()));
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?',options:{useRegex:true,maxResults:10},summary:'精简结构错误扫描'})).ndjson);
