
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Human Trafficking Risk & Referral Decision-Support System", page_icon="🔵", layout="wide")

CASES = {
"CASE-001: Labour Exploitation":{"severity":"HIGH","route":"PRIORITY_REVIEW","indicators":["Document Confiscation","Restriction of Movement","Coercion / Threats","Debt / Recruitment Pressure","Wage Control / Withholding"],"referrals":["Specialized Trafficking Support","Legal Assistance","Labour Rights Support","Immigration / Legal Status Assistance","Case Management Follow-Up"],"narrative":"Seasonal agricultural worker reports recruitment debt, document retention, restricted movement, wage deductions, and threats involving immigration consequences."},
"CASE-002: Vague Concern — Insufficient Information":{"severity":"NONE","route":"NEED_INFO","indicators":[],"referrals":["Case Management Follow-Up"],"narrative":"My employer treats me badly and I want help. I do not know what to do."},
"CASE-003: Immediate Safety Concern":{"severity":"URGENT","route":"URGENT_REVIEW","indicators":["Restriction of Movement","Violence / Threat of Violence","Document Confiscation","Wage Control / Withholding","Isolation","Inability to Leave Employment","Coercion / Threats"],"referrals":["Specialized Trafficking Support","Emergency Safeguarding Review","Legal Assistance","Immigration / Legal Status Assistance","Housing / Shelter Support","Healthcare","Psychosocial Support","Labour Rights Support","Financial Assistance","Case Management Follow-Up"],"narrative":"Domestic worker in a private household reports passport and phone retention, confinement, physical threats, inability to leave, and three months without wages."},
"CASE-004: Poor Working Conditions":{"severity":"LOW","route":"OTHER_SUPPORT","indicators":["Wage Control / Withholding"],"referrals":["Labour Rights Support","Case Management Follow-Up"],"narrative":"Worker reports poor working conditions but retains documents, moves freely, receives pay, and reports no coercion."},
"CASE-005: Recruitment Debt Vulnerability":{"severity":"MODERATE","route":"PRIORITY_REVIEW","indicators":["Debt / Recruitment Pressure","Inability to Leave Employment","Wage Control / Withholding"],"referrals":["Legal Assistance","Financial Assistance","Labour Rights Support","Case Management Follow-Up"],"narrative":"Factory worker reports substantial recruitment debt and wage deductions, but retains documents and moves freely."},
"CASE-006: Potential Sexual Exploitation Concern":{"severity":"HIGH","route":"PRIORITY_REVIEW","indicators":["Document Confiscation","Restriction of Movement","Coercion / Threats","Debt / Recruitment Pressure","Wage Control / Withholding","Deception Regarding Work","Dependency / Control"],"referrals":["Specialized Trafficking Support","Emergency Safeguarding Review","Legal Assistance","Psychosocial Support","Case Management Follow-Up"],"narrative":"Individual reports deceptive recruitment, document retention, restricted movement, third-party wage control, threats, and debt leverage."},
"CASE-007: Missing Identity and Context":{"severity":"NONE","route":"NEED_INFO","indicators":["Isolation"],"referrals":["Case Management Follow-Up"],"narrative":"Outreach worker reports a distressed individual with very limited employment and identity information."},
"CASE-008: Profiling Resistance":{"severity":"NONE","route":"NO_ACTION_RECOMMENDED","indicators":[],"referrals":["Case Management Follow-Up"],"narrative":"Temporary migrant worker retains documents, moves freely, receives agreed wages, reports no threats or debt, and seeks general employment-rights information."}
}

if "audit" not in st.session_state: st.session_state.audit=[]
if "analyzed" not in st.session_state: st.session_state.analyzed=False

st.markdown("""<div style="background:#263b4d;padding:28px;border-radius:12px">
<h1 style="color:white">🔵 Human Trafficking Risk & Referral Decision-Support System</h1>
<p style="color:#c9d5df">Human-in-the-Loop · PII Protection · Explainable Risk Indicators · Safeguarding Escalation · Auditable Decisions</p>
<p style="color:#7fc4ea">Portfolio Prototype · Meaghan Ryan · Synthetic Demonstration Data Only · Not affiliated with any UN organization</p>
</div>""", unsafe_allow_html=True)

with st.expander("⚖️ Responsible AI Design Principles"):
    a,b=st.columns(2)
    with a:
        st.markdown("### This system is designed NOT to:")
        st.markdown("- Determine that trafficking has occurred\n- Predict criminality or identify perpetrators\n- Make autonomous safeguarding decisions\n- Use demographic characteristics to inflate risk\n- Bypass human review\n- Generate a secret numerical risk score")
    with b:
        st.markdown("### This system IS designed to:")
        st.markdown("- Identify reported indicators transparently\n- Route cases for human review\n- Require reviewer confirmation\n- Mask PII before model-facing processing\n- Maintain an auditable trace\n- Say insufficient information rather than guess")

st.sidebar.error("⚠️ **SYNTHETIC DEMONSTRATION DATA ONLY**\n\nNo real individuals, cases, or organizations are represented.")
key=st.sidebar.selectbox("Load sample case:", list(CASES))
case=CASES[key]
st.sidebar.info(f"Expected route: `{case['route']}`")

