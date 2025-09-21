import streamlit as st
import requests
import json
import pandas as pd
import io
import base64
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import threading
import queue

# ----------------- Configuration -----------------
API_URL = "http://localhost:8000"  # Change if your FastAPI runs elsewhere

st.set_page_config(page_title="Finance & CA Export Agent", layout="wide")
st.title("💰 Finance & CA Export Agent")

# ----------------- Voice Chatbot Setup -----------------
# Initialize speech recognition and text-to-speech
try:
    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()
except:
    st.warning("Voice features require SpeechRecognition and pyttsx3. Install with: pip install SpeechRecognition pyttsx3")

# Set up voice commands
VOICE_COMMANDS = {
    "show dashboard": "dashboard",
    "process financials": "process_financials",
    "generate reports": "generate_reports",
    "ask agent": "agent_query",
    "compliance schedule": "compliance_schedule",
    "verify transaction": "verify_transaction",
    "financial summary": "financial_summary",
    "profit analysis": "profit_analysis",
    "gst analysis": "gst_analysis",
    "compliance status": "compliance_status"
}

# ----------------- Voice Chatbot Modal -----------------
def voice_chatbot_modal():
    """Create a voice chatbot modal"""
    if st.sidebar.button("🎤 Voice Assistant", key="voice_assistant_btn"):
        st.session_state.show_voice_modal = True
    
    if st.session_state.get('show_voice_modal', False):
        with st.expander("🎤 Voice Assistant - Click to speak", expanded=True):
            st.markdown("### Voice Commands Available:")
            col1, col2 = st.columns(2)
            with col1:
                st.write("• Show Dashboard")
                st.write("• Process Financials")
                st.write("• Generate Reports")
                st.write("• Ask Agent")
                st.write("• Compliance Schedule")
            with col2:
                st.write("• Verify Transaction")
                st.write("• Financial Summary")
                st.write("• Profit Analysis")
                st.write("• GST Analysis")
                st.write("• Compliance Status")
            
            # Voice recording and processing
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("🎤 Start Listening", key="start_listening"):
                    st.session_state.listening = True
                    process_voice_command()
            
            with col2:
                if st.button("🔊 Speak Response", key="speak_response"):
                    speak_last_response()
            
            with col3:
                if st.button("❌ Close", key="close_modal"):
                    st.session_state.show_voice_modal = False
                    st.session_state.listening = False
            
            # Display voice command status
            if st.session_state.get('listening', False):
                st.info("🎤 Listening... Speak your command")
            if st.session_state.get('last_command', ''):
                st.success(f"🎯 Command: {st.session_state.last_command}")
            if st.session_state.get('last_response', ''):
                st.info(f"🤖 Response: {st.session_state.last_response}")

def process_voice_command():
    """Process voice command using speech recognition"""
    try:
        with sr.Microphone() as source:
            st.session_state.listening = True
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        # Convert speech to text
        command = recognizer.recognize_google(audio).lower()
        st.session_state.last_command = command
        st.session_state.last_response = execute_voice_command(command)
        
    except sr.UnknownValueError:
        st.session_state.last_response = "Sorry, I didn't understand that."
    except sr.RequestError:
        st.session_state.last_response = "Speech service unavailable."
    except Exception as e:
        st.session_state.last_response = f"Error: {str(e)}"
    finally:
        st.session_state.listening = False

def execute_voice_command(command):
    """Execute the voice command"""
    # Find the best matching command
    best_match = None
    best_score = 0
    
    for voice_cmd, action in VOICE_COMMANDS.items():
        if voice_cmd in command:
            if len(voice_cmd) > best_score:
                best_match = action
                best_score = len(voice_cmd)
    
    if best_match:
        return handle_voice_action(best_match, command)
    else:
        # If no specific command matched, treat as agent query
        return handle_agent_query(command)

