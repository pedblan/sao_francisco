"""Versioned, provider-independent API cost accounting.

All persisted monetary values are decimal strings.  The GUI receives only
already-formatted totals; formulas and unit prices remain an internal detail.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Any

PRICE_TABLE_VERSION = "2026-07-28"
_MILLION = Decimal("1000000")
_MINUTE = Decimal("60")
_LONG_CONTEXT_THRESHOLD = 272_000


@dataclass(frozen=True, slots=True)
class UsageMetrics:
    """Normalized usage returned by a provider.

    ``total_tokens`` is kept separate because the interface may show a token
    count only when the provider explicitly returned one.
    """

    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None
    duration_seconds: Decimal | None = None
    reasoning_in_output: bool = True

    def __post_init__(self) -> None:
        for name in (
            "input_tokens",
            "cached_input_tokens",
            "cache_write_tokens",
            "output_tokens",
            "reasoning_tokens",
            "total_tokens",
        ):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or int(value) < 0):
                raise ValueError(f"{name} must be a non-negative integer")
            if value is not None:
                object.__setattr__(self, name, int(value))
        if self.duration_seconds is not None:
            duration = _decimal(self.duration_seconds)
            if duration < 0:
                raise ValueError("duration_seconds must not be negative")
            object.__setattr__(self, "duration_seconds", duration)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "total_tokens": self.total_tokens,
            "duration_seconds": (
                str(self.duration_seconds) if self.duration_seconds is not None else None
            ),
            "reasoning_in_output": self.reasoning_in_output,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any] | None) -> UsageMetrics:
        raw = dict(value or {})
        return cls(
            input_tokens=_optional_int(raw.get("input_tokens")),
            cached_input_tokens=_optional_int(raw.get("cached_input_tokens")),
            cache_write_tokens=_optional_int(raw.get("cache_write_tokens")),
            output_tokens=_optional_int(raw.get("output_tokens")),
            reasoning_tokens=_optional_int(raw.get("reasoning_tokens")),
            total_tokens=_optional_int(raw.get("total_tokens")),
            duration_seconds=_optional_decimal(raw.get("duration_seconds")),
            reasoning_in_output=bool(raw.get("reasoning_in_output", True)),
        )


@dataclass(frozen=True, slots=True)
class ModelPrice:
    input_per_million: Decimal | None = None
    cached_input_per_million: Decimal | None = None
    cache_write_per_million: Decimal | None = None
    output_per_million: Decimal | None = None
    long_input_per_million: Decimal | None = None
    long_cached_input_per_million: Decimal | None = None
    long_cache_write_per_million: Decimal | None = None
    long_output_per_million: Decimal | None = None
    per_minute: Decimal | None = None


def _price(**values: str | None) -> ModelPrice:
    return ModelPrice(
        **{
            key: Decimal(value) if value is not None else None
            for key, value in values.items()
        }
    )


# Standard processing, reviewed against the providers' official pricing pages
# on the version date above.
_PRICES = MappingProxyType(
    {
        ("openai", "gpt-4o-mini-transcribe"): _price(
            input_per_million="1.25",
            output_per_million="5.00",
            per_minute="0.003",
        ),
        ("openai", "gpt-4o-transcribe"): _price(
            input_per_million="2.50",
            output_per_million="10.00",
            per_minute="0.006",
        ),
        ("openai", "gpt-4o-transcribe-diarize"): _price(
            input_per_million="2.50",
            output_per_million="10.00",
            per_minute="0.006",
        ),
        ("openai", "whisper-1"): _price(per_minute="0.006"),
        ("openai", "gpt-5.6-terra"): _price(
            input_per_million="2.50",
            cached_input_per_million="0.25",
            cache_write_per_million="3.125",
            output_per_million="15.00",
            long_input_per_million="5.00",
            long_cached_input_per_million="0.50",
            long_cache_write_per_million="6.25",
            long_output_per_million="22.50",
        ),
        ("openai", "gpt-5.6-sol"): _price(
            input_per_million="5.00",
            cached_input_per_million="0.50",
            cache_write_per_million="6.25",
            output_per_million="30.00",
            long_input_per_million="10.00",
            long_cached_input_per_million="1.00",
            long_cache_write_per_million="12.50",
            long_output_per_million="45.00",
        ),
        ("gemini", "gemini-3.6-flash"): _price(
            input_per_million="1.50",
            output_per_million="7.50",
        ),
        ("gemini", "gemini-3.5-flash-lite"): _price(
            input_per_million="0.30",
            output_per_million="2.50",
        ),
    }
)


@dataclass(frozen=True, slots=True)
class CostRecord:
    stage: str
    unit_id: str
    provider: str
    model: str
    usd: Decimal | None
    method: str
    usage: UsageMetrics = UsageMetrics()
    billable_duration_seconds: Decimal | None = None
    price_version: str = PRICE_TABLE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "unit_id": self.unit_id,
            "provider": self.provider,
            "model": self.model,
            "usd": str(self.usd) if self.usd is not None else None,
            "method": self.method,
            "usage": self.usage.to_dict(),
            "billable_duration_seconds": (
                str(self.billable_duration_seconds)
                if self.billable_duration_seconds is not None
                else None
            ),
            "price_version": self.price_version,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CostRecord:
        return cls(
            stage=str(value.get("stage") or ""),
            unit_id=str(value.get("unit_id") or ""),
            provider=str(value.get("provider") or ""),
            model=str(value.get("model") or ""),
            usd=_optional_decimal(value.get("usd")),
            method=str(value.get("method") or "unavailable"),
            usage=UsageMetrics.from_dict(_mapping(value.get("usage"))),
            billable_duration_seconds=_optional_decimal(
                value.get("billable_duration_seconds")
            ),
            price_version=str(value.get("price_version") or PRICE_TABLE_VERSION),
        )


def price_for(provider: str, model: str) -> ModelPrice | None:
    return _PRICES.get((provider.strip().casefold(), model.strip()))


def build_cost_record(
    *,
    stage: str,
    unit_id: str,
    provider: str,
    model: str,
    usage: UsageMetrics | Mapping[str, Any] | None = None,
    duration_seconds: float | Decimal | None = None,
) -> CostRecord:
    normalized_usage = (
        usage
        if isinstance(usage, UsageMetrics)
        else UsageMetrics.from_dict(_mapping(usage))
    )
    duration = _optional_decimal(duration_seconds)
    price = price_for(provider, model)
    if price is None:
        return CostRecord(
            stage,
            unit_id,
            provider,
            model,
            None,
            "unavailable",
            normalized_usage,
            duration,
        )

    token_cost = _token_cost(normalized_usage, price)
    if token_cost is not None:
        return CostRecord(
            stage,
            unit_id,
            provider,
            model,
            token_cost,
            "reported_usage",
            normalized_usage,
            duration,
        )

    billed_duration = normalized_usage.duration_seconds or duration
    if billed_duration is not None and price.per_minute is not None:
        return CostRecord(
            stage,
            unit_id,
            provider,
            model,
            (billed_duration / _MINUTE) * price.per_minute,
            (
                "reported_duration"
                if normalized_usage.duration_seconds is not None
                else "planned_duration"
            ),
            normalized_usage,
            billed_duration,
        )

    return CostRecord(
        stage,
        unit_id,
        provider,
        model,
        None,
        "unavailable",
        normalized_usage,
        duration,
    )


def zero_cost_record(
    *, stage: str, unit_id: str, provider: str, model: str
) -> CostRecord:
    return CostRecord(
        stage=stage,
        unit_id=unit_id,
        provider=provider,
        model=model,
        usd=Decimal("0"),
        method="existing_captions",
    )


def summarize_costs(
    records: Iterable[CostRecord | Mapping[str, Any]],
    *,
    zero_proven: bool = False,
) -> dict[str, Any]:
    normalized = tuple(
        item if isinstance(item, CostRecord) else CostRecord.from_dict(item)
        for item in records
    )
    known = [item.usd for item in normalized if item.usd is not None]
    unavailable = any(item.usd is None for item in normalized)
    total = sum(known, Decimal("0")) if known else None
    reported_tokens = [
        item.usage.total_tokens
        for item in normalized
        if item.usage.total_tokens is not None
    ]
    token_total = sum(reported_tokens) if reported_tokens else None
    proven_zero = bool(
        zero_proven
        and normalized
        and not unavailable
        and total == 0
        and all(item.method == "existing_captions" for item in normalized)
    )
    return {
        "usd": str(total) if total is not None and not unavailable else None,
        "partial_usd": str(sum(known, Decimal("0"))) if known else None,
        "available": total is not None and not unavailable,
        "partial": bool(known and unavailable),
        "proven_zero": proven_zero,
        "reported_tokens": token_total,
        "price_version": PRICE_TABLE_VERSION,
    }


def format_cost_label(
    summary: Mapping[str, Any] | None, *, in_progress: bool = False
) -> str:
    value = dict(summary or {})
    if value.get("proven_zero"):
        return "Sem custo de API"
    raw = value.get("usd")
    if raw is None and value.get("partial"):
        raw = value.get("partial_usd")
    amount = _optional_decimal(raw)
    if amount is None:
        return ""
    prefix = "Custo até agora" if in_progress else "Custo estimado"
    if amount > 0 and amount < Decimal("0.01"):
        return f"{prefix}: menos de US$ 0,01"
    rendered = amount.quantize(Decimal("0.01"))
    return f"{prefix}: cerca de US$ {str(rendered).replace('.', ',')}"


def format_usage_label(summary: Mapping[str, Any] | None) -> str:
    tokens = _optional_int(dict(summary or {}).get("reported_tokens"))
    if tokens is None:
        return ""
    return f"Uso informado: {tokens:,} tokens".replace(",", ".")


def _token_cost(usage: UsageMetrics, price: ModelPrice) -> Decimal | None:
    if usage.input_tokens is None or usage.output_tokens is None:
        return None
    long_context = usage.input_tokens > _LONG_CONTEXT_THRESHOLD
    input_rate = (
        price.long_input_per_million
        if long_context and price.long_input_per_million is not None
        else price.input_per_million
    )
    output_rate = (
        price.long_output_per_million
        if long_context and price.long_output_per_million is not None
        else price.output_per_million
    )
    if input_rate is None or output_rate is None:
        return None

    cached = min(usage.cached_input_tokens or 0, usage.input_tokens)
    writes = min(usage.cache_write_tokens or 0, usage.input_tokens - cached)
    ordinary = max(0, usage.input_tokens - cached - writes)
    cached_rate = (
        price.long_cached_input_per_million
        if long_context and price.long_cached_input_per_million is not None
        else price.cached_input_per_million
    ) or input_rate
    write_rate = (
        price.long_cache_write_per_million
        if long_context and price.long_cache_write_per_million is not None
        else price.cache_write_per_million
    ) or input_rate
    output = usage.output_tokens
    if not usage.reasoning_in_output:
        output += usage.reasoning_tokens or 0
    return (
        Decimal(ordinary) * input_rate
        + Decimal(cached) * cached_rate
        + Decimal(writes) * write_rate
        + Decimal(output) * output_rate
    ) / _MILLION


def _mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("invalid decimal value") from exc


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    return _decimal(value)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


__all__ = [
    "CostRecord",
    "ModelPrice",
    "PRICE_TABLE_VERSION",
    "UsageMetrics",
    "build_cost_record",
    "format_cost_label",
    "format_usage_label",
    "price_for",
    "summarize_costs",
    "zero_cost_record",
]
