from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import openpyxl


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "02_检索与核验记录" / "审计记录"
BOOK = ROOT / "全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx"
EXCLUSIONS = AUDIT / "项目剔除记录_20261009.csv"
LOG = AUDIT / "项目核验日志_20261009.csv"
OUT = AUDIT / "项目去重基准_20261011.csv"
SUMMARY = AUDIT / "项目去重基准说明_20261011.md"
MANIFEST = AUDIT / "项目去重基准校验_20261011.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return re.sub(r"\s+", " ", str(value)).strip()


def norm_label(value: str) -> str:
    return re.sub(r"[\s\u3000]+", "", value).casefold()


def urls(value: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"https?://[^\s<>\]\[\)\}，；;]+", value or "")))


def canonical_url(value: str) -> str:
    if not value:
        return ""
    parsed = urlsplit(value.strip().rstrip(".,;"))
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    # Query strings can identify separate CMS documents; retain them only when
    # they carry a likely record/document ID. Drop tracking and session noise.
    query = ""
    if parsed.query and re.search(r"(?:id|article|doc|content|news|wbfileid)=", parsed.query, re.I):
        query = parsed.query
    path = re.sub(r"/{2,}", "/", parsed.path or "/").rstrip("/") or "/"
    return urlunsplit(("https", host, path, query, ""))


def year_label(raw: str, title: str, source: str) -> tuple[str, str]:
    raw = raw.strip()
    explicit = re.findall(r"20\d{2}", raw)
    if explicit:
        return raw, "工作簿年度字段"
    title_years = re.findall(r"20\d{2}", title)
    if title_years:
        return "/".join(dict.fromkeys(title_years)), "标题/项目名称明示年度；待与正式公告核对"
    # A dated URL is only a lead; never silently treat its publication year as
    # the project year.
    url_year = re.search(r"/(20\d{2})/", source)
    if url_year:
        return "年度未明（URL日期线索：" + url_year.group(1) + ")", "不得以URL发布日期代替项目年度"
    return "年度未明", "资料未给出可确认的项目年度"