def handle_voice_action(action, original_command):
    """Handle specific voice actions"""
    if action == "dashboard":
        st.session_state.menu_choice = "Dashboard"
        return "Taking you to the Dashboard"
    
    elif action == "process_financials":
        st.session_state.menu_choice = "Process Financials"
        return "Opening Process Financials section"
    
    elif action == "generate_reports":
        st.session_state.menu_choice = "Generate Reports"
        return "Opening Generate Reports section"
    
    elif action == "agent_query":
        st.session_state.menu_choice = "Agent Query"
        return "Opening Agent Query section"
    
    elif action == "compliance_schedule":
        st.session_state.menu_choice = "Compliance Schedule"
        return "Opening Compliance Schedule section"
    
    elif action == "verify_transaction":
        st.session_state.menu_choice = "Verify Transaction"
        return "Opening Verify Transaction section"
    
    elif action == "financial_summary":
        response = requests.get(f"{API_URL}/financial-kpis")
        if response.status_code == 200:
            kpis = response.json().get("kpis", {})
            return f"Financial Summary: Sales ₹{kpis.get('total_sales', 0):,.2f}, Profit ₹{kpis.get('profit_loss', 0):,.2f}, Margin {kpis.get('profit_margin_percent', 0):.1f}%"
        return "Could not fetch financial summary"
    
    elif action == "profit_analysis":
        return handle_agent_query("Analyze our profit margins and suggest improvements")
    
    elif action == "gst_analysis":
        return handle_agent_query("Analyze our GST liability and input tax credit")
    
    elif action == "compliance_status":
        response = requests.get(f"{API_URL}/compliance-schedule")
        if response.status_code == 200:
            schedule = response.json().get("compliance_schedule", {})
            return f"Next compliance submission: {schedule.get('next_submission_date', 'N/A')}"
        return "Could not fetch compliance status"
    
    return "Command executed successfully"

def handle_agent_query(query):
    """Handle agent queries through voice"""
    try:
        payload = {"question": query}
        response = requests.post(f"{API_URL}/agent-query", json=payload)
        
        if response.status_code == 200:
            return response.json().get("response", "No response from agent")
        else:
            return "Failed to get response from agent"
    except Exception as e:
        return f"Error: {str(e)}"

def speak_last_response():
    """Convert the last response to speech"""
    if st.session_state.get('last_response'):
        try:
            # Run TTS in a separate thread to avoid blocking
            def speak():
                tts_engine.say(st.session_state.last_response)
                tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.start()
            
        except Exception as e:
            st.error(f"TTS Error: {str(e)}")

# ----------------- Initialize Session State -----------------
if 'show_voice_modal' not in st.session_state:
    st.session_state.show_voice_modal = False
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'last_command' not in st.session_state:
    st.session_state.last_command = ""
if 'last_response' not in st.session_state:
    st.session_state.last_response = ""
if 'menu_choice' not in st.session_state:
    st.session_state.menu_choice = "Dashboard"

# ----------------- Sidebar Menu -----------------
menu = ["Dashboard", "Process Financials", "Generate Reports", "Agent Query", "Compliance Schedule", "Verify Transaction"]
choice = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state.menu_choice))

# Add voice chatbot to sidebar
voice_chatbot_modal()

# Update menu choice based on voice commands
if st.session_state.menu_choice != choice:
    st.session_state.menu_choice = choice

