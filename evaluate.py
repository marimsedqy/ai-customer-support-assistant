
# Import JSON tools to save the evaluation report.
import json

# Import os to read the API key from the environment.
import os

# Import datetime to record when the evaluation runs.
from datetime import datetime

# Load environment variables from the .env file.
from dotenv import load_dotenv

# Import the predefined customer-message test cases.
from evaluation_cases import EVALUATION_CASES

# Reuse the same model, classification rules, and safety checks as the app.
from support_logic import MODEL_NAME, analyze_message
from groq import Groq


# Load environment variables from the project's .env file.
load_dotenv()


# Evaluate one test case using the shared application logic.
def evaluate_case(client, test_case):
    # Display the ID of the test case currently being evaluated.
    print(f"\nRunning test case {test_case['id']}...", flush=True)

    # Analyze the message using the same logic as the Streamlit application.
    result = analyze_message(client, test_case["message"])

    # Read the model's classification results.
    category = result["category"]
    priority = result["priority"]
    sentiment = result["sentiment"]

    # Compare each prediction with the expected test-case label.
    category_correct = category == test_case["expected_category"]
    priority_correct = priority == test_case["expected_priority"]
    sentiment_correct = sentiment == test_case["expected_sentiment"]

    # Calculate the percentage of correctly predicted classification fields.
    classification_score = (
        sum([category_correct, priority_correct, sentiment_correct]) / 3
    ) * 100

    # Collect safety findings produced by the shared safety checker.
    safety_warnings = result["reply_safety_warnings"]

    # Return all relevant results for the final evaluation report.
    return {
        "id": test_case["id"],
        "name": test_case.get("name", ""),
        "message": test_case["message"],
        "expected_category": test_case["expected_category"],
        "predicted_category": category,
        "category_correct": category_correct,
        "expected_priority": test_case["expected_priority"],
        "predicted_priority": priority,
        "priority_correct": priority_correct,
        "expected_sentiment": test_case["expected_sentiment"],
        "predicted_sentiment": sentiment,
        "sentiment_correct": sentiment_correct,
        "classification_score": round(classification_score, 2),
        "suggested_reply": result["suggested_reply"],
        "reply_replaced": result["reply_replaced"],
        "safety_warnings": safety_warnings,
        "automated_safety_pass": not safety_warnings,
        "manual_reply_review_required": True,
        "reply_criteria": test_case.get("reply_criteria", []),
    }


