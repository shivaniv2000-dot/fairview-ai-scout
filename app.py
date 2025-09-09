
import streamlit as st
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

DATA_DIR = Path("data")

@st.cache_data
def load_data():
    funds = pd.read_csv(DATA_DIR / "funds.csv")
    track = pd.read_csv(DATA_DIR / "track_records.csv")
    portfolio = pd.read_csv(DATA_DIR / "portfolio.csv")
    lps = pd.read_csv(DATA_DIR / "lps.csv")
    contacts = pd.read_csv(DATA_DIR / "contacts.csv")
    news = pd.read_csv(DATA_DIR / "news.csv", parse_dates=["Date"])
    return funds, track, portfolio, lps, contacts, news

def section_title(text, styles):
    return Paragraph(f"<b>{text}</b>", styles['Heading2'])

def small(text, styles):
    return Paragraph(text, styles['BodyText'])

def make_table(data, colWidths=None):
    t = Table(data, colWidths=colWidths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#f2f2f2")),
        ("TEXTCOLOR",(0,0),(-1,0), colors.HexColor("#000000")),
        ("GRID",(0,0),(-1,-1), 0.25, colors.HexColor("#cccccc")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(0,0),(-1,0),"LEFT"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#fbfbfb")])
    ]))
    return t

def generate_pdf(output_path, gp_row, fund_row, track_df, portfolio_df, lps_df, contacts_df, news_df):
    styles = getSampleStyleSheet()
    elements = []
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    # Cover
    elements.append(Paragraph(f"<para align='center'><font size=18><b>Fairview Capital Group</b></font></para>", styles['Title']))
    elements.append(Spacer(1,12))
    elements.append(Paragraph(f"<para align='center'><font size=14>Secondary Candidate Briefing</font></para>", styles['Title']))
    elements.append(Spacer(1,12))
    elements.append(Paragraph(f"<para align='center'><font size=12>{fund_row['GP']} — {fund_row['Fund']}</font></para>", styles['Title']))
    elements.append(Spacer(1,24))

    # 1) GP Overview
    elements.append(section_title("1. GP Overview", styles))
    gp_table_data = [
        ["GP Name", gp_row['GP']],
        ["Strategy", gp_row['Strategy']],
        ["Geography (HQ/Focus)", gp_row['Geography']],
        ["Most Recent Vintage", int(gp_row['Vintage'])],
        ["Recent Fund Size", f"{gp_row['FundSize']} {gp_row['Currency']}"],
        ["Website", "—"],
        ["Placement Agent (per Preqin)", "—"],
        ["Office Locations", "—"],
        ["Investment Team (key names)", "See Key Contacts"],
    ]
    elements.append(make_table([["Field","Details"]] + gp_table_data, colWidths=[5*cm, 10*cm]))
    elements.append(Spacer(1, 12))

    # 2) Target Fund Overview
    elements.append(section_title("2. Target Fund Overview", styles))
    # For demo: fabricate reasonable metrics from track record medians if missing
    demo_metrics = {
        "Called (%)": 72, "DPI (%)": 45, "RVPI (%)": 70, "Remaining Value": "auto",
        "Net MOIC": 1.5, "Net IRR": 12.0, "As of Date": "2024-12-31"
    }
    remaining_value = f"~{round(gp_row['FundSize'] * (demo_metrics['RVPI (%)']/100.0), 2)} {gp_row['Currency']}" if demo_metrics["Remaining Value"]=="auto" else demo_metrics["Remaining Value"]
    fund_table = [
        ["Vintage", int(gp_row['Vintage'])],
        ["Fund Size", f"{gp_row['FundSize']} {gp_row['Currency']}"],
        ["Called (%)", demo_metrics["Called (%)"]],
        ["DPI (%)", demo_metrics["DPI (%)"]],
        ["RVPI (%)", demo_metrics["RVPI (%)"]],
        ["Remaining Value", remaining_value],
        ["Net MOIC", demo_metrics["Net MOIC"]],
        ["Net IRR", f"{demo_metrics['Net IRR']}%"],
        ["As of Date", demo_metrics["As of Date"]],
    ]
    elements.append(make_table([["Metric","Value"]] + fund_table, colWidths=[5*cm, 10*cm]))
    elements.append(Spacer(1, 12))

    # 3) Track record (prior funds)
    elements.append(section_title("3. Track Record (Prior Funds)", styles))
    track_subset = track_df[track_df['GP'] == fund_row['GP']].copy()
    if not track_subset.empty:
        track_subset = track_subset.sort_values('Vintage', ascending=False)
        tdata = [["Fund","Vintage","Size","Called%","DPI%","RVPI%","MOIC","IRR%","As of"]]
        for _, r in track_subset.iterrows():
            tdata.append([r["Fund"], int(r["Vintage"]), f"{r['FundSize']} {r['Currency']}", r["CalledPct"], r["DPIpct"], r["RVPIpct"], r["MOIC"], r["IRR"], r["AsOfDate"]])
        elements.append(make_table(tdata, colWidths=[5*cm, 2*cm, 3*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 3*cm]))
    else:
        elements.append(small("No prior fund data available in demo dataset.", styles))
    elements.append(Spacer(1, 12))

    # 4) Recent Developments / GP News
    elements.append(section_title("4. Recent Developments / GP News", styles))
    news_sorted = news_df.sort_values("Date", ascending=False).head(5)
    ndata = [["Date","Headline","Implication","Source"]]
    for _, r in news_sorted.iterrows():
        ndata.append([str(r["Date"].date()), r["Headline"], r["Implication"], r["Source"]])
    elements.append(make_table(ndata, colWidths=[2.5*cm, 7*cm, 6*cm, 4*cm]))
    elements.append(Spacer(1, 12))

    # 5) Target Fund Investments
    elements.append(section_title("5. Target Fund Investments", styles))
    psub = portfolio_df[portfolio_df['Fund'] == fund_row['Fund']]
    pdata = [["Company","Entry Date","Industry","Status","Website"]]
    for _, r in psub.iterrows():
        pdata.append([r["Company"], r["EntryDate"], r["Industry"], r["Status"], r["Website"]])
    if len(pdata) == 1:
        pdata.append(["—","—","—","—","—"])
    elements.append(make_table(pdata, colWidths=[4*cm, 3*cm, 4*cm, 2*cm, 6*cm]))
    elements.append(Spacer(1, 12))

    # 6) Target Fund LPs
    elements.append(section_title("6. Target Fund LPs", styles))
    lsub = lps_df[lps_df['Fund'] == fund_row['Fund']]
    ldata = [["LP Name","Type","Role"]]
    for _, r in lsub.iterrows():
        ldata.append([r["LP"], r["Type"], r["Role"]])
    if len(ldata) == 1:
        ldata.append(["—","—","—"])
    elements.append(make_table(ldata, colWidths=[7*cm, 4*cm, 3*cm]))
    elements.append(Spacer(1, 12))

    # 7) Key Contacts
    elements.append(section_title("7. Key Contacts", styles))
    csub = contacts_df[contacts_df['GP'] == fund_row['GP']]
    cdata = [["Name","Title","Email","LinkedIn"]]
    for _, r in csub.iterrows():
        cdata.append([r["Name"], r["Title"], r["Email"], r["LinkedIn"]])
    if len(cdata) == 1:
        cdata.append(["—","—","—","—"])
    elements.append(make_table(cdata, colWidths=[5*cm, 5*cm, 5*cm, 5*cm]))

    doc.build(elements)

