
# Import os to read the API key from environment variables.
import os

# Import load_dotenv to load variables from the local .env file.
from dotenv import load_dotenv

# Import Streamlit to build the customer support web interface.
import streamlit as st

# Import Groq to create the API client.
from groq import Groq

# Import the shared message-analysis function from our new module.
from support_logic import analyze_message


# Load environment variables from the project's .env file.
load_dotenv()


# Configure the browser tab title, icon, and page layout.
st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="💬",
    layout="centered",
)


# Display the application title.
st.title("AI Customer Support Assistant")

# Explain what the application does.
st.write(
    "Analyze a customer message, classify the issue, and draft a reply "
    "for a human support agent to review."
)


# Read the Groq API key without displaying its value.
api_key = os.getenv("GROQ_API_KEY")


# Stop the application safely if the API key is missing.
if not api_key:
    # Explain how to fix the missing configuration.
    st.error(
        "GROQ_API_KEY was not found. Add it to your local .env file, "
        "then restart the application."
    )

    # Prevent the rest of the application from running without an API key.
    st.stop()


# Create the Groq client using the API key from the environment.
client = Groq(api_key=api_key)


# Create a text area where the user can enter a customer message.
customer_message = st.text_area(
    "Customer message",
    placeholder="Paste a customer message here...",
    height=160,
)


# Run the analysis when the user clicks the button.
if st.button("Analyze message", type="primary"):

    # Reject empty messages before sending a request to the model.
    if not customer_message.strip():
        # Ask the user to enter a message.
        st.warning("Please enter a customer message first.")

    else:
        # Show a loading indicator while the model processes the message.
        with st.spinner("Analyzing the message..."):
            try:
                # Call the shared function for classification and reply generation.
                analysis = analyze_message(
                    client,
                    customer_message.strip(),
                )

                # Create three columns for the classification results.
                col1, col2, col3 = st.columns(3)

                # Display the predicted issue category.
                col1.metric("Category", analysis["category"])

                # Display the predicted priority.
                col2.metric("Priority", analysis["priority"])

                # Display the predicted customer sentiment.
                col3.metric("Sentiment", analysis["sentiment"])

                # Show the explanation behind the priority decision.
                st.subheader("Why this priority?")

                # Display a fallback explanation if the model returned no reason.
                st.write(
                    analysis["reason"]
                    or "No explanation was provided."
                )

                # Add a section for the suggested customer-support reply.
                st.subheader("Suggested Reply")

                # Display the suggested reply inside a bordered container.
                with st.container(border=True):
                    st.markdown(analysis["suggested_reply"])

                # Warn the user when the generated reply was replaced.
                if analysis["reply_replaced"]:
                    st.warning(
                        "The generated reply triggered a safety check, "
                        "so a safer fallback reply is shown instead."
                    )

                # Display detected safety warnings when any were found.
                if analysis["reply_safety_warnings"]:
                    with st.expander("View safety-check details"):
                        # List the warnings detected in the original reply.
                        for warning in analysis["reply_safety_warnings"]:
                            st.write(f"- {warning}")

                # Remind the user that the reply requires human review.
                st.caption(
                    "AI-generated suggestion. Review it before sending. "
                    "No order lookup, investigation, refund, or support action "
                    "is performed by this application."
                )

            # Handle API errors, invalid JSON, and unexpected processing errors.
            except Exception as error:
                # Show a general error without exposing technical details in the UI.
                st.error(
                    "The message could not be analyzed. Check the API connection "
                    "and application logs, then try again."
                )

                # Log the error type and details in the local terminal.
                print(
                    f"Analysis error: {type(error).__name__}: {error}"
                )
