# Automated News Scraper & Rewriter

An autonomous Python-based pipeline that harvests real-time political news, processes it via Generative AI for original synthesis, and operates on a fully automated schedule.

## Overview

This project automates the lifecycle of digital news content. It targets CNN Politics to extract the latest updates, uses LLMs to rewrite them for uniqueness and clarity, and maintains a hands-off operation via task scheduling.

## Key Features

* **Real-time Ingestion**: Scrapes live headlines and articles specifically from the CNN Politics vertical.
* **AI Synthesis**: Leverages the Gemini API to perform semantic analysis and rewrite content, ensuring it is 100% original while maintaining factual integrity.
* **Structured Extraction**: Utilizes News4k and BeautifulSoup for high-precision parsing of HTML content.

## Tech Stack

* **Language**: Python 3.x
* **Scraping**: News4k, BeautifulSoup4, Requests
* **AI/LLM**: Google Gemini API

## Getting Started

### 1. Prerequisites

* Python 3.10+
* A Gemini API Key (Obtain from [Google AI Studio](https://ai.google.dev/))

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
