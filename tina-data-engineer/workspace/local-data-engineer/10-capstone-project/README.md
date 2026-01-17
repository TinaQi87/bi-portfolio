# Module 10: Capstone Project

## 🎯 StreamFlow Analytics Pipeline

Congratulations! You've completed 9 modules of intensive data engineering training. Now it's time to prove you can put it all together.

This capstone project simulates a real junior data engineer's first major assignment. You'll build a complete, production-ready data pipeline that demonstrates every skill you've learned.

---

## The Scenario

You've just been hired as a Junior Data Engineer at **StreamFlow**, a music streaming startup with 100,000+ users. Your manager gives you this assignment:

> "We need a daily pipeline that processes listening data and loads it into our data warehouse. The analytics team needs to answer questions like 'What are our most popular songs?' and 'When do users listen most?' 
>
> The pipeline needs to run automatically every night, handle errors gracefully, and be maintainable by the team. Oh, and it needs to be fast enough to finish before the morning standup at 9 AM."

**This is exactly what junior data engineers do in real companies.**

---

## What You'll Build

A complete data pipeline that demonstrates mastery of all 9 modules:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STREAMFLOW DATA PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  SOURCE  │───▶│ EXTRACT  │───▶│TRANSFORM │───▶│   LOAD   │          │
│  │  DATA    │    │          │    │& VALIDATE│    │          │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │              │                │               │                  │
│       ▼              ▼                ▼               ▼                  │
│   CSV files      Python          Data Quality    Star Schema            │
│   JSON API       Pandas          Checks          Database               │
│   Database       Logging         Testing         Indexes                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      ORCHESTRATION                                │   │
│  │  Airflow DAG  │  Scheduling  │  Retries  │  Alerts  │  Monitoring │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      INFRASTRUCTURE                               │   │
│  │  Git Workflow  │  Bash Scripts  │  CI/CD  │  Documentation        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Skills Demonstrated

| Module | Skills Applied in Capstone |
|--------|---------------------------|
| **01 Linux** | Bash scripts, cron scheduling, file operations, log management |
| **02 Database** | SQL queries, schema design, indexes, transactions |
| **03 Python** | Pandas, file handling, API calls, logging, error handling |
| **04 Data Modeling** | Star schema, fact/dimension tables, SCD Type 2 |
| **05 ETL** | Extract from multiple sources, transform, incremental load |
| **06 Data Quality** | Validation rules, data contracts, monitoring, testing |
| **07 Version Control** | Git workflow, branching, pull requests, CI/CD |
| **08 Orchestration** | Airflow DAG, scheduling, dependencies, error handling |
| **09 Performance** | Query optimization, efficient pandas, profiling |

---

## Project Phases

The project is divided into 7 phases, each building on the previous:

| Phase | Focus | Time | Deliverables |
|-------|-------|------|--------------|
| 1 | Project Setup & Data Model | Day 1 | Git repo, schema, sample data |
| 2 | Extract Module | Day 2 | Working extraction from all sources |
| 3 | Transform & Validate | Day 3 | Clean data, quality checks |
| 4 | Load Module | Day 4 | Data in warehouse, incremental loading |
| 5 | Testing & Quality | Day 5 | Unit tests, integration tests |
| 6 | Orchestration | Day 6 | Airflow DAG, scheduling |
| 7 | Polish & Document | Day 7 | README, optimization, final review |

---

## Success Criteria

Your project is complete when:

### Must Have (Required for Pass)
- [ ] Pipeline runs end-to-end without errors
- [ ] Star schema is properly designed with fact and dimension tables
- [ ] Data quality checks validate all incoming data
- [ ] Code is version controlled with meaningful commits
- [ ] Pipeline is scheduled to run automatically
- [ ] README explains how to set up and run the project

### Should Have (Required for Good Grade)
- [ ] Unit tests cover transform functions
- [ ] Incremental loading (don't reload all history)
- [ ] Error handling with retries
- [ ] Logging throughout the pipeline
- [ ] Analytics queries work correctly

### Nice to Have (Bonus Points)
- [ ] SCD Type 2 for user dimension
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Performance optimization documented
- [ ] Monitoring dashboard

---

## Getting Started

1. **Read the Phase Guides** - Start with [Phase 1: Setup](phases/phase-01-setup.md)
2. **Review Sample Data** - Understand what you're working with in [sample-data/](sample-data/)
3. **Use Starter Code** - Don't start from scratch, use [starter-code/](starter-code/)
4. **Check the Rubric** - Know how you'll be evaluated in [rubric.md](rubric.md)
5. **Reference the Data Dictionary** - Understand the schema in [data-dictionary.md](data-dictionary.md)

---

## Project Structure

Your final project should look like this:

```
streamflow-pipeline/
├── README.md                 # How to run your project
├── requirements.txt          # Python dependencies
├── setup.sh                  # Bash script to set up environment
│
├── src/                      # Python source code
│   ├── __init__.py
│   ├── extract.py           # Extract from all sources
│   ├── transform.py         # Transform and clean data
│   ├── validate.py          # Data quality checks
│   ├── load.py              # Load to database
│   ├── pipeline.py          # Main orchestration
│   └── utils.py             # Helper functions
│
├── sql/                      # SQL files
│   ├── schema.sql           # Create tables
│   ├── indexes.sql          # Performance indexes
│   └── queries.sql          # Analytics queries
│
├── dags/                     # Airflow DAGs
│   └── streamflow_dag.py    # Pipeline DAG
│
├── tests/                    # Test files
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_validate.py
│
├── scripts/                  # Bash scripts
│   ├── setup.sh             # Environment setup
│   ├── run_pipeline.sh      # Run pipeline manually
│   └── check_logs.sh        # View recent logs
│
├── config/                   # Configuration
│   ├── config.yaml          # Pipeline settings
│   └── .env.example         # Environment variables template
│
├── logs/                     # Log files (gitignored)
│
└── data/                     # Sample data (gitignored in production)
    ├── events_*.csv
    ├── users.json
    └── songs.csv
```

---

## Timeline Recommendation

| Day | Morning | Afternoon |
|-----|---------|-----------|
| **1** | Read requirements, set up Git repo | Design schema, generate sample data |
| **2** | Build extract module | Test extraction, handle edge cases |
| **3** | Build transform module | Add validation, write quality checks |
| **4** | Build load module | Implement incremental loading |
| **5** | Write unit tests | Integration testing |
| **6** | Create Airflow DAG | Test scheduling, add error handling |
| **7** | Write documentation | Optimize performance, final review |

---

## Asking for Help

If you get stuck:

1. **Re-read the relevant module** - The answer is probably there
2. **Check the hints** - Each phase has hints for common problems
3. **Look at the solution** - But try yourself first!
4. **Debug systematically** - Use logging, print statements, and profiling

---

## Ready?

Start with [Phase 1: Project Setup & Data Model →](phases/phase-01-setup.md)

Good luck! 🚀
