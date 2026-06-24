from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import base64
import json
import logging
import os
import uuid
import pathlib

from dotenv import load_dotenv
load_dotenv()

from google.adk.apps import App, ResumabilityConfig
from google.adk.runners import InMemoryRunner
from google.genai import types

from aeroops_ai.agent import root_agent as aeroops_root

# Telemetry: Set otel_to_cloud=False
os.environ["OTEL_TO_CLOUD"] = "False"

# Logging: Use standard Python logging for console logs.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AeroOps AI Server")

# Mount static files
static_dir = pathlib.Path(__file__).parent / "static"
templates_dir = pathlib.Path(__file__).parent / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Mount static files and set template directory using absolute paths
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
jinja_templates = Jinja2Templates(directory=str(templates_dir))

# Ensure experimental directories exist
static_experimental_dir = pathlib.Path(__file__).parent / "static_experimental"
templates_experimental_dir = pathlib.Path(__file__).parent / "templates_experimental"
static_experimental_dir.mkdir(exist_ok=True)
templates_experimental_dir.mkdir(exist_ok=True)

# Mount experimental static files
app.mount("/static_experimental", StaticFiles(directory=str(static_experimental_dir)), name="static_experimental")


# Initialize ADK Apps
aeroops_adk_app = App(
    name="aeroops_ai",
    root_agent=aeroops_root,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
aeroops_runner = InMemoryRunner(app=aeroops_adk_app)

# ---------------------------------------------------------------------
# Dashboard route
# ---------------------------------------------------------------------

@app.get("/")
@app.get("/index.html")
async def read_dashboard(request: Request):
    """Render the AeroOps AI dashboard."""
    try:
        index_path = templates_experimental_dir / "index.html"
        html_content = index_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        logger.error(f"Experimental dashboard render error: {e}")
        return HTMLResponse(content="<h1>Experimental Dashboard error</h1><p>Unable to load dashboard.</p>", status_code=500)

# ---------------------------------------------------------------------
# Pub/Sub Trigger
# ---------------------------------------------------------------------

@app.post("/")
@app.post("/apps/{app_name}/trigger/pubsub")
async def handle_pubsub(request: Request, app_name: str = "aeroops_ai"):
    """Accepts Pub/Sub push messages and feeds them to the corresponding workflow."""
    try:
        envelope = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    message = envelope.get("message", {})
    subscription = envelope.get("subscription", "projects/local/subscriptions/default")
    short_name = subscription.split("/")[-1]
    user_id = short_name

    runner = aeroops_runner
    app_name_key = "aeroops_ai"
    session_prefix = "aeroops"

    message_id = message.get("messageId")
    if not message_id:
        message_id = f"unknown_{uuid.uuid4().hex[:8]}"
    session_id = f"{session_prefix}_{message_id}"

    data = message.get("data")
    if data:
        try:
            try:
                decoded = base64.b64decode(data).decode('utf-8')
                json_data = json.loads(decoded)
            except Exception:
                json_data = {"data": data}

            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=json.dumps(json_data))]
            )

            session = await runner.session_service.create_session(
                app_name=app_name_key,
                user_id=user_id,
                session_id=session_id
            )

            logger.info(f"Triggering {app_name_key} workflow: user: {user_id}, session: {session.id}")

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                if event.output is not None:
                    logger.info(f"Workflow output: {event.output}")

        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {"status": "error", "message": str(e)}

    return {"status": "processed"}

# ---------------------------------------------------------------------
# AeroOps AI Direct REST Endpoints
# ---------------------------------------------------------------------

@app.post("/aeroops/run")
async def run_aeroops_directly(payload: dict):
    """Direct POST trigger to run a flight operations analysis workflow."""
    session_id = payload.get("session_id") or f"aeroops_{uuid.uuid4().hex[:8]}"
    user_id = payload.get("user_id") or "local_dispatcher"

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=json.dumps(payload))]
    )

    try:
        session = await aeroops_runner.session_service.create_session(
            app_name="aeroops_ai",
            user_id=user_id,
            session_id=session_id
        )
    except Exception:
        session = await aeroops_runner.session_service.get_session(
            app_name="aeroops_ai",
            session_id=session_id
        )

    outputs = []
    interrupts = []

    try:
        async for event in aeroops_runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.output is not None:
                outputs.append(event.output)
            if hasattr(event, "interrupt_ids") and event.interrupt_ids:
                state = await aeroops_runner.session_service.get_session_state(
                    app_name="aeroops_ai",
                    session_id=session_id
                )
                interrupts.append({
                    "session_id": session_id,
                    "interrupt_ids": list(event.interrupt_ids)
                })
    except Exception as e:
        logger.error(f"Error in running AeroOps directly: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "session_id": session_id,
        "status": "suspended" if interrupts else "completed",
        "interrupts": interrupts,
        "outputs": outputs,
    }

@app.post("/aeroops/resume")
async def resume_aeroops(payload: dict):
    """Submit a response to a pending human review interrupt."""
    session_id = payload.get("session_id")
    user_id = payload.get("user_id") or "local_dispatcher"
    decision = payload.get("decision")  # "approve" or "override: ACTION [comments]"

    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")
    if not decision:
        raise HTTPException(status_code=400, detail="Missing decision")

    resume_message = types.Content(
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    name="human_review_response",
                    id="human_decision",
                    response={"decision": decision}
                )
            )
        ]
    )

    outputs = []
    try:
        async for event in aeroops_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=resume_message
        ):
            if event.output is not None:
                outputs.append(event.output)
    except Exception as e:
        logger.error(f"Error in resuming AeroOps: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "session_id": session_id,
        "status": "completed",
        "outputs": outputs,
    }

# ---------------------------------------------------------------------
# End of file
# ---------------------------------------------------------------------