# Run the complete evaluation and save its report.
def main():
    # Read the API key without displaying its value.
    api_key = os.getenv("GROQ_API_KEY")

    # Stop if the API key is missing.
    if not api_key:
        print(
            "ERROR: GROQ_API_KEY was not found. Check your .env file.",
            flush=True,
        )
        return

    # Create the API client using the environment variable.
    client = Groq(api_key=api_key)

    # Store results from test cases that finish successfully.
    all_results = []

    # Store details about test cases that fail during processing.
    failed_cases = []

    # Evaluate every predefined test case.
    for test_case in EVALUATION_CASES:
        try:
            # Evaluate the current case and store its results.
            case_result = evaluate_case(client, test_case)
            all_results.append(case_result)

            # Print the predicted classification labels.
            print(f"Category: {case_result['predicted_category']}", flush=True)
            print(f"Priority: {case_result['predicted_priority']}", flush=True)
            print(f"Sentiment: {case_result['predicted_sentiment']}", flush=True)

            # Print the correctness of each classification field.
            print(f"Category correct: {case_result['category_correct']}", flush=True)
            print(f"Priority correct: {case_result['priority_correct']}", flush=True)
            print(f"Sentiment correct: {case_result['sentiment_correct']}", flush=True)

            # Print the combined classification score.
            print(
                f"Classification score: {case_result['classification_score']:.1f}%",
                flush=True,
            )

            # Report safety-check warnings, if any were detected.
            if case_result["safety_warnings"]:
                print(
                    "Safety warnings: "
                    + "; ".join(case_result["safety_warnings"]),
                    flush=True,
                )
            else:
                print(
                    "Automated reply check: No pattern-based warnings found.",
                    flush=True,
                )

            # Report whether the generated reply was replaced by a fallback.
            print(
                f"Reply replaced by fallback: {case_result['reply_replaced']}",
                flush=True,
            )

            # Display the reply that would be shown by the application.
            print(
                "Suggested reply: " + case_result["suggested_reply"],
                flush=True,
            )

            # Remind reviewers that automated checks are not conclusive.
            print("Manual reply review required: Yes", flush=True)

        except Exception as error:
            # Record the failed case so the report remains useful.
            failed_cases.append({
                "id": test_case.get("id"),
                "error": str(error),
            })

            # Display the error without exposing environment variables.
            print(
                f"ERROR in test case {test_case.get('id')}: {error}",
                flush=True,
            )

    # Count all test cases and successfully evaluated cases.
    total_cases = len(EVALUATION_CASES)
    successful_cases = len(all_results)

    # Calculate classification metrics from successful test cases only.
    if successful_cases:
        # Calculate category prediction accuracy.
        category_accuracy = (
            sum(item["category_correct"] for item in all_results)
            / successful_cases
        ) * 100

        # Calculate priority prediction accuracy.
        priority_accuracy = (
            sum(item["priority_correct"] for item in all_results)
            / successful_cases
        ) * 100

        # Calculate sentiment prediction accuracy.
        sentiment_accuracy = (
            sum(item["sentiment_correct"] for item in all_results)
            / successful_cases
        ) * 100

        # Calculate the average classification score across all cases.
        overall_score = (
            sum(item["classification_score"] for item in all_results)
            / successful_cases
        )

        # Count replies that triggered no pattern-based safety warnings.
        cases_without_warnings = sum(
            item["automated_safety_pass"] for item in all_results
        )

        # Count replies that were replaced by safe fallback messages.
        fallback_count = sum(
            item["reply_replaced"] for item in all_results
        )

    else:
        # Use zero values when no test case completed successfully.
        category_accuracy = 0
        priority_accuracy = 0
        sentiment_accuracy = 0
        overall_score = 0
        cases_without_warnings = 0
        fallback_count = 0

    # Assemble the evaluation report.
    report = {
        "model": MODEL_NAME,
        "evaluation_timestamp": datetime.now().astimezone().isoformat(),
        "total_test_cases": total_cases,
        "successful_api_responses": successful_cases,
        "failed_test_cases": failed_cases,
        "average_classification_score": round(overall_score, 2),
        "category_accuracy": round(category_accuracy, 2),
        "priority_accuracy": round(priority_accuracy, 2),
        "sentiment_accuracy": round(sentiment_accuracy, 2),
        "cases_without_pattern_warnings": cases_without_warnings,
        "fallback_replacements": fallback_count,
        "manual_review_required": True,
        "results": all_results,
    }

    # Save the report as a readable JSON file in the project directory.
    with open("evaluation_results.json", "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    # Print the final evaluation summary.
    print("\n" + "=" * 50, flush=True)
    print("EVALUATION SUMMARY", flush=True)
    print("=" * 50, flush=True)
    print(f"Total test cases: {total_cases}", flush=True)
    print(f"Successful API responses: {successful_cases}", flush=True)
    print(f"Failed test cases: {len(failed_cases)}", flush=True)
    print(f"Average classification score: {overall_score:.1f}%", flush=True)

    # Display accuracy separately for each classification field.
    print("\nCLASSIFICATION METRICS", flush=True)
    print(f"Category accuracy: {category_accuracy:.1f}%", flush=True)
    print(f"Priority accuracy: {priority_accuracy:.1f}%", flush=True)
    print(f"Sentiment accuracy: {sentiment_accuracy:.1f}%", flush=True)

    # Display the safety-check and fallback summary.
    print(
        f"Cases without pattern warnings: "
        f"{cases_without_warnings}/{successful_cases}",
        flush=True,
    )
    print(f"Fallback replacements: {fallback_count}", flush=True)

    # Confirm where the detailed report was saved.
    print("Detailed results saved to evaluation_results.json", flush=True)

    # Explain the limitation of automated pattern-based checks.
    print(
        "Note: Pattern checks are limited; manually review every suggested reply.",
        flush=True,
    )


# Run the evaluation only when this file is executed directly.
if __name__ == "__main__":
    main()