# ----------------- Dashboard Section -----------------
if choice == "Dashboard":
    st.header("📊 Financial Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        response = requests.get(f"{API_URL}/financial-kpis")
        if response.status_code == 200:
            kpis = response.json().get("kpis", {})
            
            with col1:
                st.metric("Total Sales", f"₹{kpis.get('total_sales', 0):,.2f}")
                st.metric("Total Purchase", f"₹{kpis.get('total_purchase', 0):,.2f}")
            
            with col2:
                st.metric("Profit & Loss", f"₹{kpis.get('profit_loss', 0):,.2f}", 
                         delta=f"{kpis.get('profit_margin_percent', 0):.1f}%")
                st.metric("Gross Profit", f"₹{kpis.get('gross_profit', 0):,.2f}")
            
            with col3:
                st.metric("Net GST Liability", f"₹{kpis.get('net_gst_liability', 0):,.2f}")
                st.metric("Profit Margin", f"{kpis.get('profit_margin_percent', 0):.1f}%")
        
        else:
            st.error(f"Failed to fetch KPIs. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

# ----------------- Process Financials Section -----------------
elif choice == "Process Financials":
    st.header("🔧 Process Financial Data")
    
    # File upload section
    st.subheader("Upload Data (Optional)")
    sales_file = st.file_uploader("Upload Sales CSV", type=["csv"])
    purchase_file = st.file_uploader("Upload Purchase CSV", type=["csv"])
    
    # Manual data entry
    st.subheader("Or Enter Data Manually")
    
    with st.expander("Sales Data"):
        sales_data = st.data_editor(pd.DataFrame([
            {"id": 1, "vendor": "A Ltd", "amount": 1000, "currency": "INR", "gst": 18},
            {"id": 2, "vendor": "B Ltd", "amount": 2000, "currency": "INR", "gst": 18},
        ]), num_rows="dynamic")
    
    with st.expander("Purchase Data"):
        purchase_data = st.data_editor(pd.DataFrame([
            {"id": 1, "vendor": "C Ltd", "amount": 500, "currency": "INR", "gst": 18},
        ]), num_rows="dynamic")
    
    if st.button("🚀 Process Financial Data", type="primary"):
        try:
            # Prepare payload
            payload = {
                "sales_data": sales_data.to_dict('records'),
                "purchase_data": purchase_data.to_dict('records')
            }
            
            # Show processing steps
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Gathering data...",
                "Validating transactions...",
                "Computing financials...",
                "Generating tables...",
                "Exporting reports...",
                "Scheduling compliance..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                # Simulate processing time
                import time
                time.sleep(0.5)
            
            # Send request to backend
            response = requests.post(f"{API_URL}/process-financials", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Financial data processed successfully!")
                
                # Display results
                st.subheader("Processing Results")
                
                for step_name, step_result in result.get("steps", {}).items():
                    with st.expander(f"Step: {step_name.replace('_', ' ').title()}"):
                        st.json(step_result)
                
            else:
                st.error(f"Failed to process data. Status code: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error: {e}")

# ----------------- Generate Reports Section -----------------
elif choice == "Generate Reports":
    st.header("📝 Download Reports")
    
    try:
        # Get the specific report type
        report_types = ["csv", "excel", "pdf"]
        selected_type = st.selectbox("Select report type", report_types)
        
        response = requests.get(f"{API_URL}/reports/{selected_type}")
        
        if response.status_code == 200:
            report_data = response.json().get("report", {})
            
            if "error" in report_data:
                st.warning(report_data["error"])
                if st.button("Process Sample Data"):
                    response = requests.post(f"{API_URL}/process-financials", json={})
                    if response.status_code == 200:
                        st.success("Sample data processed! Refresh to see reports.")
                    else:
                        st.error("Failed to process sample data.")
            else:
                if selected_type == "csv":
                    st.subheader("📄 CSV Reports")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sales_csv = report_data.get("sales", "")
                        st.download_button(
                            label="Download Sales CSV",
                            data=sales_csv,
                            file_name="sales_report.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        purchase_csv = report_data.get("purchase", "")
                        st.download_button(
                            label="Download Purchase CSV",
                            data=purchase_csv,
                            file_name="purchase_report.csv",
                            mime="text/csv"
                        )
                
                elif selected_type == "excel":
                    st.subheader("📊 Excel Data")
                    excel_data = report_data
                    excel_json = json.dumps(excel_data, indent=2)
                    
                    st.download_button(
                        label="Download Excel (JSON)",
                        data=excel_json,
                        file_name="financial_data.json",
                        mime="application/json"
                    )
                
                elif selected_type == "pdf":
                    st.subheader("📑 PDF Report")
                    pdf_data = report_data
                    # Handle PDF data (could be hex string or bytes)
                    if isinstance(pdf_data, str):
                        try:
                            pdf_bytes = bytes.fromhex(pdf_data)
                        except:
                            pdf_bytes = pdf_data.encode()
                    else:
                        pdf_bytes = pdf_data
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name="financial_report.pdf",
                        mime="application/pdf"
                    )
            
            # Show financial summary
            st.subheader("Financial Summary")
            kpis_response = requests.get(f"{API_URL}/financial-kpis")
            if kpis_response.status_code == 200:
                kpis = kpis_response.json().get("kpis", {})
                st.dataframe(pd.DataFrame([kpis]).T.rename(columns={0: "Value"}))
                
        else:
            st.error(f"Failed to fetch reports. Status code: {response.status_code}")
                    
    except Exception as e:
        st.error(f"Error: {e}")

# ----------------- Agent Query Section -----------------
elif choice == "Agent Query":
    st.header("🤖 AI Finance Agent")
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Pre-defined queries
    st.subheader("Quick Queries")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 Show financial summary"):
            st.session_state.question = "Show me a summary of our financial performance"
        if st.button("📊 Analyze profit margins"):
            st.session_state.question = "Analyze our profit margins and suggest improvements"
    
    with col2:
        if st.button("📋 Compliance status"):
            st.session_state.question = "What are our current compliance requirements and deadlines?"
        if st.button("🔍 GST analysis"):
            st.session_state.question = "Analyze our GST liability and input tax credit"
    
    # Custom query
    question = st.text_area(
        "Or ask your own question:",
        value=st.session_state.get("question", ""),
        height=100
    )
    
    if st.button("Ask Agent", type="primary"):
        if question.strip():
            try:
                with st.spinner("🤔 Thinking..."):
                    payload = {"question": question}
                    response = requests.post(f"{API_URL}/agent-query", json=payload)
                    
                    if response.status_code == 200:
                        answer = response.json().get("response", "")
                        
                        st.subheader("💡 Agent Response")
                        st.write(answer)
                        
                        # Store conversation history
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer
                        })
                        
                    else:
                        st.error(f"Agent failed to answer. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a question.")
    
    # Show chat history
    if st.session_state.chat_history:
        st.subheader("💬 Conversation History")
        for i, chat in enumerate(st.session_state.chat_history[-5:], 1):  # Show last 5
            with st.expander(f"Q{i}: {chat['question'][:50]}..."):
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer']}")

# ----------------- Compliance Schedule Section -----------------
elif choice == "Compliance Schedule":
    st.header("📅 Compliance Schedule")
    
    try:
        response = requests.get(f"{API_URL}/compliance-schedule")
        if response.status_code == 200:
            schedule = response.json().get("compliance_schedule", {})
            
            st.metric("Next Submission Date", schedule.get("next_submission_date", "N/A"))
            st.write(f"**Period:** {schedule.get('period', 'N/A').title()}")
            
            st.subheader("Scheduled Tasks")
            for task in schedule.get("tasks_scheduled", []):
                st.write(f"✅ {task.replace('_', ' ').title()}")
            
            if schedule.get("reminder_set", False):
                st.success("🔔 Reminders are active")
            else:
                st.warning("🔕 Reminders not set")
                
        else:
            st.error(f"Failed to fetch schedule. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

# ----------------- Verify Transaction Section -----------------
elif choice == "Verify Transaction":
    st.header("🔗 Verify Blockchain Transaction")
    
    tx_hash = st.text_input("Enter Transaction Hash:", placeholder="0x...")
    
    if st.button("Verify Transaction", type="primary"):
        if tx_hash.strip():
            try:
                with st.spinner("🔍 Verifying on blockchain..."):
                    response = requests.get(f"{API_URL}/verify_tx/{tx_hash}")
                    
                    if response.status_code == 200:
                        tx_data = response.json()
                        
                        st.success("✅ Transaction Verified")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Transaction Details")
                            st.write(f"**Hash:** {tx_data.get('tx_hash', 'N/A')}")
                            st.write(f"**Status:** {tx_data.get('status', 'unknown').title()}")
                        
                        with col2:
                            st.subheader("Stored Data")
                            st.info("Simulated transaction data")
                        
                    else:
                        st.error(f"Failed to verify transaction. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a transaction hash.")

# ----------------- Footer -----------------
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Finance & CA Export Agent**  
    Automated financial processing with AI and blockchain integration.
    
    Features:
    - 8-step financial processing
    - AI-powered analysis
    - Blockchain audit trails
    - Compliance scheduling
    - Voice assistant
    """
)

# Health check
try:
    health_response = requests.get(f"{API_URL}/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        status = "✅ Healthy" if health_data.get("status") == "healthy" else "❌ Unhealthy"
        st.sidebar.success(f"Backend Status: {status}")
    else:
        st.sidebar.error("❌ Backend unavailable")
except:
    st.sidebar.error("❌ Cannot connect to backend")

# Installation instructions in sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
**Voice Assistant Requirements:**
- Install: `pip install SpeechRecognition pyttsx3`
- Microphone required for voice input
- Speakers required for voice output
""")