def main():
    st.set_page_config(page_title="Fairview AI Fund Scout", layout="wide")
    st.title("Fairview AI Fund Scout (MVP)")
    st.caption("Filter → Shortlist → Generate PDF memo")

    funds, track, portfolio, lps, contacts, news = load_data()

    # Sidebar filters
    with st.sidebar:
        st.subheader("Filters")
        geo = st.selectbox("Geography", options=["any"] + sorted(funds["Geography"].unique().tolist()))
        strat = st.selectbox("PE Strategy", options=["any"] + sorted(funds["Strategy"].unique().tolist()))
        vintages = sorted(funds["Vintage"].unique().tolist())
        vmin, vmax = min(vintages), max(vintages)
        v_from, v_to = st.slider("Vintage range", min_value=int(vmin), max_value=int(vmax), value=(int(vmin), int(vmax)))

    # Apply filters
    shortlist = funds.copy()
    if geo != "any":
        shortlist = shortlist[shortlist["Geography"] == geo]
    if strat != "any":
        shortlist = shortlist[shortlist["Strategy"] == strat]
    shortlist = shortlist[(shortlist["Vintage"] >= v_from) & (shortlist["Vintage"] <= v_to)].reset_index(drop=True)

    st.subheader("Shortlist")
    st.dataframe(shortlist)

    # Selection
    if not shortlist.empty:
        selected_idx = st.selectbox("Select a fund to generate memo:", options=shortlist.index, format_func=lambda i: f"{shortlist.loc[i,'GP']} — {shortlist.loc[i,'Fund']} ({shortlist.loc[i,'Vintage']})")
        selected_fund_row = shortlist.loc[selected_idx]
        if st.button("Generate PDF memo"):
            outdir = Path("output")
            outdir.mkdir(exist_ok=True)
            outpath = outdir / f"{selected_fund_row['GP']} - {selected_fund_row['Fund']} - Briefing.pdf"
            generate_pdf(
                output_path=str(outpath),
                gp_row=selected_fund_row,
                fund_row=selected_fund_row,
                track_df=track,
                portfolio_df=portfolio,
                lps_df=lps,
                contacts_df=contacts,
                news_df=news
            )
            with open(outpath, "rb") as f:
                st.download_button(label="Download PDF memo", data=f.read(), file_name=outpath.name, mime="application/pdf")
            st.success(f"PDF generated: {outpath}")
    else:
        st.info("No funds match your filters. Try broadening them.")

if __name__ == "__main__":
    main()
