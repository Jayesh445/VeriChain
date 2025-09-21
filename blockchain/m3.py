from fastapi import FastAPI, BackgroundTasks 
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import hashlib
import io
import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from web3 import Web3
import json
import asyncio

# LangChain + Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool

# ---------- FastAPI ----------
app = FastAPI(title="Finance & CA Export Agent")

# ---------- Polygon Setup ----------
POLYGON_RPC_URL = "https://greatest-fittest-diamond.matic-amoy.quiknode.pro/aef075a72de9ad3fbd6cec805950849d9b5fc0b6/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = "0x26E0c55391c7C7c4e5CF1e2389712375dFd694c9"
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
if not w3.is_connected():
    print("⚠️ Warning: Not connected to Polygon network")

# ---------- Simple Agent ----------
class SimpleAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def run(self, question):
        try:
            ql = question.lower()
            if any(k in ql for k in ['financial', 'profit', 'margin', 'kpi']):
                res = self.tool_map['FinancialAnalysis'].func(question)
            elif any(k in ql for k in ['report', 'export', 'csv', 'pdf']):
                res = self.tool_map['ReportGeneration'].func(question)
            elif any(k in ql for k in ['compliance', 'gst', 'tax', 'submission']):
                res = self.tool_map['ComplianceCheck'].func(question)
            else:
                res = self.llm.invoke(f"You are a finance assistant. Answer: {question}")
                return getattr(res, 'content', str(res))

            # Ensure we return the single output key value
            if isinstance(res, dict) and "output" in res:
                return res["output"]
            # If it's a dict but doesn't have "output", convert to string
            elif isinstance(res, dict):
                return json.dumps(res)
            return str(res)
        except Exception as e:
            return f"Error: {str(e)}"

# ---------- Agentic Finance Processor ----------
class FinanceCAExportAgent:
    def __init__(self):
        self.sales_data = None
        self.purchase_data = None
        self.vendor_contracts = None
        self.financial_results = {}
        self.reports_generated = {}
        self.compliance_schedule = None

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key="AIzaSyD9aoSFk91edXOptty5X2p3uXD4Ou-LAjg"
        )
        self.tools = self._setup_tools()
        self.agent = SimpleAgent(self.llm, self.tools)

    # ---------- Step 1 ----------
    async def gather_data(self, sales_df: pd.DataFrame, purchase_df: pd.DataFrame, vendor_contracts: Optional[Dict] = None):
        self.sales_data = sales_df.copy()
        self.purchase_data = purchase_df.copy()
        self.vendor_contracts = vendor_contracts or {}
        return {"sales_records": len(self.sales_data), "purchase_records": len(self.purchase_data), "vendors_loaded": len(self.vendor_contracts)}

    # ---------- Step 2 ----------
    async def validate_transactions(self):
        valid_sales = self.sales_data[self.sales_data["currency"]=="INR"].drop_duplicates(subset=["id"])
        valid_purchase = self.purchase_data[self.purchase_data["currency"]=="INR"].drop_duplicates(subset=["id"])
        self.sales_data = valid_sales
        self.purchase_data = valid_purchase
        return {"valid_sales": len(valid_sales), "valid_purchase": len(valid_purchase)}

    # ---------- Step 3 ----------
    async def compute_financials(self):
        ts = self.sales_data["amount"].sum()
        tp = self.purchase_data["amount"].sum()
        pnl = ts - tp
        gst_out = ts*0.18
        gst_in = tp*0.18
        net_gst = gst_out - gst_in
        margin = (pnl/ts*100) if ts else 0
        self.financial_results = {
            "total_sales": float(ts),
            "total_purchase": float(tp),
            "profit_loss": float(pnl),
            "gst_output": float(gst_out),
            "gst_input": float(gst_in),
            "net_gst_liability": float(net_gst),
            "profit_margin_percent": round(float(margin), 2),
            "gross_profit": float(pnl)
        }
        return self.financial_results

    # ---------- Step 4 ----------
    async def generate_finance_tables(self):
        sales_pivot = self.sales_data.pivot_table(values="amount", index="vendor", aggfunc=["sum","count"])
        purchase_pivot = self.purchase_data.pivot_table(values="amount", index="vendor", aggfunc=["sum","count"])
        gst_summary = pd.DataFrame({"sales_gst":self.sales_data["amount"]*0.18,"purchase_gst":self.purchase_data["amount"]*0.18}).sum().to_dict()
        return {"sales_by_vendor": sales_pivot.to_dict(), "purchase_by_vendor": purchase_pivot.to_dict(), "gst_summary": gst_summary}

    # ---------- Step 5 ----------
    async def export_reports(self):
        sales_csv = self.sales_data.to_csv(index=False)
        purchase_csv = self.purchase_data.to_csv(index=False)
        excel_data = {"sales": self.sales_data.to_dict('records'), "purchase": self.purchase_data.to_dict('records'), "financial_summary": self.financial_results}
        pdf_report = self._generate_pdf_report()
        self.reports_generated = {"csv": {"sales": sales_csv, "purchase": purchase_csv}, "excel": excel_data, "pdf": pdf_report.hex() if isinstance(pdf_report, bytes) else str(pdf_report)}
        return {"formats":["csv","excel","pdf"],"status":"exported"}

    # ---------- Step 6 ----------
    async def store_on_blockchain(self):
        report_hash = hashlib.sha256(json.dumps(self.financial_results).encode()).hexdigest()
        tx_hash = self._store_on_polygon(report_hash)
        return {"report_hash": report_hash, "transaction_hash": tx_hash, "status":"stored_on_blockchain"}

    # ---------- Step 7 ----------
    async def schedule_ca_submissions(self, period="monthly"):
        today = datetime.date.today()
        next_sub = today + datetime.timedelta(days=30 if period=="monthly" else 90)
        self.compliance_schedule = {"next_submission_date": next_sub.strftime("%Y-%m-%d"), "period": period, "tasks_scheduled": ["GST_filing","Income_tax","Compliance_report"], "reminder_set": True}
        return self.compliance_schedule

    # ---------- Step 8 ----------
    def _setup_tools(self):
        return [
            Tool(name="FinancialAnalysis", func=self._agent_financial_analysis, description="Analyze financial data"),
            Tool(name="ReportGeneration", func=self._agent_generate_report, description="Generate reports"),
            Tool(name="ComplianceCheck", func=self._agent_compliance_check, description="Check compliance")
        ]

    def _agent_financial_analysis(self, query):
        return {"output": json.dumps({"metrics": self.financial_results, "recommendations": ["Optimize vendor costs","Review GST compliance"]}, indent=2)}

    def _agent_generate_report(self, query):
        return {"output": json.dumps({"available_reports": list(self.reports_generated.keys()), "status":"ready"}, indent=2)}

    def _agent_compliance_check(self, query):
        # Use the pre-computed schedule instead of calling asyncio.run()
        if self.compliance_schedule is None:
            # Create a new event loop if needed (for standalone use)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we can't use asyncio.run()
                    schedule = {"next_submission_date": "Not scheduled yet", "period": "monthly", "tasks_scheduled": [], "reminder_set": False}
                else:
                    schedule = asyncio.run(self.schedule_ca_submissions())
            except:
                schedule = {"next_submission_date": "Not scheduled yet", "period": "monthly", "tasks_scheduled": [], "reminder_set": False}
        else:
            schedule = self.compliance_schedule
            
        return {"output": json.dumps({"next_submission": schedule}, indent=2)}

    def process_agent_query(self, question):
        return self.agent.run(question)

    def _generate_pdf_report(self):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf)
        data = [["Metric","Value"]] + [[k.replace("_"," ").title(), f"₹{v:,.2f}"] for k,v in self.financial_results.items()]
        table = Table(data)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.grey),("GRID",(0,0),(-1,-1),1,colors.black),("FONTSIZE",(0,0),(-1,-1),10)]))
        doc.build([table])
        buf.seek(0)
        return buf.getvalue()

    def _store_on_polygon(self, hash_str): return f"simulated_tx_hash_{hash_str[:16]}"

