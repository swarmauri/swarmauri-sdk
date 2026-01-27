from __future__ import annotations


async def ensure_txt(ctx, zone_id: str, name: str, value: str, ttl: int = 60) -> None:
    client = ctx.get("aws_route53")
    if not client:
        return
    try:
        await client.upsert_txt(zone_id=zone_id, name=name, value=value, ttl=ttl)
    except Exception:
        pass


async def delete_txt(ctx, zone_id: str, name: str, value: str | None = None) -> None:
    client = ctx.get("aws_route53")
    if not client:
        return
    try:
        await client.delete_txt(zone_id=zone_id, name=name, value=value)
    except Exception:
        pass
