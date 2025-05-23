from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, RootModel
from open_webui.utils.auth import get_verified_user
from open_webui.moneta.ledger.db_connection import get_db_connection, release_connection
from collections import Counter

router = APIRouter()

class QueriesOverTimeResponse(BaseModel):
    day: str
    Claude: int
    ChatGPT: int
    Gemini: int
    Total: int

class LLMDistributionResponse(BaseModel):
    single_llm: int
    multi_llm: int

class LLMBreakdownResponse(RootModel):
    root: Dict[str, int]

@router.get("/llm-queries-over-time", response_model=List[QueriesOverTimeResponse])
async def llm_queries_over_time(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user=Depends(get_verified_user)
):
    conn = None
    try:
        print(f"Fetching queries over time for user: {user.id}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not start or not end:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()

        user_id = user.id
        query = '''
        SELECT 
            DATE("startTime") as day,
            SUM(CASE WHEN "model" ILIKE '%%claude%%' THEN 1 ELSE 0 END) as Claude,
            SUM(CASE WHEN "model" ILIKE '%%gpt%%' THEN 1 ELSE 0 END) as ChatGPT,
            SUM(CASE WHEN "model" ILIKE '%%gemini%%' THEN 1 ELSE 0 END) as Gemini,
            COUNT(*) as Total
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" BETWEEN %s AND %s
        AND "end_user" = %s
        GROUP BY day
        ORDER BY day;
        '''
        print(f"Executing query with parameters: start_date={start_date}, end_date={end_date}, user_id={user_id}")
        cur.execute(query, (start_date, end_date + timedelta(days=1), user_id))
        rows = cur.fetchall()
        print(f"Query returned {len(rows)} results")
        
        if not rows:
            result = []
            current_date = start_date
            while current_date <= end_date:
                result.append({
                    "day": str(current_date),
                    "Claude": 0,
                    "ChatGPT": 0,
                    "Gemini": 0,
                    "Total": 0
                })
                current_date += timedelta(days=1)
        else:
            result = [{"day": str(row[0]), "Claude": row[1], "ChatGPT": row[2], "Gemini": row[3], "Total": row[4]} for row in rows]
        
        cur.close()
        return result
    except Exception as e:
        print(f"Error in llm_queries_over_time: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if conn:
            release_connection(conn)

@router.get("/llm-distribution", response_model=LLMDistributionResponse)
async def llm_distribution(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user=Depends(get_verified_user)
):
    conn = None
    try:
        print(f"Fetching LLM distribution for user: {user.id}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not start or not end:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()

        user_id = user.id
        # Fetch all queries for the user in the date range
        query = '''
        SELECT "startTime", "model"
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" BETWEEN %s AND %s
        AND "end_user" = %s
        ORDER BY "startTime"
        '''
        cur.execute(query, (start_date, end_date + timedelta(days=1), user_id))
        rows = cur.fetchall()
        cur.close()

        # Group queries by 1-second windows
        used = set()
        multi_llm = 0
        single_llm = 0
        i = 0
        n = len(rows)
        while i < n:
            t0 = rows[i][0]
            window_models = set()
            window_indices = []
            j = i
            while j < n and abs((rows[j][0] - t0).total_seconds()) <= 1:
                window_models.add(rows[j][1])
                window_indices.append(j)
                j += 1
            if not any(idx in used for idx in window_indices):
                if len(window_models) > 1:
                    multi_llm += 1
                else:
                    single_llm += 1
                used.update(window_indices)
            i = j
        return {"single_llm": single_llm, "multi_llm": multi_llm}
    except Exception as e:
        print(f"Error in llm_distribution: {str(e)}")
        return {"single_llm": 0, "multi_llm": 0}
    finally:
        if conn:
            release_connection(conn)

@router.get("/llm-breakdown", response_model=LLMBreakdownResponse)
async def llm_breakdown(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user=Depends(get_verified_user)
):
    conn = None
    try:
        print(f"Fetching LLM breakdown for user: {user.id}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not start or not end:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()

        user_id = user.id
        query = '''
        SELECT 
            CASE 
                WHEN "model" ILIKE '%%claude%%' THEN 'Claude'
                WHEN "model" ILIKE '%%gpt%%' THEN 'ChatGPT'
                WHEN "model" ILIKE '%%gemini%%' THEN 'Gemini'
                ELSE 'Other'
            END as model_type,
            COUNT(*) as count
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" BETWEEN %s AND %s
        AND "end_user" = %s
        GROUP BY model_type;
        '''
        print(f"Executing query with parameters: start_date={start_date}, end_date={end_date}, user_id={user_id}")
        cur.execute(query, (start_date, end_date + timedelta(days=1), user_id))
        rows = cur.fetchall()
        print(f"Query returned {len(rows)} results")
        
        if not rows:
            result = {"Claude": 0, "ChatGPT": 0, "Gemini": 0, "Other": 0}
        else:
            result = {row[0]: row[1] for row in rows}
            
        cur.close()
        return result
    except Exception as e:
        print(f"Error in llm_breakdown: {str(e)}")
        return {"Claude": 0, "ChatGPT": 0, "Gemini": 0, "Other": 0}
    finally:
        if conn:
            release_connection(conn)

@router.get("/llm-combinations")
async def llm_combinations(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user=Depends(get_verified_user)
):
    conn = None
    try:
        print(f"Fetching LLM combinations for user: {user.id}")
        conn = get_db_connection()
        cur = conn.cursor()
        if not start or not end:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        user_id = user.id
        query = '''
        SELECT "startTime", "model"
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" BETWEEN %s AND %s
        AND "end_user" = %s
        ORDER BY "startTime"
        '''
        cur.execute(query, (start_date, end_date + timedelta(days=1), user_id))
        rows = cur.fetchall()
        cur.close()

        # Group queries by 1-second windows
        used = set()
        combo_counter = Counter()
        i = 0
        n = len(rows)
        while i < n:
            t0 = rows[i][0]
            window_models = set()
            window_indices = []
            j = i
            while j < n and abs((rows[j][0] - t0).total_seconds()) <= 1:
                window_models.add(rows[j][1])
                window_indices.append(j)
                j += 1
            if not any(idx in used for idx in window_indices):
                if len(window_models) > 1:
                    combo = '+'.join(sorted(window_models))
                    combo_counter[combo] += 1
                used.update(window_indices)
            i = j
        return [{"combination": k, "count": v} for k, v in combo_counter.most_common()]
    except Exception as e:
        print(f"Error in llm_combinations: {str(e)}")
        return []
    finally:
        if conn:
            release_connection(conn) 