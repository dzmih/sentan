# sentan

A small Python CLI tool I built for automating customer feedback analysis. It reads a CSV of comments, sends each one to an LLM via OpenRouter, and writes back the sentiment tag + a one-liner summary into a new CSV.

Useful when you have 50-200 short customer reviews and don't want to read through all of them manually.

---

## Stack

- Python 3.8+
- [OpenRouter API](https://openrouter.ai) (model-agnostic, tested with `openai/gpt-4o-mini` and `anthropic/claude-3-haiku`)
- `openai` SDK — OpenRouter is fully compatible with it
- `tqdm` for progress bar, `python-dotenv` for env management

---

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and paste your OpenRouter key:

```env
OPENROUTER_API_KEY=sk-or-v1-...
```

---

## Usage

Basic run with sample data:

```bash
python sentiment_analyzer.py --input sample_feedback.csv
```

With custom options:

```bash
python sentiment_analyzer.py \
  --input data/reviews.csv \
  --output data/reviews_analyzed.csv \
  --column "review_text" \
  --model "anthropic/claude-3-haiku"
```

The script auto-detects the comment column if it's named something like `comment`, `feedback`, `review`, or `text`. If your column has a different name, pass it with `--column`.

---

## Output

Adds two columns to the original CSV: `sentiment` (positive / neutral / negative) and `summary` (one sentence, ≤12 words).

Example from the included sample dataset:

| customer_name | comment | sentiment | summary |
|---|---|---|---|
| Sarah Jenkins | The product arrived two days early and worked right out of the box... | positive | Product arrived early and customer service was very helpful. |
| Elena Rostova | Totally disappointed. The item stopped working after 3 days... | negative | Item failed quickly and refund process was slow. |
| Michael Chang | Decent quality for the price but the user interface feels a bit dated... | neutral | Quality is decent, but the interface is outdated. |

Real run on 15 rows took ~16 seconds using `gpt-4o-mini`.

---

## Why OpenRouter

Didn't want to hardcode a single provider. With OpenRouter you can swap models in one flag — useful for comparing cost/quality or switching if a model goes down. Same `openai` SDK, different base URL.

---

## CLI reference

| Flag | Short | Default |
|---|---|---|
| `--input` | `-i` | `sample_feedback.csv` |
| `--output` | `-o` | `<input>_processed.csv` |
| `--column` | `-c` | auto-detect |
| `--model` | `-m` | `openai/gpt-4o-mini` |
| `--api-key` | | `$OPENROUTER_API_KEY` |

---

MIT License
