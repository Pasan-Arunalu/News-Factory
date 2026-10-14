# Automated News Scraper & Rewriter

An autonomous Python-based pipeline that harvests real-time political news, processes it via Generative AI for original synthesis, and operates on a fully automated schedule.

## Overview

This project automates the lifecycle of digital news content. It targets CNN Politics to extract the latest updates, uses LLMs to rewrite them for uniqueness and clarity, and maintains a hands-off operation via task scheduling.

## Key Features

- **Real-time Ingestion**: Scrapes live headlines and articles specifically from the CNN Politics vertical.
- **AI Synthesis**: Leverages the Gemini API to perform semantic analysis and rewrite content, ensuring it is 100% original while maintaining factual integrity.
- **Structured Extraction**: Utilizes News4k and BeautifulSoup for high-precision parsing of HTML content.

## Tech Stack

- **Language**: Python 3.x
- **Scraping**: News4k, BeautifulSoup4, Requests
- **AI/LLM**: Google Gemini API

## Getting Started

### 1. Prerequisites

- Python 3.10+
- A Gemini API Key (Obtain from [Google AI Studio](https://ai.google.dev/))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/news-scraper-rewriter.git

# Navigate to the directory
cd news-scraper-rewriter

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory and add your API credentials:

```
GEMINI_API_KEY=your_api_key_here
```

### 4. Usage

To execute the scraping and rewriting cycle manually:

```bash
python main.py
```

# NewsScraper & AI Editorial Rewriter

A modular backend for automated international news ingestion, analysis, and editorial generation.

## Architecture

This project uses a modular pipeline:

1. **Ingestion**: Fetches URLs from sources (e.g., CNN Politics) and normalizes them.
2. **Extraction**: Uses Playwright to bypass Cloudflare, and `newspaper3k` to extract article text.
3. **Clustering & Deduplication**: Avoids processing the same story twice using hashes and basic clustering.
4. **Intelligence**: Feeds multiple articles of a Story to Gemini to extract a structured JSON report (facts, claims, entities).
5. **Editorial Generation**: Generates platform-specific drafts (e.g., Facebook posts) using the intelligence report.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Configuration:
   Copy `.env.example` to `.env` and fill in your variables:

   ```env
   GEMINI_API_KEY=your_key
   DATABASE_URL=sqlite:///news_data_v2.db
   ```

3. Initialize Database:
   ```bash
   python -m app.main init
   ```

## Running the Pipeline

You can run individual steps or the full pipeline:

```bash
# Ingest new links
python -m app.main ingest

# Extract HTML and text
python -m app.main extract

# Cluster into Stories
python -m app.main cluster

# Run Gemini Analysis
python -m app.main analyze

# Generate Editorial Drafts (e.g., Facebook)
python -m app.main generate

# Check pipeline health and source metrics
python -m app.main health

# Run everything sequentially
python -m app.main run
```

## Adding a New Source

To add a new news source:

1. Create a class inheriting from `BaseSource` in `app/sources/`.
2. For HTML sources, implement `discover_articles`.
3. For RSS sources, simply inherit from `RSSSource` and define the fields.
4. Add the source to `PipelineRunner` in `app/services/pipeline.py`.
