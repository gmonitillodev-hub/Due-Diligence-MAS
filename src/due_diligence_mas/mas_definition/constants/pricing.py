# USD per single token, by model. A key matches any model name containing it, whatever the provider prefix or
# version suffix ("gpt-4o-mini" matches "openai/gpt-4o-mini" and "gpt-4o-mini-2024-07-18"); the longest key wins.
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "openai/gpt-oss-20b": {"input": 0.075 / 1_000_000, "output": 0.30 / 1_000_000},
    "openai/gpt-oss-120b": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
}
