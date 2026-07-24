from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.export import export_to_excel
from app.models import ProjectRequest, ProjectSummary
from app.service import calculate_project

app = FastAPI(title="Sergek APK Calculator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/calculate", response_model=ProjectSummary)
def calculate(req: ProjectRequest) -> ProjectSummary:
    try:
        return calculate_project(req)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/export/excel")
def export_excel(req: ProjectRequest) -> Response:
    try:
        summary = calculate_project(req)
        data = export_to_excel(summary)
        filename = f"{summary.name or 'spec'}.xlsx"
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
