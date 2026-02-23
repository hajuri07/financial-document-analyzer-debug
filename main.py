import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from crewai import Crew, Process

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tasks import verification, analyze_financial_document as analyze_task, investment_analysis, risk_assessment
from database import init_db, get_db, AnalysisResult

app = FastAPI(title="Financial Document Analyzer", version="2.0.0")


@app.on_event("startup")
def startup_event():
    init_db()  # create DB tables when server starts


def run_crew(query: str, file_path: str):
    """Run the full CrewAI pipeline"""
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_task, investment_analysis, risk_assessment],
        process=Process.sequential,
    )
    result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check"""
    return {"message": "Financial Document Analyzer API is running", "version": "2.0.0"}


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """
    Upload a financial PDF and get a full analysis.
    Result is saved to the database and returned in the response.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not query or not query.strip():
        query = "Analyze this financial document for investment insights"

    job_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{job_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Run the crew
        response = run_crew(query=query.strip(), file_path=file_path)

        # Save result to database
        analysis = AnalysisResult(
            id=job_id,
            filename=file.filename,
            query=query.strip(),
            status="completed",
            result=str(response)
        )
        db.add(analysis)
        db.commit()

        return {
            "status": "success",
            "job_id": job_id,
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        # Save failed result to database too
        analysis = AnalysisResult(
            id=job_id,
            filename=file.filename,
            query=query.strip(),
            status="failed",
            result=str(e)
        )
        db.add(analysis)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@app.get("/history")
async def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """Get the last N analysis results from the database"""
    jobs = (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "total": len(jobs),
        "results": [
            {
                "job_id": j.id,
                "filename": j.filename,
                "query": j.query,
                "status": j.status,
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ]
    }


@app.get("/result/{job_id}")
async def get_result(job_id: str, db: Session = Depends(get_db)):
    """Fetch a specific analysis result by job_id"""
    job = db.query(AnalysisResult).filter(AnalysisResult.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"No result found for job {job_id}")
    return {
        "job_id": job.id,
        "filename": job.filename,
        "query": job.query,
        "status": job.status,
        "analysis": job.result,
        "created_at": job.created_at.isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
