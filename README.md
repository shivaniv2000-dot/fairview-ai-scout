
# Fairview AI Fund Scout — MVP

A working prototype to **filter GP/Funds by Geography, Vintage, Strategy**, shortlist candidates, and generate a **pitch-ready PDF memo** in Fairview's format.

## What it does
- Filter by **Geography**, **Vintage range**, and **PE Strategy**
- See a **shortlist** of matching funds
- Select one and **generate a PDF** with:
  1. GP Overview
  2. Target Fund Overview
  3. Track Record (Prior Funds)
  4. Recent Developments / GP News
  5. Target Fund Investments
  6. Target Fund LPs
  7. Key Contacts

> This MVP uses **dummy but realistic data** stored in `data/`. Hook up APIs (Preqin, PitchBook, News) in v1.

## Quick start

1. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Use the sidebar filters** to get a shortlist → select a fund → click **Generate PDF memo** → download.

## Project structure
```
fairview_ai_scout_mvp/
├─ app.py                 # Streamlit UI + PDF generator
├─ data/
│  ├─ funds.csv
│  ├─ track_records.csv
│  ├─ portfolio.csv
│  ├─ lps.csv
│  ├─ contacts.csv
│  └─ news.csv
├─ requirements.txt
└─ README.md
```

## Notes
- The PDF uses **ReportLab**. Swap to PowerPoint using `python-pptx` if you prefer slides.
- Replace dummy data in `data/` with your internal datasets or API connectors.
- Add logos, benchmarking charts, and house branding later (template-ready).

— Built with ❤️ for your team demo.
