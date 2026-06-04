"""
🚀 100 Useful Python Automation Tools
Interactive Launcher - Run any of the 100 tools from a single menu
Author: Varshan | AI/ML & CSE Student
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns
from rich import box
from rich.text import Text

console = Console()

BASE = Path(__file__).parent

TOOLS = [
    # Category 1: File & Media (01-20)
    ("01", "Bulk File Renamer",         "file_media/01_bulk_rename.py",          "📁 Rename hundreds of files with smart patterns"),
    ("02", "Duplicate File Finder",     "file_media/02_duplicate_finder.py",     "🔍 Find & remove exact duplicate files by MD5"),
    ("03", "Smart Folder Organizer",    "file_media/03_folder_organizer.py",     "📂 Auto-sort files into subfolders by type"),
    ("04", "PDF Toolkit",               "file_media/04_pdf_toolkit.py",          "📄 Merge, split, extract text from PDFs"),
    ("05", "Image Batch Processor",     "file_media/05_image_batch.py",          "🖼️  Convert, resize, watermark images in bulk"),
    ("06", "QR Code Generator",         "file_media/06_qr_generator.py",         "📲 Generate QR for URLs, WiFi, contacts"),
    ("07", "File Encryptor/Decryptor",  "file_media/07_file_encrypt.py",         "🔒 AES-256 password-based file encryption"),
    ("08", "Text-to-Speech",            "file_media/08_text_to_speech.py",       "🔊 Convert text or files to MP3 audio"),
    ("09", "Clipboard Manager",         "file_media/09_clipboard_manager.py",    "📋 Track, search, and recall clipboard history"),
    ("10", "Disk Space Analyzer",       "file_media/10_disk_analyzer.py",        "💾 Visualize folder sizes & find large files"),
    ("11", "YouTube Downloader",        "file_media/11_youtube_downloader.py",   "📺 Download videos/audio from YouTube"),
    ("12", "Screenshot Scheduler",      "file_media/12_screenshot_scheduler.py", "📸 Auto-capture screenshots at set intervals"),
    ("13", "Markdown to HTML",          "file_media/13_markdown_to_html.py",     "📝 Convert MD files to styled dark HTML"),
    ("14", "Random Data Generator",     "file_media/14_data_generator.py",       "🎲 Generate realistic fake data (JSON/CSV)"),
    ("15", "Smart Note Taker",          "file_media/15_note_taker.py",           "📓 Notes with tags, search, markdown export"),
    ("16", "CSV Analyzer",              "file_media/16_csv_analyzer.py",         "📊 Filter, stats, and plot CSV data"),
    ("17", "Password Generator",        "file_media/17_password_generator.py",   "🔑 Generate secure passwords, check strength"),
    ("18", "JSON Toolkit",              "file_media/18_json_toolkit.py",         "📋 Format, validate, minify, query JSON"),
    ("19", "Code Line Counter",         "file_media/19_loc_counter.py",          "📏 Count LOC across your entire project"),
    ("20", "Regex Tester",              "file_media/20_regex_tester.py",         "🔍 Test regex patterns, extract/replace matches"),

    # Category 2: Web & Network (21-40)
    ("21", "Website Health Monitor",    "web_network/21_website_monitor.py",     "🌐 Check uptime, SSL, response time for URLs"),
    ("22", "Web Scraper",               "web_network/22_web_scraper.py",         "🕷️  Extract links, images, headings from pages"),
    ("23", "API Tester",                "web_network/23_api_tester.py",          "⚡ Test REST APIs with custom headers & body"),
    ("24", "Internet Speed Test",       "web_network/24_speed_test.py",          "🚀 Measure download/upload speed & ping"),
    ("25", "Port Scanner",              "web_network/25_port_scanner.py",        "🔌 Scan open TCP ports on any host"),
    ("26", "Network Info Dashboard",    "web_network/26_network_info.py",        "📡 Show local IP, public IP, interfaces"),
    ("27", "URL Shortener/Expander",    "web_network/27_url_shortener.py",       "🔗 Shorten URLs or expand shortened links"),
    ("28", "Email Validator",           "web_network/28_email_validator.py",     "✉️  Validate emails: syntax, MX, disposable"),
    ("29", "HTTP Header Analyzer",      "web_network/29_http_header_analyzer.py","🛡️  Analyze HTTP security headers, rate security"),
    ("30", "WHOIS Lookup",              "web_network/30_whois_lookup.py",        "🔎 Domain registration & availability lookup"),
    ("31", "Ping Sweep",                "web_network/31_ping_sweep.py",          "📡 Sweep IP range, find alive hosts"),
    ("32", "DNS Lookup",                "web_network/32_dns_lookup.py",          "🌍 Query A/MX/NS/TXT DNS records"),
    ("33", "RSS Reader",                "web_network/33_rss_reader.py",          "📰 Read and display RSS/Atom news feeds"),
    ("34", "Weather CLI",               "web_network/34_weather_cli.py",         "🌤️  Current weather & 3-day forecast (no API key)"),
    ("35", "GitHub Profile Analyzer",   "web_network/35_github_profile_analyzer.py","🐙 Analyze GitHub profiles, repos, languages"),
    ("36", "Web Link Checker",          "web_network/36_web_link_checker.py",    "🔗 Find broken links on any webpage"),
    ("37", "IP Geolocation",            "web_network/37_ip_geolocation.py",      "📍 Geolocate any IP: country, city, ISP"),
    ("38", "HTTP Load Tester",          "web_network/38_http_load_tester.py",    "💥 Concurrent HTTP load test, measure RPS"),
    ("39", "Tech Stack Detector",       "web_network/39_tech_stack_detector.py", "🔬 Detect CMS, frameworks, analytics on sites"),
    ("40", "News Aggregator",           "web_network/40_news_aggregator.py",     "📡 Fetch top news headlines by topic"),

    # Category 3: System & Productivity (41-60)
    ("41", "System Monitor",            "system_productivity/41_system_monitor.py",   "💻 Real-time CPU/RAM/disk/network dashboard"),
    ("42", "Process Manager",           "system_productivity/42_process_manager.py",  "⚙️  List, search, kill processes interactively"),
    ("43", "Task Scheduler",            "system_productivity/43_task_scheduler.py",   "⏰ Schedule recurring Python scripts/commands"),
    ("44", "Pomodoro Timer",            "system_productivity/44_pomodoro_timer.py",   "🍅 25+5 min Pomodoro with notifications"),
    ("45", "Habit Tracker",             "system_productivity/45_habit_tracker.py",    "✅ Daily habits, streaks, weekly progress grid"),
    ("46", "TODO Manager",              "system_productivity/46_todo_manager.py",     "📝 Tasks with priorities, due dates, categories"),
    ("47", "Expense Tracker",           "system_productivity/47_expense_tracker.py",  "💰 Log expenses, monthly summaries, budgets"),
    ("48", "Time Tracker",              "system_productivity/48_time_tracker.py",     "⏱️  Track work time per task, daily reports"),
    ("49", "Focus Timer",               "system_productivity/49_focus_timer.py",      "🎯 Deep focus sessions with interruption tracking"),
    ("50", "Battery Monitor",           "system_productivity/50_battery_monitor.py",  "🔋 Battery level, health, charge time alerts"),
    ("51", "Clipboard History Search",  "system_productivity/51_clipboard_history_search.py","📋 Monitor, index, search clipboard by type"),
    ("52", "File Watcher",              "system_productivity/52_file_watcher.py",     "👁️  Watch folder for changes, run on-change cmd"),
    ("53", "Startup Manager",           "system_productivity/53_startup_manager.py",  "🚀 List & analyze startup programs/impact"),
    ("54", "Color Picker",              "system_productivity/54_color_picker.py",     "🎨 Convert HEX/RGB/HSL, find complementary"),
    ("55", "ASCII Art Generator",       "system_productivity/55_ascii_art_generator.py","🎭 Convert text/images to ASCII art"),
    ("56", "Unit Converter",            "system_productivity/56_unit_converter.py",   "📐 Convert length, weight, temp, data, speed"),
    ("57", "Countdown Timer",           "system_productivity/57_countdown_timer.py",  "⏳ Live countdown to exam dates/deadlines"),
    ("58", "Random Decider",            "system_productivity/58_random_decider.py",   "🎲 Coin flip, dice roll, spin wheel of options"),
    ("59", "Clipboard Formatter",       "system_productivity/59_clipboard_formatter.py","✏️  Transform clipboard: case, spacing, wrap"),
    ("60", "System Info Report",        "system_productivity/60_system_info.py",      "🖥️  Full system report: OS, CPU, RAM, GPU"),

    # Category 4: AI & ML (61-80)
    ("61", "Gemini AI Chatbot",         "ai_ml/61_gemini_chat.py",       "🤖 Multi-turn Gemini AI conversation"),
    ("62", "AI Text Summarizer",        "ai_ml/62_text_summarizer.py",   "📝 Summarize articles, papers, files with AI"),
    ("63", "AI Code Explainer",         "ai_ml/63_code_explainer.py",    "💡 Get plain-English explanations of any code"),
    ("64", "Sentiment Analyzer",        "ai_ml/64_sentiment_analyzer.py","😊 Analyze text sentiment with confidence scores"),
    ("65", "AI Idea Generator",         "ai_ml/65_idea_generator.py",    "💡 Generate startup/project/research ideas"),
    ("66", "AI Bug Detector",           "ai_ml/66_bug_detector.py",      "🐛 Find bugs in code, get AI fix suggestions"),
    ("67", "Resume Analyzer",           "ai_ml/67_resume_analyzer.py",   "📄 Match resume vs job description, get tips"),
    ("68", "Essay Grader",              "ai_ml/68_essay_grader.py",      "📝 Grade essays with rubric and AI feedback"),
    ("69", "Interview Prep Coach",      "ai_ml/69_interview_prep.py",    "🎤 AI mock interview for CS/ML/DSA/HR"),
    ("70", "Learning Roadmap AI",       "ai_ml/70_learning_roadmap.py",  "🗺️  Generate structured learning roadmaps"),
    ("71", "Data Visualizer",           "ai_ml/71_data_visualizer.py",   "📈 Auto-visualize CSV data with smart charts"),
    ("72", "Digit Classifier Demo",     "ai_ml/72_number_classifier.py", "🔢 KNN/SVM digit recognition demo with sklearn"),
    ("73", "Text Clustering",           "ai_ml/73_text_clustering.py",   "🗂️  Cluster text inputs with TF-IDF + KMeans"),
    ("74", "Stock Analyzer",            "ai_ml/74_stock_analyzer.py",    "📈 Analyze stock prices, trends, MA, RSI"),
    ("75", "Linear Regression Demo",    "ai_ml/75_linear_regression_demo.py","📉 Interactive linear regression with plots"),
    ("76", "Word Frequency Analyzer",   "ai_ml/76_word_frequency.py",    "📊 Top words, frequency stats, stopword removal"),
    ("77", "AI Translation Tool",       "ai_ml/77_translation_tool.py",  "🌍 Translate text to any language with Gemini"),
    ("78", "Grammar Checker",           "ai_ml/78_grammar_checker.py",   "✍️  AI grammar, style, and readability checker"),
    ("79", "Equation Solver",           "ai_ml/79_equation_solver.py",   "🧮 Solve linear, quadratic, systems step-by-step"),
    ("80", "Dataset Profiler",          "ai_ml/80_dataset_profiler.py",  "🔬 Full data quality report for CSV datasets"),

    # Category 5: Study & Exam Prep (81-100)
    ("81", "Flashcard Maker",           "study_exam/81_flashcard_maker.py",          "🃏 Q&A flashcards with spaced repetition"),
    ("82", "MCQ Quiz Engine",           "study_exam/82_mcq_quiz.py",                 "📝 NEET/JEE-style timed MCQ quizzes"),
    ("83", "Formula Sheet Manager",     "study_exam/83_formula_sheet.py",            "⚗️  Physics/Chemistry/Math formula database"),
    ("84", "Study Planner",             "study_exam/84_study_planner.py",            "📅 Day-by-day exam study schedule generator"),
    ("85", "AI Subject Tutor",          "study_exam/85_ai_tutor.py",                 "🎓 Ask Physics/Chem/Bio/Math questions to AI"),
    ("86", "NEET Countdown",            "study_exam/86_neet_countdown.py",           "⏱️  NEET 2026 countdown with daily motivation"),
    ("87", "Concept Mapper",            "study_exam/87_concept_mapper.py",           "🗺️  Build and navigate concept relationship maps"),
    ("88", "PYQ Analyzer",              "study_exam/88_previous_year_analyzer.py",   "📊 NEET/JEE topic-wise frequency analysis"),
    ("89", "Mock Test Generator",       "study_exam/89_mock_test_generator.py",      "🤖 AI-generated NEET-style MCQ mock tests"),
    ("90", "Revision Notes AI",         "study_exam/90_revision_notes_ai.py",        "📖 AI-generated structured revision notes"),
    ("91", "Periodic Table CLI",        "study_exam/91_periodic_table.py",           "⚗️  Interactive periodic table element lookup"),
    ("92", "Math Practice Generator",   "study_exam/92_math_practice.py",            "🔢 Random math problems with timer & scoring"),
    ("93", "Biology Glossary",          "study_exam/93_biology_glossary.py",         "🧬 200+ biology terms, search, quiz yourself"),
    ("94", "Citation Generator",        "study_exam/94_citation_generator.py",       "📚 Generate APA/MLA/Chicago citations"),
    ("95", "Memory Palace Builder",     "study_exam/95_memory_palace.py",            "🏛️  Create and navigate memory palaces"),
    ("96", "Speed Reading Trainer",     "study_exam/96_speed_reading.py",            "⚡ RSVP speed reading with comprehension quiz"),
    ("97", "Error Log Analyzer",        "study_exam/97_error_log_analyzer.py",       "❌ Track mistakes, find weak topics, improve"),
    ("98", "Vocabulary Builder",        "study_exam/98_vocabulary_builder.py",       "📖 Daily science/GRE vocabulary with quiz"),
    ("99", "Mind Dump",                 "study_exam/99_mind_dump.py",                "🧠 Timed brain dump + AI key idea summary"),
    ("100","Motivational Dashboard",    "study_exam/100_motivational_dashboard.py",  "🌟 Daily stats, streak, NEET countdown, quotes"),
]

CATEGORIES = [
    ("📁 File & Media",        "01-20", "cyan"),
    ("🌐 Web & Network",       "21-40", "green"),
    ("⚙️  System & Productivity","41-60", "yellow"),
    ("🤖 AI & Machine Learning","61-80", "magenta"),
    ("📚 Study & Exam Prep",   "81-100","red"),
]

def banner():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🚀 100 USEFUL AUTOMATION TOOLS[/bold cyan]\n"
        "[dim]Built by Varshan | AI/ML & CSE Student[/dim]\n"
        "[dim]Pick a tool number or browse by category[/dim]",
        border_style="cyan", padding=(1, 4)
    ))

def show_category(cat_idx: int):
    start_nums = [1, 21, 41, 61, 81]
    end_nums = [20, 40, 60, 80, 100]
    start, end = start_nums[cat_idx], end_nums[cat_idx]
    cat_tools = [t for t in TOOLS if start <= int(t[0]) <= end]
    
    cat_name, cat_range, color = CATEGORIES[cat_idx]
    table = Table(title=f"{cat_name} ({cat_range})", box=box.ROUNDED,
                  header_style=f"bold {color}", border_style=color)
    table.add_column("#", style="dim", width=5)
    table.add_column("Tool Name", style=f"bold {color}")
    table.add_column("Description", style="white")
    
    for num, name, _, desc in cat_tools:
        table.add_row(num, name, desc)
    console.print(table)

def run_tool(tool_num: str):
    tool = next((t for t in TOOLS if t[0] == tool_num.zfill(2) or t[0] == tool_num), None)
    if not tool:
        console.print(f"[red]Tool {tool_num} not found![/red]")
        return
    
    num, name, script, desc = tool
    script_path = BASE / script
    
    if not script_path.exists():
        console.print(f"[red]Script not found: {script_path}[/red]")
        console.print("[yellow]This tool may not be installed yet.[/yellow]")
        return
    
    console.print(f"\n[bold cyan]▶ Launching Tool #{num}: {name}[/bold cyan]")
    console.print(f"[dim]{desc}[/dim]\n")
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=False)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def main():
    while True:
        banner()
        
        # Category shortcuts
        console.print("\n[bold]Browse by Category:[/bold]")
        for i, (name, rang, color) in enumerate(CATEGORIES, 1):
            console.print(f"  [bold {color}]C{i}[/bold {color}] - {name} [{rang}]")
        
        console.print("\n[dim]Or enter a tool number (1-100) to run it directly[/dim]")
        console.print("[dim]Type 'list' to see all tools, 'q' to quit[/dim]\n")
        
        choice = Prompt.ask("[bold cyan]Enter tool # or command[/bold cyan]")
        
        if choice.lower() in ["q", "quit", "exit"]:
            console.print("\n[bold cyan]Goodbye! Keep building! 🚀[/bold cyan]\n")
            break
        
        elif choice.lower() == "list":
            for i, (name, rang, color) in enumerate(CATEGORIES):
                show_category(i)
        
        elif choice.upper().startswith("C") and choice[1:].isdigit():
            idx = int(choice[1:]) - 1
            if 0 <= idx < len(CATEGORIES):
                show_category(idx)
                tool_num = Prompt.ask("Run tool # (or blank to go back)", default="")
                if tool_num.strip():
                    run_tool(tool_num.strip())
        
        elif choice.isdigit():
            run_tool(choice)
        
        else:
            # Search by name
            query = choice.lower()
            matches = [t for t in TOOLS if query in t[1].lower() or query in t[3].lower()]
            if matches:
                console.print(f"\n[green]Found {len(matches)} matches:[/green]")
                for num, name, _, desc in matches:
                    console.print(f"  [cyan]{num}[/cyan] - {name}: {desc}")
                pick = Prompt.ask("Run which # (blank to go back)", default="")
                if pick.strip():
                    run_tool(pick.strip())
            else:
                console.print(f"[yellow]No tools match '{choice}'. Try a tool number or 'list'.[/yellow]")

if __name__ == "__main__":
    main()
