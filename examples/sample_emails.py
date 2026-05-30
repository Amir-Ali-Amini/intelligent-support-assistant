# sample emails for the demo and tests

# the main one: 3 requests in one email
MULTI_INTENT = (
    "Hi there,\n\n"
    "I placed order #12345 last week and I'd like to know where it is now. "
    "Also, I just got the Aurora Smartwatch and I can't figure out how to "
    "connect it to Wi-Fi and how long the battery lasts. "
    "Finally, if it turns out not to be a good fit, what is your refund "
    "policy?\n\n"
    "Thanks,\nMaria"
)

ORDER_ONLY = (
    "Hello, can you tell me the status of order 98765? It's been a few days. "
    "Thanks!"
)

TECH_ONLY = (
    "Quick question about the Thunder X1 Headphones — what's the battery "
    "life and do they support Bluetooth?"
)

REFUND_ONLY = (
    "I'm not happy with my purchase and want my money back. How do refunds "
    "work?"
)

VAGUE = "Hi, I have a problem. Please help."

ALL_SAMPLES = {
    "multi_intent": MULTI_INTENT,
    "order_only": ORDER_ONLY,
    "tech_only": TECH_ONLY,
    "refund_only": REFUND_ONLY,
    "vague": VAGUE,
}
