import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.agents.workflow_orchestrator import AgentWorkflowOrchestrator
from app.core.logging import logger


async def main():
    """Test the complete agentic workflow"""
    logger.info("Starting agentic workflow test...")
    
    try:
        # Initialize orchestrator
        orchestrator = AgentWorkflowOrchestrator()
        
        # Run analysis
        async with AsyncSessionLocal() as db:
            print("🤖 Triggering AI agent analysis...")
            
            workflow_context = await orchestrator.trigger_full_analysis(
                db=db,
                trigger_type="test",
                parameters={"test_mode": True}
            )
            
            print(f"✅ Workflow started: {workflow_context.workflow_id}")
            print(f"📊 Status: {workflow_context.status.value}")
            
            if workflow_context.status.value == "completed":
                print(f"⏱️  Duration: {(workflow_context.completed_at - workflow_context.started_at).total_seconds():.2f} seconds")
                print(f"🎯 Decisions made: {len(workflow_context.decisions)}")
                print(f"⚡ Actions taken: {len(workflow_context.actions_taken)}")
                
                # Print some results
                if workflow_context.results.get("ai_analysis", {}).get("success"):
                    ai_analysis = workflow_context.results["ai_analysis"]["analysis"]
                    print(f"📋 Reorder recommendations: {len(ai_analysis.get('restock_recommendations', []))}")
                    print(f"⚠️  Anomaly alerts: {len(ai_analysis.get('anomaly_alerts', []))}")
                    print(f"🏪 Vendor risks: {len(ai_analysis.get('vendor_risks', []))}")
                
                # Print errors if any
                if workflow_context.errors:
                    print(f"❌ Errors encountered: {len(workflow_context.errors)}")
                    for error in workflow_context.errors:
                        print(f"   - {error}")
            
            elif workflow_context.status.value == "failed":
                print("❌ Workflow failed!")
                for error in workflow_context.errors:
                    print(f"   Error: {error}")
            
            else:
                print(f"⏳ Workflow status: {workflow_context.status.value}")
        
        print("\n" + "="*60)
        print("AI AGENT TEST COMPLETED")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())