# AI Customer Support Assistant

An AI-powered application that analyzes customer support messages, classifies customer issues, identifies priority and sentiment, and generates suggested replies.

## Project Overview

Customer support teams receive messages about different issues, such as shipping, missing items, refunds, and account security. This project helps organize those messages and provides AI-generated reply suggestions for support agents to review.

## Features

- **Message Classification:** Identifies the category of a customer support message.
- **Priority Detection:** Classifies messages as Low, Medium, or High priority.
- **Sentiment Analysis:** Identifies Positive, Neutral, or Negative sentiment.
- **Reply Generation:** Generates contextual replies using a large language model.
- **Basic Safety Checks:** Detects selected patterns that may indicate unsupported promises or claims.
- **Evaluation:** Tests classification performance using predefined test cases.
- **Interactive Interface:** Provides a user interface built with Streamlit.

## Technologies Used

- Python
- Streamlit
- Groq API
- Large Language Models (LLMs)
- JSON
- Regular Expressions

## Evaluation Results

The current evaluation used six predefined test cases.

| Metric | Result |
|---|---:|
| Successful API responses | 6/6 |
| Category accuracy | 100% |
| Priority accuracy | 100% |
| Sentiment accuracy | 100% |
| Fallback replacements | 0 |

These results apply only to the current test set and do not guarantee the same performance on unseen messages.

## Project Structure

```text
ai-customer-support-assistant/
├── app.py
├── support_logic.py
├── evaluate.py
├── evaluation_cases.py
├── evaluation_results.json
├── .gitignore
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/marimsedqy/ai-customer-support-assistant.git
cd ai-customer-support-assistant
```

### 2. Create and activate a virtual environment

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install the required packages

Install the dependencies used by the project:

```powershell
pip install streamlit groq python-dotenv
```

### 4. Configure the API key

Create a `.env` file in the project root and add your own Groq API key:

```text
GROQ_API_KEY=your_groq_api_key
```

Never commit your actual API key to GitHub.

### 5. Run the application

```powershell
streamlit run app.py
```

### 6. Run the evaluation

```powershell
python evaluate.py
```

## Safety and Limitations

- Generated replies are suggestions and require human review before being sent to customers.
- Safety checks use predefined patterns and may miss unsupported claims or flag legitimate wording.
- The application does not access real orders or perform refunds, replacements, cancellations, or other support actions.
- Evaluation results are based on a small predefined test set.

## Future Improvements

- Expand the evaluation dataset.
- Improve safety checks and reply-quality evaluation.
- Add more robust error handling.
- Integrate verified support policies and knowledge sources.
- Connect to authorized customer support systems when appropriate.

## Author

**Maryem Sedqy**

GitHub: [@marimsedqy](https://github.com/marimsedqy)