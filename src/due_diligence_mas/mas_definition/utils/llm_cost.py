from typing import Optional

from due_diligence_mas.mas_definition.constants.pricing import MODEL_PRICING


def get_model_pricing(model: str) -> Optional[dict]:
    """Per-token prices of the model (longest matching key of MODEL_PRICING), None if the model is not priced."""
    matches = [key for key in MODEL_PRICING if key in model]
    return MODEL_PRICING[max(matches, key=len)] if matches else None


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[dict]:
    """
    Cost in USD of the given tokens.

    Returns:
        {"input": ..., "output": ..., "total": ...}, or None if the model has no price in MODEL_PRICING
    """
    pricing = get_model_pricing(model)
    if pricing is None:
        return None

    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    return {"input": input_cost, "output": output_cost, "total": input_cost + output_cost}


def summarize_cost(models: dict) -> dict:
    """
    Cost in USD of the tokens by model: total and per model. Models without a price are listed in
    `unpriced_models` and not counted.

    Args:
        models: {model name: {"prompt_tokens": ..., "completion_tokens": ...}}
    """
    by_model, unpriced = {}, []
    for model, totals in models.items():
        cost = calculate_cost(model, totals["prompt_tokens"], totals["completion_tokens"])
        if cost is None:
            unpriced.append(model)
        else:
            by_model[model] = {key: round(value, 6) for key, value in cost.items()}

    return {
        "input": round(sum(cost["input"] for cost in by_model.values()), 6),
        "output": round(sum(cost["output"] for cost in by_model.values()), 6),
        "total": round(sum(cost["total"] for cost in by_model.values()), 6),
        "by_model": by_model,
        "unpriced_models": unpriced,
    }
