
# Import JSON tools to parse the model's structured response.
import json

# Import regular expressions to check generated replies for safety risks.
import re

# Import Groq to define the client type used by the shared analysis function.
from groq import Groq


# Define the exact language model used by both the app and evaluation.
MODEL_NAME = "openai/gpt-oss-120b"


# Define every category the model is allowed to return.
ALLOWED_CATEGORIES = [
    "Shipping policy inquiry",
    "Missing item",
    "Account security breach",
    "Refund not received",
    "Return policy inquiry",
    "Positive order feedback",
    "Damaged item",
    "Late delivery",
    "Order cancellation",
    "Product inquiry",
    "Payment issue",
    "Other",
]


# Define the valid priority labels.
ALLOWED_PRIORITIES = ["Low", "Medium", "High"]

# Define the valid sentiment labels.
ALLOWED_SENTIMENTS = ["Positive", "Neutral", "Negative"]


# Give the model the same classification and safety instructions everywhere.
SYSTEM_PROMPT = f"""
You are an AI customer-support assistant.

Analyze the customer's message and return one valid JSON object with these keys:
category, priority, sentiment, reason, suggested_reply.

Classification rules:
- Select exactly one category from this allowed list:
  {json.dumps(ALLOWED_CATEGORIES)}
- Copy the selected category label exactly as written.
- High priority is for credible immediate security risks, compromised accounts,
  unauthorized transactions, threats to personal safety, or similarly urgent cases.
- Medium priority is for unresolved order problems, missing items, late deliveries,
  damaged items, payment problems, and delayed refunds without immediate security risk.
- Low priority is for routine policy questions, product questions, general shipping
  questions, positive feedback, and non-urgent requests.
- An angry tone or a demand for an immediate answer does not automatically mean High.
- A missing item or delayed refund alone does not automatically mean High.
- Use Neutral sentiment for neutral questions, even if the topic is a problem.
- Use Negative sentiment when the customer expresses dissatisfaction or distress.
- Use Positive sentiment when the customer expresses praise or satisfaction.
- Briefly explain the selected priority in the reason field.

Reply safety rules:
- Write a polite, clear, empathetic reply suitable for a support agent to review.
- Never claim that you checked an order, account, payment, shipment, or refund.
- Never claim that an investigation, escalation, cancellation, replacement, or refund
  has started or has been completed.
- Never promise a refund, replacement, resolution, escalation, or response timeline.
- Never invent company policies, shipping details, refund windows, or case outcomes.
- Never invent company departments, support channels, or internal processes.
- You may ask for relevant non-sensitive details, such as an order number or the
  name of a missing product.
- Never ask for passwords, one-time codes, full card numbers, security codes,
  or other authentication secrets.
- For account compromise or unauthorized purchases, recommend changing the password
  through the official website or app, enabling multi-factor authentication if available,
  contacting the bank/payment provider about unauthorized charges, and contacting
  support through a verified official channel.
- Do not say "I will investigate", "I have checked", "we will issue a refund",
  or similar statements that imply an action has been performed or guaranteed.
- Keep the suggested reply concise and focused on the customer's issue.
- Return JSON only, with no Markdown fences or extra text.
"""


