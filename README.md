# Customer Feedback Sentiment & Summarization Processor

A lightweight, production-ready Python CLI tool that ingests customer feedback CSV exports, analyzes sentiment (`positive`, `neutral`, `negative`), and produces crisp 1-line summaries using **OpenRouter API**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![OpenRouter](https://img.shields.io/badge/API-OpenRouter-purple)
![OpenAI SDK](https://img.shields.io/badge/SDK-OpenAI-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 🌟 Key Features

- **Multi-Model Flexibility**: Uses OpenRouter API to seamlessly switch between GPT-4o Mini, Claude 3, Llama 3.3, DeepSeek, and Gemini without changing code.
- **Smart Column Auto-Detection**: Automatically identifies comment text in columns named `comment`, `feedback`, `review`, `text`, or `message`.
- **Structured JSON Output**: Enforces strict JSON responses with system prompts for consistent sentiment classification and length-capped summaries.
- **Robust CSV Handling**: Safely parses uneven CSV files, handling trailing commas and missing headers without crashing.
- **Terminal UI & Progress Bar**: Real-time visual progress bar via `tqdm` with automatic fallback to clean console logs.

---

## 🤔 Why OpenRouter?

- **Model Agnostic**: Access 100+ LLM providers using a single standardized API format (`openai` SDK).
- **Cost & Speed Optimization**: Easily test and deploy cheaper/faster models (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`, or `deepseek/deepseek-chat`).
- **No Provider Lock-in**: Switch models on the fly via the command line (`-m / --model`).

---

## 📁 Repository Structure

```
├── sentiment_analyzer.py          # Main Python script (OpenRouter / OpenAI SDK)
├── sample_feedback.csv            # Sample input dataset (15 customer comments)
├── sample_feedback_processed.csv  # Verified sample output dataset
├── requirements.txt               # Dependencies (openai, python-dotenv, tqdm)
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules (protects API keys)
└── README.md                      # Documentation & portfolio overview
```

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/your-username/customer-feedback-analyzer.git
cd customer-feedback-analyzer

pip install -r requirements.txt
```

### 2. Configure OpenRouter API Key

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Add your OpenRouter key to `.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-your_openrouter_api_key_here
```

### 3. Run the Script

Process the sample dataset using default settings (`openai/gpt-4o-mini`):

```bash
python sentiment_analyzer.py --input sample_feedback.csv
```

Or specify a custom model or input file:

```bash
python sentiment_analyzer.py \
  --input custom_data.csv \
  --output analyzed_data.csv \
  --column "customer_review" \
  --model "anthropic/claude-3-haiku"
```

---

## 📊 Real Execution Example

### Terminal Output
```text
Reading 'sample_feedback.csv'...
Found 15 entries. Analyzing column: 'comment' using OpenRouter model 'openai/gpt-4o-mini'...

Processing comments: 100%|█████████████████████████████████████████████| 15/15 [00:15<00:00, 1.06it/s]

Writing results to 'sample_feedback_processed.csv'...
==================================================
 PROCESSING COMPLETED SUCCESSFULLY
==================================================
Total Rows Processed: 15
Time Taken:           15.93 seconds
Sentiment Summary:
  - Positive: 6
  - Neutral:  3
  - Negative: 6
Output File Saved:   .../sample_feedback_processed.csv
==================================================
```

### Sample Data Preview (`sample_feedback_processed.csv`)

| id | customer_name | comment | sentiment | summary |
|---|---|---|---|---|
| 1 | Sarah Jenkins | The product arrived two days early and worked right out of the box!... | `positive` | Product arrived early and customer service was very helpful. |
| 2 | Michael Chang | Decent quality for the price but the user interface feels a bit dated... | `neutral` | Quality is decent, but the interface is outdated. |
| 3 | Elena Rostova | Totally disappointed. The item stopped working after 3 days... | `negative` | Item failed quickly and refund process was slow. |
| 7 | Laura Martinez | The software crashes frequently after the latest v2.4 update... | `negative` | Software frequently crashes after the latest update. |
| 11 | Chloe Bennett | Outstanding support team! They solved my issue in under 10 minutes... | `positive` | Support team resolved issue quickly via live chat. |

---

## 🛠️ CLI Options

| Argument | Short | Description | Default |
|---|---|---|---|
| `--input` | `-i` | Input CSV file path | `sample_feedback.csv` |
| `--output` | `-o` | Output CSV file path | `<input_basename>_processed.csv` |
| `--column` | `-c` | CSV feedback column name | Auto-detected |
| `--model` | `-m` | OpenRouter model ID | `openai/gpt-4o-mini` |
| `--api-key` | | Pass API key via CLI | `$OPENROUTER_API_KEY` |

---

## 📄 License

MIT License. Free to use for personal or commercial projects.
