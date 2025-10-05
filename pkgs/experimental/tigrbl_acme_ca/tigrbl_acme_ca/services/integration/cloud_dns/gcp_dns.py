from __future__ import annotations

async def ensure_txt(ctx, zone: str, name: str, value: str, ttl: int = 60) -> None:
    client = ctx.get("gcp_dns")
    if not client:
        return
    try:
        await client.upsert_txt(zone=zone, name=name, value=value, ttl=ttl)
    except Exception:
        pass

async def delete_txt(ctx, zone: str, name: str, value: str | None = None) -> None:
    client = ctx.get("gcp_dns")
    if not client:
        return
    try:
        await client.delete_txt(zone=zone, name=name, value=value)
    except Exception:
        pass
