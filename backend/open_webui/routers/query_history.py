from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from open_webui.utils.auth import get_verified_user
from open_webui.moneta.ledger.db_connection import get_db_connection, release_connection
from math import ceil
from datetime import timezone

router = APIRouter()

class QueryHistoryItem(BaseModel):
    query_id: str
    timestamp: str
    llm: str
    input_prompt: str
    input_tokens: int
    input_cost: str
    output_tokens: int
    output_cost: str
    total_cost: str

class QueryHistoryResponse(BaseModel):
    items: List[QueryHistoryItem]
    total_pages: int
    total_records: int
    current_page: int

@router.get("/", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = 1,
    page_size: int = 8,
    user=Depends(get_verified_user)
):
    conn = None
    try:
        print(f"Fetching query history for user: {user.id}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # First, let's check what end_user values exist in the database
        cur.execute('SELECT DISTINCT "end_user" FROM "LiteLLM_SpendLogs" LIMIT 5;')
        existing_users = cur.fetchall()
        print(f"Sample of existing end_user values in database: {existing_users}")
        
        # First, get total count
        count_query = '''
        SELECT COUNT(*) 
        FROM "LiteLLM_SpendLogs"
        WHERE "end_user" = %s;
        '''
        cur.execute(count_query, (user.id,))
        total_records = cur.fetchone()[0]
        print(f"Total records found for user {user.id}: {total_records}")
        total_pages = ceil(total_records / page_size)
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size
        
        # Main query with pagination
        query = '''
        WITH numbered_queries AS (
            SELECT 
                ROW_NUMBER() OVER (ORDER BY "startTime" ASC)::TEXT AS query_number,
                "request_id",
                "startTime" AT TIME ZONE 'UTC' AS timestamp,
                "model" AS llm,
                COALESCE(
                    "messages"->0->>'content',
                    metadata->'usage_object'->>'prompt_tokens_details',
                    'No prompt available'
                ) AS input_prompt,
                "prompt_tokens" AS input_tokens,
                "completion_tokens" AS output_tokens,
                ROUND(CAST(
                    "prompt_tokens" *
                    COALESCE(
                        (metadata->'model_map_information'->'model_map_value'->>'input_cost_per_token')::FLOAT,
                        0.0
                    )
                    AS NUMERIC
                ), 8)::TEXT AS input_cost,
                ROUND(CAST(
                    "completion_tokens" *
                    COALESCE(
                        (metadata->'model_map_information'->'model_map_value'->>'output_cost_per_token')::FLOAT,
                        0.0
                    )
                    AS NUMERIC
                ), 8)::TEXT AS output_cost,
                ROUND(CAST(
                    ("prompt_tokens" *
                      COALESCE(
                        (metadata->'model_map_information'->'model_map_value'->>'input_cost_per_token')::FLOAT,
                        0.0
                      )
                    +
                     "completion_tokens" *
                      COALESCE(
                        (metadata->'model_map_information'->'model_map_value'->>'output_cost_per_token')::FLOAT,
                        0.0
                      )
                    )
                    AS NUMERIC
                ), 8)::TEXT AS total_cost
            FROM "LiteLLM_SpendLogs"
            WHERE "end_user" = %s
        )
        SELECT 
            LPAD(query_number, 4, '0') AS query_id,
            timestamp,
            llm,
            input_prompt,
            input_tokens,
            output_tokens,
            input_cost,
            output_cost,
            total_cost
        FROM numbered_queries
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s;
        '''
        
        print(f"Executing query with parameters: user_id={user.id}, page_size={page_size}, offset={offset}")
        cur.execute(query, (user.id, page_size, offset))
        results = cur.fetchall()
        print(f"Query returned {len(results)} results")
        
        # Get column names
        column_names = [desc[0] for desc in cur.description]
        
        # Convert results to list of dictionaries
        items = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            # Convert timestamp to ISO format string with timezone
            if 'timestamp' in row_dict and row_dict['timestamp']:
                # Ensure the timestamp is in UTC and includes timezone info
                if row_dict['timestamp'].tzinfo is None:
                    row_dict['timestamp'] = row_dict['timestamp'].replace(tzinfo=timezone.utc)
                row_dict['timestamp'] = row_dict['timestamp'].isoformat()
            items.append(QueryHistoryItem(**row_dict))
        
        cur.close()
        
        return QueryHistoryResponse(
            items=items,
            total_pages=total_pages,
            total_records=total_records,
            current_page=page
        )
    except Exception as e:
        print(f"Error in get_query_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if conn:
            release_connection(conn) 