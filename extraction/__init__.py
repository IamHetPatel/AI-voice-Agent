"""Asynchronous extraction layer.

The chat LLM (Gemini) is freed from JSON-schema bookkeeping; instead we stream
the live transcript here and let GLiNER2 zero-shot tag the 13 claim pillars.
This is what wins the Pioneer/Fastino bounty AND keeps voice latency low.
"""