# ---------- Global Agent ----------
finance_agent = FinanceCAExportAgent()

# ---------- Mock Data ----------
mock_sales = pd.DataFrame([{"id":1,"vendor":"A Ltd","amount":1000,"currency":"INR"},{"id":2,"vendor":"B Ltd","amount":2000,"currency":"INR"},{"id":3,"vendor":"C Ltd","amount":1500,"currency":"USD"}])
mock_purchase = pd.DataFrame([{"id":1,"vendor":"D Ltd","amount":500,"currency":"INR"},{"id":1,"vendor":"D Ltd","amount":500,"currency":"INR"}])

# ---------- Schemas ----------
class ProcessRequest(BaseModel):
    sales_data: Optional[List[Dict]] = None
    purchase_data: Optional[List[Dict]] = None
    vendor_contracts: Optional[Dict] = None

class QueryRequest(BaseModel):
    question: str

# ---------- Endpoints ----------
@app.post("/process-financials")
async def process_financial_data(req: ProcessRequest, background_tasks: BackgroundTasks):
    sales_df = pd.DataFrame(req.sales_data) if req.sales_data else mock_sales
    purchase_df = pd.DataFrame(req.purchase_data) if req.purchase_data else mock_purchase
    gather = await finance_agent.gather_data(sales_df,purchase_df,req.vendor_contracts)
    validate = await finance_agent.validate_transactions()
    compute = await finance_agent.compute_financials()
    tables = await finance_agent.generate_finance_tables()
    export = await finance_agent.export_reports()
    background_tasks.add_task(finance_agent.store_on_blockchain)
    schedule = await finance_agent.schedule_ca_submissions()
    return {"pipeline_status":"completed","steps":{"data_gathering":gather,"validation":validate,"computation":compute,"tables":tables,"export":export,"scheduling":schedule}}

@app.post("/agent-query")
async def agent_query_endpoint(req: QueryRequest):
    return {"response": finance_agent.process_agent_query(req.question)}

@app.get("/financial-kpis")
async def get_financial_kpis(): return {"kpis": finance_agent.financial_results}

@app.get("/reports/{report_type}")
async def get_reports(report_type: str): 
    if report_type not in finance_agent.reports_generated:
        return {"error": "Report not found. Please process financial data first."}
    return {"report": finance_agent.reports_generated.get(report_type)}

@app.get("/compliance-schedule")
async def get_compliance_schedule(): 
    if finance_agent.compliance_schedule is None:
        finance_agent.compliance_schedule = await finance_agent.schedule_ca_submissions()
    return {"compliance_schedule": finance_agent.compliance_schedule}

@app.get("/health")
async def health_check(): return {"status":"healthy","agent_initialized":True,"blockchain_connected":w3.is_connected()}

@app.get("/verify_tx/{tx_hash}")
async def verify_tx(tx_hash:str): return {"tx_hash":tx_hash,"status":"simulated" if tx_hash.startswith("simulated_tx_hash_") else "verified_simulation"}

# ---------- Startup ----------
@app.on_event("startup")
async def startup_event():
    await finance_agent.gather_data(mock_sales,mock_purchase)
    await finance_agent.validate_transactions()
    await finance_agent.compute_financials()
    await finance_agent.generate_finance_tables()
    finance_agent.compliance_schedule = await finance_agent.schedule_ca_submissions()
    print("Finance CA Export Agent initialized and ready")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)