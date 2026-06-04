# 🚀 100 Useful Python Automation Tools

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tools](https://img.shields.io/badge/Tools-100-00D084?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0yMiA5VjdoLTJWNWMwLTEuMS0uOS0yLTItMkg0Yy0xLjEgMC0yIC45LTIgMnYxNGMwIDEuMS45IDIgMiAyaDE2YzEuMSAwIDItLjkgMi0ydi0yaDJWOWgtMlptLTIgMTBINFY1aDE2djE0ek02IDEzaDJ2Mmgteno\
iTTEwIDEzaDJ2Mmgteno\niTMgMTNoMnYyaC0yeiIvPjwvc3ZnPg==)
![Stars](https://img.shields.io/github/stars/VARSHAN69/100-useful-tools?style=for-the-badge&color=FFD700)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![NEET](https://img.shields.io/badge/NEET%202026-June%2021-FF4500?style=for-the-badge&logo=target)

**Built by a 1st-year AI/ML & CSE student. 100 genuinely useful Python tools for developers, students, and professionals.**

[🚀 Quick Start](#-quick-start) • [📦 All 100 Tools](#-all-100-tools) • [🤖 AI-Powered Tools](#-category-4-ai--ml-tools-61-80) • [📚 Study Tools](#-category-5-study--exam-prep-81-100)

</div>

---

## ✨ What is this?

A collection of **100 standalone Python CLI tools** covering:
- 📁 **File & Media Automation** — rename, organize, convert, encrypt
- 🌐 **Web & Network** — scrape, monitor, test, analyze
- ⚙️ **System & Productivity** — timers, trackers, schedulers
- 🤖 **AI & ML** — Gemini-powered tools, data science demos
- 📚 **Study & Exam Prep** — flashcards, NEET countdown, AI tutor

> Each tool is **self-contained**, uses the `rich` library for beautiful terminal output, and can be run individually or via the interactive launcher.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/VARSHAN69/100-useful-tools.git
cd 100-useful-tools
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Interactive Menu
```bash
python runner.py
```

### 4. Or Run Any Tool Directly
```bash
python file_media/01_bulk_rename.py
python web_network/34_weather_cli.py
python study_exam/86_neet_countdown.py
```

### 5. Set Up Gemini API (for AI tools 61-90)
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```
Get your free API key at [aistudio.google.com](https://aistudio.google.com)

---

## 📦 All 100 Tools

### 📁 Category 1: File & Media Automation (01-20)

| # | Tool | What It Does |
|---|------|-------------|
| 01 | **Bulk File Renamer** | Rename hundreds of files with prefix/suffix, sequential numbering, date stamps, text replacement, or extension change |
| 02 | **Duplicate File Finder** | Scan folders by MD5 hash, identify exact duplicates, show wasted space, bulk delete |
| 03 | **Smart Folder Organizer** | Auto-sort messy Downloads into Images, Videos, Audio, Documents, Code, Archives subfolders |
| 04 | **PDF Toolkit** | Merge multiple PDFs, split by page range, extract all text to .txt |
| 05 | **Image Batch Processor** | Convert formats, resize batches, add watermarks, compress with quality control |
| 06 | **QR Code Generator** | Generate QR for URLs, WiFi credentials, contact vCards, emails with custom colors |
| 07 | **File Encryptor/Decryptor** | AES-256 password-based encryption and decryption for any file |
| 08 | **Text-to-Speech** | Convert text files or typed text to MP3 audio with voice/speed/volume control |
| 09 | **Clipboard Manager** | Track clipboard history (last 50 items), search, recall any past copy |
| 10 | **Disk Space Analyzer** | Visualize folder sizes, find largest files, file type distribution |
| 11 | **YouTube Downloader** | Download videos (MP4) or extract audio (MP3) using yt-dlp |
| 12 | **Screenshot Scheduler** | Auto-capture screenshots at configurable intervals for time-lapses |
| 13 | **Markdown to HTML** | Convert `.md` files to beautiful dark-themed HTML pages |
| 14 | **Random Data Generator** | Generate realistic fake data (names, emails, IPs, addresses) as JSON/CSV |
| 15 | **Smart Note Taker** | Create tagged notes, search, export to markdown |
| 16 | **CSV Analyzer** | Load CSV, filter/sort rows, show statistics, plot histograms |
| 17 | **Password Generator** | Generate secure passwords, check strength, create memorable passphrases |
| 18 | **JSON Toolkit** | Format, validate, minify, and query JSON data with dot notation |
| 19 | **Code Line Counter** | Count LOC, comments, blanks per language across entire projects |
| 20 | **Regex Tester** | Test patterns interactively, extract/replace matches, built-in presets |

---

### 🌐 Category 2: Web & Network (21-40)

| # | Tool | What It Does |
|---|------|-------------|
| 21 | **Website Health Monitor** | Check uptime, SSL validity, response time; continuous ping monitor |
| 22 | **Web Scraper** | Extract titles, links, images, headings, meta tags from any URL |
| 23 | **API Tester** | Make REST API calls (GET/POST/PUT/DELETE) with custom headers, auth, body |
| 24 | **Internet Speed Test** | Measure download/upload speed and ping via speedtest-cli |
| 25 | **Port Scanner** | Threaded TCP port scanner with service name detection |
| 26 | **Network Info Dashboard** | Show local/public IP, MAC, DNS, gateway, all network interfaces |
| 27 | **URL Shortener/Expander** | Shorten URLs with TinyURL or expand shortened links to reveal destination |
| 28 | **Email Validator** | Check syntax, MX records, disposable domains, role-based addresses |
| 29 | **HTTP Header Analyzer** | Audit security headers (HSTS, CSP, X-Frame-Options), rate website security |
| 30 | **WHOIS Lookup** | Domain registration info, expiry date, name servers, availability check |
| 31 | **Ping Sweep** | Threaded sweep of IP ranges to find alive hosts on your network |
| 32 | **DNS Lookup** | Query A, AAAA, MX, NS, TXT, CNAME records for any domain |
| 33 | **RSS Reader** | Parse and display articles from any RSS/Atom feed with open-in-browser |
| 34 | **Weather CLI** | Current weather and 3-day forecast for any city using wttr.in (no API key!) |
| 35 | **GitHub Profile Analyzer** | Analyze GitHub profiles: repos, languages, stars, forks, contributions |
| 36 | **Web Link Checker** | Crawl a webpage and report all broken/dead hyperlinks |
| 37 | **IP Geolocation** | Look up location, ISP, timezone, country for any IP address |
| 38 | **HTTP Load Tester** | Concurrent HTTP requests to test endpoint performance and RPS |
| 39 | **Tech Stack Detector** | Detect CMS, frameworks, analytics, CDN from website headers/HTML |
| 40 | **News Aggregator** | Fetch top headlines by topic, keyword search across RSS sources |

---

### ⚙️ Category 3: System & Productivity (41-60)

| # | Tool | What It Does |
|---|------|-------------|
| 41 | **System Monitor** | Live CPU%, RAM, disk, network I/O, top processes dashboard with auto-refresh |
| 42 | **Process Manager** | Interactive process list sorted by CPU/RAM, search and kill processes |
| 43 | **Task Scheduler** | Add recurring scripts/commands with interval scheduling, persist to JSON |
| 44 | **Pomodoro Timer** | 25min work + 5min break Pomodoro with desktop notifications and session log |
| 45 | **Habit Tracker** | Daily habits, streaks, weekly grid, motivational stats |
| 46 | **TODO Manager** | Tasks with priorities (HIGH/MEDIUM/LOW), due dates, categories, full CLI |
| 47 | **Expense Tracker** | Log expenses, monthly summaries, category breakdown, budget tracking |
| 48 | **Time Tracker** | Start/stop timer per task, daily/weekly productivity reports |
| 49 | **Focus Timer** | Deep focus sessions, track interruptions, focus quality score |
| 50 | **Battery Monitor** | Battery level, estimated time remaining, charging status, low-battery alerts |
| 51 | **Clipboard History Search** | Monitor clipboard, index by type (URL/code/email/text), full-text search |
| 52 | **File Watcher** | Watch folder for file changes, log events, run command on change |
| 53 | **Startup Manager** | List and analyze startup programs with impact ratings (Windows) |
| 54 | **Color Picker** | Convert HEX/RGB/HSL/HSV, generate complementary colors, copy color codes |
| 55 | **ASCII Art Generator** | Convert text to ASCII art with pyfiglet fonts; images to ASCII |
| 56 | **Unit Converter** | Length, weight, temperature, area, speed, data size conversions |
| 57 | **Countdown Timer** | Live countdown to exam dates with rich.live real-time display |
| 58 | **Random Decider** | Coin flip, dice (d4/d6/d8/d20), random name picker, spin wheel |
| 59 | **Clipboard Formatter** | Apply text transformations (case, wrap, deduplicate) to clipboard content |
| 60 | **System Info Report** | Full hardware/software report: OS, CPU, RAM, GPU, Python, network |

---

### 🤖 Category 4: AI & ML Tools (61-80)

> 🔑 Tools 61-79 require `GEMINI_API_KEY`. Get yours free at [aistudio.google.com](https://aistudio.google.com)

| # | Tool | What It Does |
|---|------|-------------|
| 61 | **Gemini AI Chatbot** | Multi-turn conversational chatbot powered by Google Gemini |
| 62 | **AI Text Summarizer** | Summarize articles, papers, files with adjustable detail level |
| 63 | **AI Code Explainer** | Get plain-English explanations of any code, line-by-line mode |
| 64 | **Sentiment Analyzer** | Analyze text sentiment (positive/negative/neutral) with confidence |
| 65 | **AI Idea Generator** | Generate startup, project, app, or research ideas based on your interests |
| 66 | **AI Bug Detector** | Find bugs in Python/JS code, explain issues, get fix suggestions |
| 67 | **Resume Analyzer** | Match resume vs job description, get compatibility score and improvement tips |
| 68 | **Essay Grader** | Grade essays on clarity, structure, grammar with rubric scores and feedback |
| 69 | **Interview Prep Coach** | AI mock interview for CS, ML, DSA, or HR rounds with live feedback |
| 70 | **Learning Roadmap AI** | Get a structured weekly/monthly learning plan for any skill |
| 71 | **Data Visualizer** | Load CSV, auto-detect column types, generate smart charts |
| 72 | **Digit Classifier Demo** | KNN/SVM digit recognition demo on sklearn digits dataset |
| 73 | **Text Clustering** | TF-IDF + KMeans clustering of text inputs, visualize clusters |
| 74 | **Stock Analyzer** | Historical price data, moving averages, RSI indicator, trend plots |
| 75 | **Linear Regression Demo** | Interactive regression with data input, plot, R² score, equation |
| 76 | **Word Frequency Analyzer** | Top words, frequency stats, stopword removal for any text |
| 77 | **AI Translation Tool** | Translate text to any language with source language auto-detection |
| 78 | **Grammar Checker** | AI grammar, style, and readability analysis with corrected version |
| 79 | **Equation Solver** | Solve linear, quadratic, and systems of equations step-by-step (sympy) |
| 80 | **Dataset Profiler** | Full data quality report: missing values, outliers, correlations, HTML export |

---

### 📚 Category 5: Study & Exam Prep (81-100)

> 🎯 Specially designed for NEET 2026 prep and competitive exam students!

| # | Tool | What It Does |
|---|------|-------------|
| 81 | **Flashcard Maker** | Create Q&A flashcard decks, quiz with spaced repetition, track scores |
| 82 | **MCQ Quiz Engine** | NEET/JEE-style timed MCQ quizzes from JSON question banks |
| 83 | **Formula Sheet Manager** | Physics/Chemistry/Math formula database with topic search |
| 84 | **Study Planner** | Generate day-by-day study schedule based on exam date and subjects |
| 85 | **AI Subject Tutor** | Ask any Physics/Chemistry/Biology/Math question to Gemini AI |
| 86 | **NEET Countdown** | Live countdown to NEET 2026 (June 21) with daily motivation |
| 87 | **Concept Mapper** | Build concept relationship maps, navigate hierarchically |
| 88 | **PYQ Analyzer** | NEET/JEE previous year question topic-wise frequency analysis |
| 89 | **Mock Test Generator** | AI-generated NEET-style MCQs with 4 options and explanations |
| 90 | **Revision Notes AI** | Structured chapter revision notes with key points and mnemonics |
| 91 | **Periodic Table CLI** | Interactive element lookup with full properties by symbol/name |
| 92 | **Math Practice Generator** | Timed random math problems (arithmetic to calculus), track accuracy |
| 93 | **Biology Glossary** | 200+ biology terms by system, search, add custom, quiz mode |
| 94 | **Citation Generator** | APA/MLA/Chicago citation formatter from paper title/URL/DOI |
| 95 | **Memory Palace Builder** | Create virtual memory palaces and associate facts to locations |
| 96 | **Speed Reading Trainer** | RSVP technique trainer with WPM control and comprehension quiz |
| 97 | **Error Log Analyzer** | Track test mistakes, identify weak topics, targeted revision suggestions |
| 98 | **Vocabulary Builder** | Daily science/GRE words with etymology, usage examples, quiz mode |
| 99 | **Mind Dump** | Timed free-writing brain dump + AI summary of key ideas |
| 100 | **Motivational Dashboard** | Streak, study hours, NEET countdown, daily quote, study tip |

---

## 🛠️ Tech Stack

| Library | Used For |
|---------|----------|
| `rich` | All terminal UI, tables, progress bars, panels |
| `requests` + `BeautifulSoup4` | Web scraping and API calls |
| `psutil` | System monitoring, process management |
| `Pillow` | Image processing and conversion |
| `yt-dlp` | YouTube downloading |
| `google-generativeai` | All Gemini AI-powered tools |
| `pandas` + `matplotlib` | Data analysis and visualization |
| `sklearn` | ML demos (clustering, classification) |
| `PyPDF2` | PDF manipulation |
| `qrcode` | QR code generation |
| `pyttsx3` | Text-to-speech conversion |
| `schedule` | Task scheduling |
| `sympy` | Symbolic math equation solving |

---

## 📂 Project Structure

```
100-tools/
├── runner.py               # 🚀 Interactive launcher (start here!)
├── requirements.txt        # All dependencies
│
├── file_media/             # Tools 01-20
│   ├── 01_bulk_rename.py
│   ├── 02_duplicate_finder.py
│   └── ...
│
├── web_network/            # Tools 21-40
│   ├── 21_website_monitor.py
│   └── ...
│
├── system_productivity/    # Tools 41-60
│   ├── 41_system_monitor.py
│   └── ...
│
├── ai_ml/                  # Tools 61-80
│   ├── 61_gemini_chat.py
│   └── ...
│
└── study_exam/             # Tools 81-100
    ├── 81_flashcard_maker.py
    ├── 86_neet_countdown.py
    └── ...
```

---

## 🤝 Contributing

Found a bug or want to add a tool? PRs are welcome!

1. Fork the repo
2. Create a branch: `git checkout -b feature/tool-name`
3. Add your tool following the existing style
4. Submit a PR

---

## 📄 License

MIT License — use freely, credit appreciated.

---

## 👨‍💻 About

Built by **[Varshan](https://github.com/VARSHAN69)** — 1st year CSE + AI/ML student, building tools while preparing for NEET 2026.

> *"The best way to learn is to build."*

⭐ **Star this repo if any tool saved you time!**

