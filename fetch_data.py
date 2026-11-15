#!/usr/bin/env python3
"""Fetch latest 100+ P5 draws from China Sports Lottery history endpoint.
Endpoint/gameNo are configurable because upstream may change them.
"""
import json, os, re, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from pathlib import Path

URL = os.getenv("SPORTTERY_API_URL", "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry")
GAME_NO = os.getenv("SPORTTERY_GAME_NO", "350133")
PAGE_SIZE = int(os.getenv("SPORTTERY_PAGE_SIZE", "100"))
OUT = Path("data/draws.json")

def request_page(page):
    params = f"?gameNo={GAME_NO}&provinceId=0&pageSize={PAGE_SIZE}&isVerify=1&pageNo={page}"
    req = Request(URL + params, headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://m.lottery.gov.cn/",
    })
    with urlopen(req, timeout=25) as resp:
        raw = resp.read().decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # WAF or upstream response is not JSON; do not silently treat as empty data.
        raise RuntimeError("官方接口返回的内容不是 JSON：" + raw[:300])

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)

def parse_records(payload):
    found = {}
    for item in walk(payload):
        period = item.get("lotteryDrawNum") or item.get("lotteryDrawNo") or item.get("expect") or item.get("issue")
        raw = item.get("lotteryDrawResult") or item.get("lotteryDrawResultDesc") or item.get("openCode") or item.get("number")
        if not period or raw is None:
            continue
        digits = re.findall(r"(?<!\d)\d(?!\d)", str(raw))
        if len(digits) < 4:
            digits = list(re.sub(r"\D", "", str(raw)))
        if len(digits) < 4:
            continue
        # 排列五开奖结果为五位；本系统只分析前四位：万、千、百、十。
        number5 = "".join(digits[:5])
        number4 = number5[:4]
        date = item.get("lotteryDrawTime") or item.get("openTime") or item.get("drawTime") or ""
        found[str(period)] = {
            "period": str(period), "date": str(date),
            "number": number4, "official_number": number5,
        }
    return list(found.values())

def main():
    records = []
    errors = []
    for page in (1, 2, 3, 4, 5):
        try:
            payload = request_page(page)
            batch = parse_records(payload)
            if not batch:
                # Stop only after the first empty page; a changed response schema is an error.
                if page == 1:
                    raise RuntimeError("接口响应中未找到期号及开奖号码字段；需重新核对官方响应结构。")
                break
            records.extend(batch)
            if len(records) >= 500:
                break
            time.sleep(1.2)
        except Exception as exc:
            errors.append(f"page {page}: {exc}")
            if page == 1:
                raise
            break
    unique = {x["period"]: x for x in records}
    records = sorted(unique.values(), key=lambda x: x["period"], reverse=True)[:500]
    if len(records) < 100:
        raise RuntimeError(f"仅取得 {len(records)} 期，少于最低100期；拒绝覆盖旧数据。错误：{errors}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "meta": {
            "source": URL, "game_no": GAME_NO,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": "official endpoint fetch; verify against official publication",
            "records": len(records),
            "note": "仅分析官方五位开奖号码的前四位（万千百十）；原始五位保存在 official_number。"
        },
        "draws": records
    }
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OUT)
    print(f"Saved {len(records)} draws to {OUT}")
    if errors:
        print("Warnings:", "; ".join(errors))

if __name__ == "__main__":
    main()
