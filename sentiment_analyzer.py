#!/usr/bin/env python3
"""
Customer Feedback Sentiment & Summarization Processor
Powered by OpenRouter API (OpenAI Compatible SDK)

This script reads customer feedback comments from a CSV file,
uses OpenRouter API to analyze sentiment (positive, neutral, negative)
and produce a concise one-line summary for each comment,
then exports the enriched data to a new CSV file.
"""

import os
import sys
import csv
import json
import time
import argparse
from typing import List, Dict, Any, Tuple

# Optional dotenv support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Optional tqdm progress bar support
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# Import OpenAI SDK (used for OpenRouter)
try:
    from openai import OpenAI
except ImportError:
    print("Error: The 'openai' package is required for OpenRouter. Install it using:\n  pip install openai")
    sys.exit(1)


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"
ALTERNATIVE_MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.3-70b-instruct"
]
POSSIBLE_COMMENT_COLUMNS = ["comment", "comments", "feedback", "review", "text", "message"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process CSV customer feedback using OpenRouter API for sentiment analysis and summarization."
    )
    parser.add_argument(
        "-i", "--input",
        default="sample_feedback.csv",
        help="Path to input CSV file (default: sample_feedback.csv)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path to output CSV file (default: <input_filename>_processed.csv)"
    )
    parser.add_argument(
        "-c", "--column",
        default=None,
        help="Name of the CSV column containing customer feedback comments (autodetected if omitted)"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"OpenRouter model to use (default: {DEFAULT_MODEL}). Working alternatives: {', '.join(ALTERNATIVE_MODELS)}"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenRouter API Key (defaults to OPENROUTER_API_KEY environment variable)"
    )
    return parser.parse_args()


def detect_comment_column(fieldnames: List[str], target_column: str = None) -> str:
    """Find the column containing feedback text in the CSV."""
    clean_fieldnames = [f for f in fieldnames if f]
    if target_column:
        if target_column not in clean_fieldnames:
            raise ValueError(f"Specified column '{target_column}' not found in CSV. Available columns: {clean_fieldnames}")
        return target_column

    # Auto-detection
    for name in clean_fieldnames:
        if name.strip().lower() in POSSIBLE_COMMENT_COLUMNS:
            return name

    # Fallback to the first valid column if no match found
    print(f"Warning: Could not auto-detect comment column. Using first column: '{clean_fieldnames[0]}'")
    return clean_fieldnames[0]


def analyze_comment(client: OpenAI, comment: str, model: str) -> Tuple[str, str]:
    """
    Calls OpenRouter API to get sentiment classification and a one-line summary.
    Returns a tuple: (sentiment, summary)
    """
    if not comment or not comment.strip():
        return "neutral", "Empty comment provided."

    system_prompt = (
        "You are an expert customer feedback analyzer. "
        "Analyze the customer comment and respond ONLY with a JSON object containing two fields:\n"
        '1. "sentiment": must be strictly one of "positive", "neutral", or "negative".\n'
        '2. "summary": a concise, single-sentence summary (max 12 words) of the main point.'
    )

    prompt = f"Analyze this customer feedback:\n\"\"\"{comment.strip()}\"\"\""

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.0,
            max_tokens=150,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.choices[0].message.content.strip()
        
        # Clean up codeblock markers if present
        if response_text.startswith("```"):
            parts = response_text.split("```")
            if len(parts) > 1:
                response_text = parts[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

        data = json.loads(response_text)
        sentiment = str(data.get("sentiment", "neutral")).lower()
        if sentiment not in ["positive", "neutral", "negative"]:
            sentiment = "neutral"
        
        summary = str(data.get("summary", "")).strip()
        return sentiment, summary

    except json.JSONDecodeError:
        # Fallback if model returned plain text instead of JSON
        return "neutral", response_text[:100]
    except Exception as e:
        err_msg = str(e)
        if "404" in err_msg or "No endpoints found" in err_msg:
            print(f"\n[Model Error]: Model '{model}' not found on OpenRouter. Try -m openai/gpt-4o-mini or -m anthropic/claude-3-haiku")
        else:
            print(f"\n[Error analyzing comment]: {err_msg[:100]}")
        return "error", f"Processing error: {err_msg[:50]}"


def process_csv(input_path: str, output_path: str, column_name: str, model: str, api_key: str):
    """Main processing loop."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)

    # Initialize OpenAI Client configured for OpenRouter
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://github.com/your-username/customer-feedback-analyzer",
            "X-Title": "Customer Feedback Analyzer",
        }
    )

    # Read input CSV
    print(f"Reading '{input_path}'...")
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        raw_fieldnames = reader.fieldnames
        if not raw_fieldnames:
            print("Error: Input CSV file is empty or missing headers.")
            sys.exit(1)

        # Filter out None from fieldnames if header had extra trailing commas
        fieldnames = [f for f in raw_fieldnames if f is not None and f.strip() != ""]
        comment_col = detect_comment_column(fieldnames, column_name)
        rows = list(reader)

    print(f"Found {len(rows)} entries. Analyzing column: '{comment_col}' using OpenRouter model '{model}'...\n")

    # Output field names (strictly clean strings)
    out_fieldnames = list(fieldnames)
    if "sentiment" not in out_fieldnames:
        out_fieldnames.append("sentiment")
    if "summary" not in out_fieldnames:
        out_fieldnames.append("summary")

    processed_rows = []
    stats = {"positive": 0, "neutral": 0, "negative": 0, "error": 0}
    start_time = time.time()

    iterator = tqdm(rows, desc="Processing comments") if HAS_TQDM else rows

    for idx, row in enumerate(iterator):
        # Clean row dictionary from any None keys produced by DictReader on extra trailing commas
        clean_row = {k: v for k, v in row.items() if k is not None}

        comment_text = clean_row.get(comment_col, "")
        sentiment, summary = analyze_comment(client, comment_text, model)
        
        clean_row["sentiment"] = sentiment
        clean_row["summary"] = summary
        processed_rows.append(clean_row)

        stats[sentiment] = stats.get(sentiment, 0) + 1

        if not HAS_TQDM:
            print(f"[{idx+1}/{len(rows)}] Sentiment: {sentiment:<8} | Summary: {summary}")

    # Write output CSV
    print(f"\nWriting results to '{output_path}'...")
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    elapsed = round(time.time() - start_time, 2)

    # Summary Report
    print("=" * 50)
    print(" PROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print(f"Total Rows Processed: {len(processed_rows)}")
    print(f"Time Taken:           {elapsed} seconds")
    print("Sentiment Summary:")
    print(f"  - Positive: {stats['positive']}")
    print(f"  - Neutral:  {stats['neutral']}")
    print(f"  - Negative: {stats['negative']}")
    if stats['error'] > 0:
        print(f"  - Errors:   {stats['error']}")
    print(f"Output File Saved:   {os.path.abspath(output_path)}")
    print("=" * 50)


def main():
    args = parse_arguments()

    # Determine API Key (checks CLI arg, OPENROUTER_API_KEY, or fallback OPENAI_API_KEY)
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenRouter API Key is missing.")
        print("Please provide it via --api-key argument, or set OPENROUTER_API_KEY in environment or .env file.")
        sys.exit(1)

    # Determine Output Path
    if not args.output:
        base, ext = os.path.splitext(args.input)
        output_path = f"{base}_processed{ext}"
    else:
        output_path = args.output

    process_csv(
        input_path=args.input,
        output_path=output_path,
        column_name=args.column,
        model=args.model,
        api_key=api_key
    )


if __name__ == "__main__":
    main()