# Provide safe fallback replies if a generated reply is unsafe or empty.
SAFE_FALLBACK_REPLIES = {
    "Shipping policy inquiry": (
        "Thank you for contacting us. Please check the shipping information "
        "published on the official website, or contact a verified support "
        "channel if you need help with a specific order."
    ),
    "Missing item": (
        "I'm sorry an item was missing from your order. Please share your order "
        "number and the name of the missing item through a verified support "
        "channel so the support team has the details needed to assist you."
    ),
    "Account security breach": (
        "I'm sorry you're experiencing this. Change your password through the "
        "official website or app, enable multi-factor authentication if available, "
        "and contact your bank about unauthorized charges. Please contact support "
        "through a verified official channel. Never share your password or "
        "one-time verification codes."
    ),
    "Refund not received": (
        "I'm sorry your refund hasn't arrived yet. Please have your order number "
        "and return confirmation, if available, ready when contacting a verified "
        "support channel. Refund timing can depend on the merchant and payment provider."
    ),
    "Return policy inquiry": (
        "Thank you for your question. Please review the return policy on the "
        "official website, or contact a verified support channel if you need "
        "help understanding how it applies to your order."
    ),
    "Positive order feedback": (
        "Thank you for sharing your feedback. We're glad to hear about your "
        "experience, and we appreciate you taking the time to let us know."
    ),
    "Damaged item": (
        "I'm sorry your item arrived damaged. Please keep the item and packaging "
        "if possible, and contact a verified support channel with your order "
        "number and a description of the damage."
    ),
    "Late delivery": (
        "I'm sorry your delivery is late. Please review the tracking information "
        "available to you and contact a verified support channel if you need help."
    ),
    "Order cancellation": (
        "I understand you'd like to cancel your order. Please review the available "
        "cancellation options on the official website or contact a verified support "
        "channel. I can't confirm whether cancellation is possible."
    ),
    "Product inquiry": (
        "Thanks for your question. Please check the product details published "
        "on the official website, or contact a verified support channel if "
        "you need clarification about a specific product."
    ),
    "Payment issue": (
        "I'm sorry you're having a payment issue. Please don't share full card "
        "details or security codes. Contact your bank or payment provider through "
        "an official channel if you suspect an unauthorized transaction."
    ),
    "Other": (
        "Thank you for contacting us. Could you share a little more detail about "
        "your issue, without including passwords, verification codes, or sensitive "
        "payment information?"
    ),
}


# Define patterns that may indicate unsupported actions or promises.
UNSUPPORTED_ACTION_PATTERNS = [
    
    r"\bi (?:have |already have )?(?:already )?(?:checked|investigated|looked into)\b",
    r"\bwe (?:have |already have )?(?:already )?(?:checked|investigated|looked into)\b",
    r"\b(?:i|we) will (?:issue|process|send|provide|arrange|initiate|approve)\b",
    r"\b(?:your refund|a refund|your replacement|a replacement) will be\b",
    r"\bwe will (?:refund|replace|cancel|escalate|resolve|contact you)\b",
    
    # Detect claims that an action has already been completed.
    r"\b(?:i|we) have (?:already )?(?:checked|investigated|processed|approved|refunded|cancelled|canceled|escalated)\b",
    r"\b(?:has|have) been (?:escalated|processed|approved|refunded|cancelled|canceled)\b",

    r"\b(?:guarantee|guaranteed|definitely) (?:a refund|a replacement|resolution)\b",
    r"\bwithin \d+ business days\b",
]


# Define patterns that may indicate a request for sensitive information.
SENSITIVE_REQUEST_PATTERNS = [
    r"\b(?:send|share|provide|tell me|give me)\b.{0,35}\bpassword\b",
    r"\b(?:send|share|provide|tell me|give me)\b.{0,35}\b(?:one-time|verification|security) code\b",
    r"\b(?:send|share|provide|tell me|give me)\b.{0,35}\b(?:full card number|cvv|cvc|security code)\b",
]



# Inspect a generated reply for common safety risks.
def inspect_reply(reply):
    # Create a list to collect every detected safety warning.
    warnings = []

    # Normalize the reply to lowercase for case-insensitive matching.
    normalized_reply = reply.lower()

    # Check for unsupported actions, guarantees, and promised timelines.
    for pattern in UNSUPPORTED_ACTION_PATTERNS:
        # Search for the exact part of the reply that matches this pattern.
        match = re.search(pattern, normalized_reply, flags=re.IGNORECASE)

        # Record the matched phrase to make the warning easier to understand.
        if match:
            warnings.append(
                f"Potential unsupported action or promise: "
                f"'{reply[match.start():match.end()]}'"
            )

    # Check for requests for passwords, codes, or sensitive payment information.
    for pattern in SENSITIVE_REQUEST_PATTERNS:
        # Search for the exact part of the reply that matches this pattern.
        match = re.search(pattern, normalized_reply, flags=re.IGNORECASE)

        # Record the matched phrase if a sensitive-information request is detected.
        if match:
            warnings.append(
                f"Potential sensitive-information request: "
                f"'{reply[match.start():match.end()]}'"
            )

    # Return all warnings so the caller can decide how to handle the reply.
    return warnings



