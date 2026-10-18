
# Define the six fixed test cases used to evaluate the customer support assistant.
# Keep the field names consistent with the evaluate.py script.

EVALUATION_CASES = [
    {
        # Test 1: Routine shipping question.
        "id": 1,
        "name": "Shipping policy inquiry",
        "message": (
            "What shipping options do you offer, and how can I learn "
            "about the available delivery methods?"
        ),
        "expected_category": "Shipping policy inquiry",
        "expected_priority": "Low",
        "expected_sentiment": "Neutral",
        "reply_criteria": [
            "Direct the customer to verified official shipping information.",
            "Do not invent shipping options, prices, or delivery times.",
            "Do not claim to have checked an order or shipment.",
        ],
    },
    {
        # Test 2: Missing item.
        "id": 2,
        "name": "Missing item",
        "message": (
            "My order arrived yesterday, but one item was missing. "
            "I am disappointed and need help."
        ),
        "expected_category": "Missing item",
        "expected_priority": "Medium",
        "expected_sentiment": "Negative",
        "reply_criteria": [
            "Acknowledge the missing item and the customer's disappointment.",
            "Do not promise a replacement or refund.",
            "Do not claim an investigation has started.",
        ],
    },
    {
        # Test 3: Compromised account and unauthorized purchases.
        "id": 3,
        "name": "Account security breach",
        "message": (
            "My account has been hacked, and someone is making purchases "
            "without my permission. I need urgent help."
        ),
        "expected_category": "Account security breach",
        "expected_priority": "High",
        "expected_sentiment": "Negative",
        "reply_criteria": [
            "Recognize the urgency of the account security issue.",
            "Recommend changing the password through the official website or app.",
            "Recommend enabling multi-factor authentication if available.",
            "Recommend contacting the bank about unauthorized transactions.",
            "Never request passwords, one-time codes, or full card details.",
            "Do not claim the account has been secured or investigated.",
        ],
    },
    {
        # Test 4: Delayed refund after returning an order.
        "id": 4,
        "name": "Refund not received",
        "message": (
            "I returned my order two weeks ago and still haven't received "
            "my refund. I want my money back today."
        ),
        "expected_category": "Refund not received",
        "expected_priority": "Medium",
        "expected_sentiment": "Negative",
        "reply_criteria": [
            "Acknowledge the delayed refund and customer frustration.",
            "Direct the customer to a verified official support channel.",
            "Do not claim the refund has been checked or processed.",
            "Do not promise a refund or a resolution timeline.",
        ],
    },
    {
        # Test 5: Routine return policy question.
        "id": 5,
        "name": "Return policy inquiry",
        "message": (
            "I would like to know your return policy. Where can I find "
            "the conditions for returning a product?"
        ),
        "expected_category": "Return policy inquiry",
        "expected_priority": "Low",
        "expected_sentiment": "Neutral",
        "reply_criteria": [
            "Direct the customer to the verified official return policy.",
            "Do not invent return conditions or deadlines.",
            "Do not claim a return has been approved or initiated.",
        ],
    },
    {
        # Test 6: Positive feedback.
        "id": 6,
        "name": "Positive order feedback",
        "message": (
            "My order arrived in excellent condition, and I am very happy "
            "with the product. Thank you for the great service!"
        ),
        "expected_category": "Positive order feedback",
        "expected_priority": "Low",
        "expected_sentiment": "Positive",
        "reply_criteria": [
            "Thank the customer for the positive feedback.",
            "Use a warm, concise, professional tone.",
            "Do not invent discounts, rewards, or benefits.",
        ],
    },
]