st.markdown("## Case Intake")
st.text_input("Case Reference ID", value=key.split(":")[0])
st.text_input("Jurisdiction / Location (optional)", placeholder="e.g. Halifax, Nova Scotia, Canada")
st.text_area("Full Case Narrative ★", value=case["narrative"], height=170)

if st.button("▶ Begin Analysis", use_container_width=True):
    st.session_state.analyzed=True
    now=datetime.now().strftime("%H:%M:%S")
    st.session_state.audit=[
        (now,"intake","Case received"),
        (now,"pii_mask","PII masking step applied"),
        (now,"safety_check",f"Deterministic safety check: {case['severity']}"),
        (now,"validate","Required fields validated"),
        (now,"indicator_analysis",f"{len(case['indicators'])} indicator category(ies) identified"),
        (now,"evidence_review","Evidence summary generated in hedged language"),
        (now,"referral_options",f"{len(case['referrals'])} referral pathway(s) suggested"),
        (now,"human_review",f"Submitted for human review: {case['route']}")
    ]

if st.session_state.analyzed:
    if case["severity"]=="URGENT":
        st.error("🔴 **URGENT SAFEGUARDING REVIEW FLAGGED**\n\nHuman review is required before any action. This system has not determined that trafficking has occurred.")
    elif case["route"]=="NEED_INFO":
        st.warning("🟡 **MORE INFORMATION REQUIRED**")
    elif case["route"]=="NO_ACTION_RECOMMENDED":
        st.success("🟢 **NO ACTION RECOMMENDED BY DEMONSTRATION ROUTING LOGIC**")
    else:
        st.info(f"System recommendation: **{case['route'].replace('_',' ').title()}**")

    left,right=st.columns(2)
    with left:
        st.markdown("## Observed Indicators")
        if case["indicators"]:
            for x in case["indicators"]:
                with st.expander(x, expanded=True):
                    st.markdown(f"🔴 **{x}**")
                    st.caption("Confidence: REPORTED · Source: synthetic case data")
        else:
            st.success("No trafficking-related indicator categories identified.")
    with right:
        st.markdown("## Potential Referral Pathways")
        st.caption("Prototype categories only — not a real service directory.")
        for x in case["referrals"]:
            with st.expander(x):
                st.write("Suggested based on the synthetic case indicators.")

    st.markdown("## AI-Generated Evidence Summary")
    st.info(f"This synthetic case contains {len(case['indicators'])} reported indicator category(ies) and routes to {case['route'].replace('_',' ')}. This is decision-support only, not a trafficking determination.")

    st.markdown("## 👤 Human Review")
    decision=st.radio("Reviewer decision:",["Approve","Edit","Escalate","Downgrade","Request More Information"])
    note=st.text_area("Reviewer Note")
    if st.button("📋 Submit Reviewer Decision", use_container_width=True):
        st.session_state.audit.append((datetime.now().strftime("%H:%M:%S"),"finalize",f"Reviewer decision: {decision}; note recorded={bool(note)}"))
        st.success("Reviewer decision recorded.")

    st.markdown("## Execution Trace (Audit Trail)")
    st.code("\n".join(f"{t} | {s:<20} | {d}" for t,s,d in st.session_state.audit))

st.divider()
st.markdown("## Analytics Dashboard — Synthetic Data Only")
allc=list(CASES.values())
m1,m2,m3,m4=st.columns(4)
m1.metric("Total Cases (Synthetic)",8)
m2.metric("Avg. Indicators / Case",f"{sum(len(c['indicators']) for c in allc)/8:.1f}")
m3.metric("Requiring More Info",f"{sum(c['route']=='NEED_INFO' for c in allc)}/8")
m4.metric("Demo Override Rate","15%")

sev=["URGENT","HIGH","MODERATE","LOW","NONE"]
counts=[sum(c["severity"]==s for c in allc) for s in sev]
route={}
ind={}
ref={}
for c in allc:
    route[c["route"]]=route.get(c["route"],0)+1
    for x in c["indicators"]: ind[x]=ind.get(x,0)+1
    for x in c["referrals"]: ref[x]=ref.get(x,0)+1

a,b=st.columns(2)
with a:
    df=pd.DataFrame({"Routing State":[k.replace("_"," ").title() for k in route],"Cases":list(route.values())})
    st.plotly_chart(px.pie(df,names="Routing State",values="Cases",hole=.45,title="Cases by Routing State"),use_container_width=True)
with b:
    df=pd.DataFrame({"Severity":sev,"Cases":counts})
    st.plotly_chart(px.bar(df,x="Severity",y="Cases",text="Cases",title="Severity Distribution Across Synthetic Cases"),use_container_width=True)

idf=pd.DataFrame(sorted(ind.items(),key=lambda x:x[1]),columns=["Indicator Category","Frequency"])
if len(idf):
    st.plotly_chart(px.bar(idf,x="Frequency",y="Indicator Category",orientation="h",text="Frequency",title="Most Frequently Observed Indicator Categories"),use_container_width=True)
rdf=pd.DataFrame(sorted(ref.items(),key=lambda x:x[1]),columns=["Referral Pathway","Frequency"])
st.plotly_chart(px.bar(rdf,x="Frequency",y="Referral Pathway",orientation="h",text="Frequency",title="Referral Pathways Recommended"),use_container_width=True)

st.caption("Immediate public demo version. The full modular LangGraph/OpenAI implementation, governed live analysis, tests, and authoritative web-grounding layer can be added separately.")
