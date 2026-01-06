# Asana Simulation Seed Data Generator

This project generates realistic seed data for an Asana workspace simulation, representing a B2B SaaS company with 5,000-10,000 employees using Asana for product development, marketing, and operations workflows.

## Overview

The generator creates a comprehensive SQLite database with realistic data for:
- Organizations and Workspaces
- Teams and Users
- Projects (Sprint, Bug Tracking, Marketing Campaigns, etc.)
- Tasks and Subtasks
- Comments and Activity
- Custom Fields
- Tags and Associations
- Attachments

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM-generated content)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Scalar Assignment"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the main script to generate the database:

```bash
python src/main.py
```

The script will:
1. Create the database schema
2. Scrape/generate realistic data from various sources
3. Generate organizations, teams, and users
4. Create projects with appropriate sections
5. Generate tasks with realistic names, descriptions, and metadata
6. Add comments, tags, custom fields, and attachments
7. Save everything to `output/asana_simulation.sqlite`

## Configuration

You can modify the generation parameters in `src/main.py`:

```python
config = {
    'organization_size': 7000,  # Target company size
    'num_teams': 50,            # Number of teams
    'num_projects': 200,        # Total projects
    'tasks_per_project': 50,    # Average tasks per project
    'date_range_months': 6,     # Historical data range
}
```

## Project Structure

```
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── schema.sql                  # Database schema DDL
├── .env.example               # Environment variables template
├── src/
│   ├── main.py                # Main orchestration script
│   ├── scrapers/              # Data scraping modules
│   │   ├── __init__.py
│   │   ├── companies.py       # Company name sources
│   │   └── templates.py       # Project template sources
│   ├── generators/            # Data generation logic
│   │   ├── __init__.py
│   │   ├── users.py           # User generation
│   │   ├── teams.py           # Team generation
│   │   ├── projects.py        # Project generation
│   │   ├── tasks.py           # Task generation
│   │   ├── comments.py        # Comment generation
│   │   └── metadata.py        # Tags, custom fields, etc.
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── database.py        # Database connection and models
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── llm.py             # LLM content generation
│       ├── dates.py           # Date/time utilities
│       └── distributions.py   # Statistical distributions
├── prompts/                   # LLM prompt templates
│   ├── task_names.txt
│   ├── task_descriptions.txt
│   └── project_descriptions.txt
└── output/
    └── asana_simulation.sqlite # Generated database
```

## Data Sources

### Real-World Data Sources

- **Company Names**: Y Combinator directory, Crunchbase (programmatically accessible)
- **User Names**: US Census Bureau name data via Faker library
- **Project Templates**: Public Asana templates, GitHub project boards
- **Task Patterns**: GitHub issues, Asana community templates

### Research-Based Distributions

- Task completion rates: Asana "Anatomy of Work" 2023 report
- Sprint durations: Agile methodology research (2-4 weeks)
- Team sizes: Industry benchmarks (5-15 members)
- Due date patterns: Sprint planning and project management research

## Output

The generated SQLite database (`output/asana_simulation.sqlite`) contains:
- 1 organization
- 50+ teams
- 5,000-10,000 users
- 200+ projects
- 10,000+ tasks
- Realistic distributions and relationships

## Documentation

See the Google Doc for detailed methodology:
- Section A: Complete database schema with ERD
- Section B: Column-by-column data generation strategy

## License

This project is created for evaluation purposes as part of a take-home assignment.
