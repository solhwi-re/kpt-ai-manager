import os
from typing import Any

import requests
from fastapi import HTTPException

NOTION_TOKEN = (os.getenv("NOTION_TOKEN") or "").strip()
NOTION_DATA_SOURCE_ID = (os.getenv("NOTION_DATA_SOURCE_ID") or "").strip()

NOTION_VERSION = "2025-09-03"


def notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def rich_text_to_plain(items: list[dict[str, Any]] | None) -> str:
    return "".join(item.get("plain_text", "") for item in (items or [])).strip()


def get_title(properties: dict[str, Any]) -> str:
    for prop in properties.values():
        if prop.get("type") == "title":
            return rich_text_to_plain(prop.get("title"))
    return ""


def get_property_text(prop: dict[str, Any] | None) -> str:
    if not prop:
        return ""

    prop_type = prop.get("type")

    if prop_type == "title":
        return rich_text_to_plain(prop.get("title"))
    if prop_type == "rich_text":
        return rich_text_to_plain(prop.get("rich_text"))
    if prop_type == "select":
        return (prop.get("select") or {}).get("name", "")
    if prop_type == "status":
        return (prop.get("status") or {}).get("name", "")
    if prop_type == "people":
        return ", ".join(p.get("name", "") for p in prop.get("people", [])).strip()
    if prop_type == "checkbox":
        return "완료" if prop.get("checkbox") else "미완료"
    if prop_type == "date":
        date = prop.get("date")
        return date.get("start", "") if date else ""
    if prop_type == "formula":
        formula = prop.get("formula", {})
        ftype = formula.get("type")
        return str(formula.get(ftype, "")) if ftype else ""
    if prop_type == "rollup":
        return str(prop.get("rollup", ""))

    return ""


def query_data_source() -> list[dict[str, Any]]:
    if not NOTION_TOKEN:
        raise HTTPException(status_code=500, detail="NOTION_TOKEN is missing")
    if not NOTION_DATA_SOURCE_ID:
        raise HTTPException(status_code=500, detail="NOTION_DATA_SOURCE_ID is missing")

    url = f"https://api.notion.com/v1/data_sources/{NOTION_DATA_SOURCE_ID}/query"

    all_results: list[dict[str, Any]] = []
    payload: dict[str, Any] = {"page_size": 100}

    while True:
        res = requests.post(url, headers=notion_headers(), json=payload, timeout=30)

        if res.status_code >= 400:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Notion API error: {res.text}",
            )

        data = res.json()
        all_results.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data.get("next_cursor")

    return all_results


def normalize_category(value: str) -> str:
    text = (value or "").strip().lower()
    if "keep" in text:
        return "keep"
    if "problem" in text:
        return "problem"
    if text == "try" or "try" in text:
        return "try"
    return "unknown"


def get_kpt_items() -> dict[str, Any]:
    pages = query_data_source()

    grouped: dict[str, list[dict[str, str]]] = {
        "keep": [],
        "problem": [],
        "try": [],
        "unknown": [],
    }

    for page in pages:
        props = page.get("properties", {})

        title = get_title(props)
        category = get_property_text(props.get("구분"))
        summary = get_property_text(props.get("Summary"))
        manager = get_property_text(props.get("담당자"))
        complete = get_property_text(props.get("complete"))

        item = {
            "title": title,
            "summary": summary,
            "manager": manager,
            "complete": complete,
        }

        grouped[normalize_category(category)].append(item)

    return {
        "count": {
            "keep": len(grouped["keep"]),
            "problem": len(grouped["problem"]),
            "try": len(grouped["try"]),
            "unknown": len(grouped["unknown"]),
            "total": len(pages),
        },
        **grouped,
    }


def archive_page(page_id: str) -> None:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"archived": True}

    res = requests.patch(url, headers=notion_headers(), json=payload, timeout=30)

    if res.status_code >= 400:
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Notion archive error: {res.text}",
        )


def reset_kpt_board() -> dict[str, Any]:
    pages = query_data_source()

    archived_count = 0

    for page in pages:
        page_id = page.get("id")
        if not page_id:
            continue

        archive_page(page_id)
        archived_count += 1

    return {
        "status": "success",
        "message": "KPT 보드가 초기화되었습니다.",
        "archived_count": archived_count,
    }