# Analyze one customer message using the shared model and safety rules.
def analyze_message(client: Groq, customer_message: str) -> dict:
    # Send the shared system prompt and the customer's message to Groq.
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            # Supply the common classification and safety instructions.
            {"role": "system", "content": SYSTEM_PROMPT},
            # Pass the customer message as input data to analyze.
            {
                "role": "user",
                "content": (
                    f"Allowed categories: {json.dumps(ALLOWED_CATEGORIES)}\n"
                    f"Customer message: {customer_message}"
                ),
            },
        ],
        # Request JSON output so the response can be parsed consistently.
        response_format={"type": "json_object"},
        # Use deterministic generation to reduce variation between requests.
        temperature=0,
    )

 
  

    # Read the model's response text.
    raw_content = response.choices[0].message.content

    # Parse the JSON response into a Python dictionary.
    result = json.loads(raw_content)

    # Replace an invalid category with the safe general category.
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"

    # Replace an invalid priority with the default priority.
    if result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Medium"

    # Replace an invalid sentiment with the neutral label.
    if result.get("sentiment") not in ALLOWED_SENTIMENTS:
        result["sentiment"] = "Neutral"

    # Normalize the explanation into a clean string.
    result["reason"] = str(result.get("reason") or "").strip()

    # Normalize the suggested reply into a clean string.
    result["suggested_reply"] = str(result.get("suggested_reply") or "").strip()

    
    # Check the original model-generated reply for safety warnings.
    original_reply = result["suggested_reply"]
    reply_warnings = inspect_reply(original_reply)

    # Print diagnostic details to help identify false safety warnings.
    print("\n--- Reply Safety Debugging ---")
    print("Original generated reply:", repr(original_reply))
    print("Detected safety warnings:", reply_warnings)
    print("--- End Reply Safety Debugging ---\n")


    # Decide whether the generated reply must be replaced.
    reply_replaced = bool(reply_warnings) or not result["suggested_reply"]

    # Use the category-specific fallback if the reply is unsafe or empty.
    if reply_replaced:
        result["suggested_reply"] = SAFE_FALLBACK_REPLIES[result["category"]]

    # Attach the safety findings so the app and evaluation can report them.
    result["reply_safety_warnings"] = reply_warnings

    # Record whether the fallback reply replaced the generated reply.
    result["reply_replaced"] = reply_replaced

    # Return the same structured analysis to every caller.
    return result


# Test the safety checker with safe and unsafe example replies.
def test_safety_checker():
    # Define example replies and the expected detection results.
    test_cases = [
        {
            "name": "Safe assistance",
            "reply": "I can help you understand the next steps.",
            "should_warn": False,
        },
        {
            "name": "Unsupported replacement promise",
            "reply": "We will send you a replacement tomorrow.",
            "should_warn": True,
        },
        {
            "name": "Claimed refund action",
            "reply": "I have already processed your refund.",
            "should_warn": True,
        },
    ]

    # Track how many tests match their expected results.
    passed = 0

    # Run each example through the existing safety checker.
    for case in test_cases:
        # Collect all warnings detected in this example.
        warnings = inspect_reply(case["reply"])

        # Determine whether the checker produced the expected warning result.
        actual_warning = bool(warnings)
        expected_warning = case["should_warn"]

        # Print the test name, expected result, actual result, and warnings.
        print(f"\nTest: {case['name']}")
        print(f"Expected warning: {expected_warning}")
        print(f"Actual warning: {actual_warning}")
        print(f"Warnings: {warnings}")

        # Count the test as passed only when the results match.
        if actual_warning == expected_warning:
            passed += 1
            print("Result: PASS")
        else:
            print("Result: FAIL")

    # Print the final test summary.
    print(f"\nSafety tests passed: {passed}/{len(test_cases)}")


# Run the tests only when this file is executed directly.
if __name__ == "__main__":
    test_safety_checker()