def batch_key(platform_owner: str, platform: str, year: str, source: str) -> str:
    # URL is a batch locator, not proof of project equivalence. Distinct topics
    # under one notice intentionally share a batch key.
    raw = "|".join(map(norm_label, [platform_owner, platform, year, source]))
    return "B-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def main() -> None:
    wb = openpyxl.load_workbook(BOOK, read_only=True, data_only=True)
    ws = wb["03所有项目完整详情"]
    detail_values = list(ws.values)
    headers = [text(v) for v in detail_values[0]]
    rows = [dict(zip(headers, row)) for row in detail_values[1:] if text(row[0])]
    audit_rows = read_csv(EXCLUSIONS)
    logs = read_csv(LOG)

    detail_by_id: dict[str, dict[str, object]] = {}
    alias_owner: dict[str, str] = {}
    items: list[dict[str, str]] = []
    for row in rows:
        pid = text(row.get("项目编号"))
        owner = text(row.get("依托单位"))
        platform = text(row.get("实验室/项目"))
        title = platform
        raw_year = text(row.get("项目年度"))
        all_sources = list(dict.fromkeys(urls(text(row.get("公告/线索来源URL")) + "\n" + text(row.get("官方指南/办法/附件URL")))) )
        announcement_urls = urls(text(row.get("公告/线索来源URL")))
        primary = canonical_url(announcement_urls[0] if announcement_urls else (all_sources[0] if all_sources else ""))
        yr, yr_basis = year_label(raw_year, title, primary)
        bkey = batch_key(owner, platform, yr, primary)
        d = {
            "记录类型": "工作簿详情", "项目编号": pid, "关联工作簿编号": pid,
            "依托单位原文": owner, "平台或项目原文": platform,
            "平台核对键": norm_label(owner) + "|" + norm_label(platform),
            "项目年度原文": raw_year, "基准年度": yr, "年度依据": yr_basis,
            "批次核对键": bkey, "批次来源定位": primary,
            "状态原文": text(row.get("申报状态")), "截止日期原文": text(row.get("截止日期")),
            "原编号及别名": text(row.get("其他原编号")),
            "主来源URL": primary, "全部来源URL": "\n".join(all_sources),
            "重复/关联判断": "工作簿基准记录；项目编号唯一。仅共享平台年度批次键不代表项目重复。",
            "需人工复核": "是" if ("未明" in yr or not primary) else "否",
        }
        detail_by_id[pid] = d
        for alias in re.findall(r"(?<![A-Z0-9])[A-Z]\d{3}(?![A-Z0-9])", text(row.get("其他原编号"))):
            if alias != pid:
                alias_owner[alias] = pid
        items.append(d)

    # Crosswalk exclusion audit entries to the workbook, keeping recovered and
    # repeated audit rows instead of counting them as separate projects.
    for audit in audit_rows:
        pid = text(audit.get("原项目编号"))
        owner = text(audit.get("依托单位"))
        platform = text(audit.get("实验室/项目"))
        source_urls = urls(text(audit.get("官方来源")))
        primary = canonical_url(source_urls[0] if source_urls else "")
        canonical_id = pid if pid in detail_by_id else alias_owner.get(pid, "")
        linked = detail_by_id.get(canonical_id)
        yr, yr_basis = year_label("", platform, primary)
        bkey = batch_key(owner, platform, yr, primary)
        overlap = ("同编号已在工作簿详情" if pid in detail_by_id else
                   ("原编号/误设别名已由详情表交叉引用" if linked else
                    "剔除/恢复审计记录；需按平台、年度、批次与详情对照"))
        if linked:
            yr = str(linked["基准年度"])
            yr_basis = "关联工作簿编号 " + pid
            bkey = str(linked["批次核对键"])
            if norm_label(owner) != norm_label(str(linked["依托单位原文"])) or norm_label(platform) != norm_label(str(linked["平台或项目原文"])):
                overlap += "；单位/项目名称有差异，保留原文并复核"
        item = {
            "记录类型": "剔除/恢复审计", "项目编号": pid, "关联工作簿编号": canonical_id if linked else "",
            "依托单位原文": owner, "平台或项目原文": platform,
            "平台核对键": norm_label(owner) + "|" + norm_label(platform),
            "项目年度原文": "", "基准年度": yr, "年度依据": yr_basis,
            "批次核对键": bkey, "批次来源定位": primary,
            "状态原文": text(audit.get("状态")), "截止日期原文": "",
            "原编号及别名": pid if canonical_id and canonical_id != pid else "",
            "主来源URL": primary, "全部来源URL": "\n".join(source_urls),
            "重复/关联判断": overlap + "；审计行不是新增项目计数",
            "需人工复核": "是" if (not linked or "差异" in overlap or "未明" in yr or not primary) else "否",
        }
        items.append(item)

    by_platform_year: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_batch: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    audit_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in items:
        if item["记录类型"] == "工作簿详情":
            by_platform_year[(item["平台核对键"], item["基准年度"])].append(item)
            by_batch[(item["平台核对键"], item["基准年度"], item["批次核对键"])].append(item)
        else:
            audit_by_id[item["项目编号"]].append(item)

    for bucket in by_platform_year.values():
        if len(bucket) > 1:
            for item in bucket:
                item["需人工复核"] = "是"
                item["重复/关联判断"] += "；同平台同年度多条记录，需比对公告批次/项目身份，不自动合并"

    fields = list(items[0])
    with OUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)

    platform_year_multiple = [v for v in by_platform_year.values() if len(v) > 1]
    batch_multiple = [v for v in by_batch.values() if len(v) > 1]
    audit_repeated = {k: v for k, v in audit_by_id.items() if len(v) > 1}
    id_set = {item["项目编号"] for item in items if item["记录类型"] == "工作簿详情"}
    audit_ids = {item["项目编号"] for item in items if item["记录类型"] == "剔除/恢复审计"}
    log_ids = {text(row.get("项目编号")) for row in logs if text(row.get("项目编号"))}
    log_project_ids = {pid for pid in log_ids if re.fullmatch(r"[A-Z]\d{3}", pid)}
    mapped_log_ids = {alias_owner.get(pid, pid) for pid in log_project_ids}
    matched_audit = audit_ids & id_set
    status_counts = Counter(item["状态原文"] for item in items if item["记录类型"] == "工作簿详情")
    unresolved_year = sum("未明" in item["基准年度"] for item in items if item["记录类型"] == "工作簿详情")
    no_source = sum(not item["主来源URL"] for item in items if item["记录类型"] == "工作簿详情")
    manifest = {
        "as_of": "2026-10-11",
        "workbook": BOOK.name,
        "workbook_sha256": hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        "inputs": {
            "detail_rows": len(rows), "detail_unique_ids": len(id_set),
            "exclusion_audit_rows": len(audit_rows), "exclusion_unique_ids": len(audit_ids),
            "audit_ids_also_in_details": len(matched_audit), "audit_ids_not_in_details": len(audit_ids - id_set),
            "verification_log_rows": len(logs), "verification_log_unique_ids": len(log_ids),
        },
        "benchmark_rows": len(items),
        "detail_platform_year_groups": len(by_platform_year),
        "detail_platform_year_groups_with_multiple_records": len(platform_year_multiple),
        "detail_platform_year_batch_groups": len(by_batch),
        "batch_keys_with_multiple_detail_records": len(batch_multiple),
        "repeated_audit_ids": {k: len(v) for k, v in audit_repeated.items()},
        "detail_status_counts": dict(status_counts),
        "detail_rows_with_unresolved_project_year": unresolved_year,
        "detail_rows_without_source_url": no_source,
        "log_nonproject_scope_ids": len(log_ids - log_project_ids),
        "log_project_ids_after_alias_map": len(mapped_log_ids),
        "log_project_ids_not_in_details_or_exclusion_audit_after_alias_map": len(mapped_log_ids - id_set - audit_ids),
        "output_csv_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "rules": [
            "项目编号用于交叉引用，不覆盖平台/年度/批次对账。",
            "平台＋年度＋批次是对账桶；相同桶内多条详情保留为独立项目，除非具体项目身份和公告证据证明重复。",
            "批次以正式公告主来源URL定位；同一公告不同转载URL不自动合并，需人工比对公告内容。",
            "剔除/恢复审计行不是项目数；先按原编号关联详情，再处理别名、更名及后续新年度/批次。",
            "核验日志是字段事件，不计项目；机构范围记录编号不作项目编号；详情表其他原编号用于映射旧编号。",
            "工作簿年度字段优先；否则只记录名称明确年度，URL发布日期绝不代替项目年度。",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""# 项目去重基准说明（2026-10-11）

本基准只建立既有项目的对账索引，不新增检索结论，也不修改Excel。主台账以当前交付版完整详情为准，剔除记录用于恢复/排除状态交叉核对，核验日志用于追溯字段证据；日志行不是项目。

## 输入和行数

- 完整详情：{len(rows)}条，{len(id_set)}个唯一原编号。
- 剔除/恢复审计：{len(audit_rows)}行、{len(audit_ids)}个不同编号；其中{len(matched_audit)}个编号已在详情表，{len(audit_ids - id_set)}个尚未按编号映射到详情。
- 核验日志：{len(logs)}条字段事件、{len(log_ids)}种编号；其中{len(log_ids - log_project_ids)}个为机构范围记录编号，不作项目计数。旧编号映射后，未映射到详情或剔除审计的项目编号有{len(mapped_log_ids - id_set - audit_ids)}个。
- 去重基准CSV：{len(items)}行，包含全部详情和逐行剔除/恢复审计。

## 主键与防误合并规则

每条记录保留原项目编号、依托单位、平台/项目名、状态、年度原文及来源。平台核对键由单位和平台原文去空格生成；它只是辅助键，不把更名、共同依托或相似名称自动合并。项目年度优先取详情表年度字段；字段没有年度时只接受名称中明确写出的年度，URL年份仅作为待查提示。

基准按“平台核对键＋项目年度＋公告批次来源定位”形成批次核对键。它用于把资料放入可比对的桶，**不等于同桶项目重复**。同平台同年度可以存在不同批次或不同课题；只有核实公告批次及具体课题身份相同，才标为重复。不同年度、新批次、延期公告均保留单独核对位置；延期回到原批次交叉引用，不另增项目数。

公告链接优先使用详情表“公告/线索来源URL”首个来源，规范化时去掉跟踪参数；保留原始全部来源。转载、迁移页或共用公告尚未证明等同的，不自动归并。剔除审计按原编号与详情关联；同一项目的恢复/重复审计仍逐行保留，但不另计项目。核验日志只作字段证据索引。

## 当前基准统计

- 详情中有{len(by_platform_year)}个平台—年度组合，其中{len(platform_year_multiple)}组含多条记录；有{len(by_batch)}个平台—年度—批次桶，其中{len(batch_multiple)}桶含多条详情，须逐项目核对，不能按桶直接去重。
- 同平台同年度多条记录的组合已在CSV中逐行标记人工比对；当前一组为同一滁州学院平台2025年度的N059与N187，两条公告URL不同，基准暂分成两个批次定位键，未据此断定相同或不同项目。
- 详情中{unresolved_year}条项目年度无法从年度字段或名称确认，{no_source}条缺主来源URL；这些记录标记待复核。
- 详情状态原文分布：{json.dumps(dict(status_counts), ensure_ascii=False)}。

## 文件

- `项目去重基准_20261011.csv`：逐条交叉索引与批次桶。
- `项目去重基准校验_20261011.json`：输入散列、行数、未映射编号和可复算口径。
- `建立去重基准.py`：重新生成上述基准的脚本。

这份基准是既有数据的去重起点，不表示已逐条重新人工核验400余条公告，也不代表全国平台清查完成。后续进入线索核实时，只对本基准中的重复候选、年度/批次缺口和未映射项按具体证据处理。
"""
    SUMMARY.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
