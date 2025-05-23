from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from db_connection import get_db_connection
import os
from contextlib import asynccontextmanager
from typing import Optional
import atexit
from datetime import datetime, timedelta

app = FastAPI()

# Global connection and tunnel variables
db_connection = None
tunnel = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create initial connection
    global db_connection, tunnel
    try:
        db_connection, tunnel = get_db_connection()
        print("Success: Initial database connection established")
    except Exception as e:
        print(f"Error: {e}")
        db_connection = None
        tunnel = None
    
    yield
    
    # Shutdown: Clean up connections
    if db_connection:
        db_connection.close()
    if tunnel:
        tunnel.stop()
    print("Connections closed")

app = FastAPI(lifespan=lifespan)

# Create necessary directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

def ensure_connection():
    global db_connection, tunnel
    try:
        if db_connection is None or db_connection.closed:
            db_connection, tunnel = get_db_connection()
            print("Success: Database connection reestablished")
    except Exception as e:
        print(f"Error: {e}")
        raise e
    return db_connection

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        # Ensure we have a valid connection
        conn = ensure_connection()
        cur = conn.cursor()
        
        query = '''
        SELECT
          "request_id" AS query_id,
          "startTime" AT TIME ZONE 'UTC' AS timestamp,
          "model" AS llm,
          "messages"->0->>'content' AS input_prompt,
          "prompt_tokens" AS input_tokens,
          "completion_tokens" AS output_tokens,
          ROUND(CAST(
            "prompt_tokens" *
            (metadata->'model_map_information'->'model_map_value'->>'input_cost_per_token')::FLOAT
            AS NUMERIC
          ), 8)::TEXT AS input_cost,
          ROUND(CAST(
            "completion_tokens" *
            (metadata->'model_map_information'->'model_map_value'->>'output_cost_per_token')::FLOAT
            AS NUMERIC
          ), 8)::TEXT AS output_cost,
          ROUND(CAST(
            ("prompt_tokens" *
              (metadata->'model_map_information'->'model_map_value'->>'input_cost_per_token')::FLOAT
            +
             "completion_tokens" *
              (metadata->'model_map_information'->'model_map_value'->>'output_cost_per_token')::FLOAT
            )
            AS NUMERIC
          ), 8)::TEXT AS total_cost
        FROM
          "LiteLLM_SpendLogs"
        WHERE
          "end_user" = '0834a6d1-b476-4a75-abb8-46055793f134'
        ORDER BY
          "startTime" DESC
        LIMIT 10 OFFSET 0;
        '''
        cur.execute(query)
        results = cur.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cur.description]
        
        # Convert results to list of dictionaries
        data = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            # Convert timestamp to ISO format string
            if 'timestamp' in row_dict and row_dict['timestamp']:
                row_dict['timestamp'] = row_dict['timestamp'].isoformat()
            data.append(row_dict)
        
        cur.close()
        
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "data": data, "columns": column_names}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.get("/api/llm-queries-over-time")
async def llm_queries_over_time(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    conn = ensure_connection()
    cur = conn.cursor()
    if not start or not end:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    query = '''
    SELECT 
      DATE("startTime") as day,
      SUM(CASE WHEN "model" ILIKE '%%claude%%' THEN 1 ELSE 0 END) as Claude,
      SUM(CASE WHEN "model" ILIKE '%%gpt%%' THEN 1 ELSE 0 END) as ChatGPT,
      SUM(CASE WHEN "model" ILIKE '%%gemini%%' THEN 1 ELSE 0 END) as Gemini,
      COUNT(*) as Total
    FROM "LiteLLM_SpendLogs"
    WHERE "startTime" BETWEEN %s AND %s
    GROUP BY day
    ORDER BY day;
    '''
    cur.execute(query, (start_date, end_date + timedelta(days=1)))
    rows = cur.fetchall()
    result = [{"day": str(row[0]), "Claude": row[1], "ChatGPT": row[2], "Gemini": row[3], "Total": row[4]} for row in rows]
    cur.close()
    return JSONResponse(content=result)

@app.get("/api/llm-distribution")
async def llm_distribution(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    conn = ensure_connection()
    cur = conn.cursor()
    if not start or not end:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    query = '''
    SELECT COUNT(*) as single_llm
    FROM "LiteLLM_SpendLogs"
    WHERE "startTime" BETWEEN %s AND %s;
    '''
    cur.execute(query, (start_date, end_date + timedelta(days=1)))
    row = cur.fetchone()
    cur.close()
    return JSONResponse(content={"multi_llm": 0, "single_llm": row[0]})

@app.get("/api/llm-breakdown")
async def llm_breakdown(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    conn = ensure_connection()
    cur = conn.cursor()
    if not start or not end:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    query = '''
    SELECT "model", COUNT(*) as count
    FROM "LiteLLM_SpendLogs"
    WHERE "startTime" BETWEEN %s AND %s
    GROUP BY "model";
    '''
    cur.execute(query, (start_date, end_date + timedelta(days=1)))
    rows = cur.fetchall()
    cur.close()
    return JSONResponse(content={row[0]: row[1] for row in rows})

@app.get("/api/llm-combinations")
async def llm_combinations(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    conn = ensure_connection()
    cur = conn.cursor()
    if not start or not end:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    query = '''
    SELECT "model" as combination, COUNT(*) as count
    FROM "LiteLLM_SpendLogs"
    WHERE "startTime" BETWEEN %s AND %s
    GROUP BY "model"
    ORDER BY count DESC;
    '''
    cur.execute(query, (start_date, end_date + timedelta(days=1)))
    rows = cur.fetchall()
    cur.close()
    return JSONResponse(content=[{"combination": row[0], "count": row[1]} for row in rows])

@app.get("/api/average-queries-per-day")
async def average_queries_per_day(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    conn = ensure_connection()
    cur = conn.cursor()
    if not start or not end:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    query = '''
    SELECT AVG(daily_count) as avg_queries
    FROM (
      SELECT DATE("startTime") as day, COUNT(*) as daily_count
      FROM "LiteLLM_SpendLogs"
      WHERE "startTime" BETWEEN %s AND %s
      GROUP BY day
    ) sub;
    '''
    cur.execute(query, (start_date, end_date + timedelta(days=1)))
    row = cur.fetchone()
    cur.close()
    return JSONResponse(content={"average": float(row[0]) if row[0] is not None else 0})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 