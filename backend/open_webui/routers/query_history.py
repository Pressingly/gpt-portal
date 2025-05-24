from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from open_webui.utils.auth import get_verified_user
from open_webui.moneta.ledger.db_connection import get_db_connection, release_connection
from math import ceil
from datetime import timezone
import json

router = APIRouter()

class QueryHistoryItem(BaseModel):
    query_id: str
    timestamp: str
    llm: str
    input_prompt: str
    input_tokens: int
    output_tokens: int
    input_cost: str
    output_cost: str
    total_cost: str
    metadata: Optional[Dict[str, Any]] = None

class QueryHistoryResponse(BaseModel):
    items: List[QueryHistoryItem]
    total_pages: int
    total_records: int
    current_page: int

@router.get("/", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = 1,
    page_size: int = 20,
    user=Depends(get_verified_user),
    debug: bool = QueryParam(False)
):
    conn = None
    try:
        user_id = user.id
        print(f"Fetching query history for user: {user_id}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # If debug mode, get a sample record to examine the structure
        if debug:
            sample_query = '''
            SELECT 
                "request_id", "startTime", "model", "messages", "metadata"
            FROM "LiteLLM_SpendLogs"
            WHERE "end_user" = %s
            LIMIT 1;
            '''
            cur.execute(sample_query, (user_id,))
            sample_record = cur.fetchone()
            if sample_record:
                print(f"Sample record structure:")
                for i, col in enumerate(cur.description):
                    col_name = col[0]
                    value = sample_record[i]
                    print(f"  {col_name}: {type(value)}")
                    if col_name == "metadata" and value:
                        try:
                            # If already a dict, just use it, otherwise try to parse JSON
                            metadata = value if isinstance(value, dict) else json.loads(value)
                            print(f"  metadata keys: {list(metadata.keys())}")
                            if 'proxy_server_request' in metadata:
                                print(f"  proxy_server_request keys: {list(metadata['proxy_server_request'].keys())}")
                        except Exception as e:
                            print(f"  Error parsing metadata: {e}")
        
        # First, get total count
        count_query = '''
        SELECT COUNT(*) 
        FROM "LiteLLM_SpendLogs"
        WHERE "end_user" = %s;
        '''
        cur.execute(count_query, (user_id,))
        total_records = cur.fetchone()[0]
        print(f"Total records found for user {user_id}: {total_records}")
        
        if total_records == 0:
            return QueryHistoryResponse(
                items=[],
                total_pages=0,
                total_records=0,
                current_page=1
            )
            
        total_pages = ceil(total_records / page_size)
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size
        
        # Main query with pagination
        query = '''
        WITH all_queries AS (
            SELECT 
                "request_id",
                "startTime" AT TIME ZONE 'UTC' AS timestamp,
                "model" AS llm,
                COALESCE(
                    "messages"->0->>'content',
                    metadata->'usage_object'->>'prompt',
                    metadata->'usage_object'->>'prompt_tokens_details',
                    'No prompt available'
                ) AS input_prompt,
                metadata->>'proxy_server_request' AS proxy_server_request,
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
                ), 8)::TEXT AS total_cost,
                metadata
            FROM "LiteLLM_SpendLogs"
            WHERE "end_user" = %s
        ),
        numbered_queries AS (
            SELECT *,
                ROW_NUMBER() OVER (ORDER BY timestamp ASC) AS abs_num
            FROM all_queries
        )
        SELECT 
            LPAD(abs_num::TEXT, 4, '0') AS query_id,
            timestamp,
            llm,
            input_prompt,
            proxy_server_request,
            input_tokens,
            output_tokens,
            input_cost,
            output_cost,
            total_cost,
            metadata
        FROM numbered_queries
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s;
        '''
        
        print(f"Executing query with parameters: user_id={user_id}, page_size={page_size}, offset={offset}")
        cur.execute(query, (user_id, page_size, offset))
        results = cur.fetchall()
        print(f"Query returned {len(results)} results")
        
        # Get column names
        column_names = [desc[0] for desc in cur.description]
        
        # Convert results to list of dictionaries
        items = []
        last_readable_prompt = None
        def is_unreadable(prompt):
            if not prompt or len(prompt) < 5:
                return True
            try:
                obj = json.loads(prompt)
                if isinstance(obj, dict):
                    return True
            except Exception:
                pass
            # Known pattern for audio tokens/cached tokens
            if 'audio_tokens' in prompt and 'cached_tokens' in prompt:
                return True
            return False

        # Process in ascending order (oldest to newest)
        for row in reversed(results):
            row_dict = dict(zip(column_names, row))
            
            # Convert timestamp to ISO format string with timezone
            if 'timestamp' in row_dict and row_dict['timestamp']:
                # Ensure the timestamp is in UTC and includes timezone info
                if row_dict['timestamp'].tzinfo is None:
                    row_dict['timestamp'] = row_dict['timestamp'].replace(tzinfo=timezone.utc)
                row_dict['timestamp'] = row_dict['timestamp'].isoformat()
            
            # Extract input prompt from proxy_server_request if available
            if ('input_prompt' not in row_dict or 
                not row_dict['input_prompt'] or 
                row_dict['input_prompt'] == 'No prompt available' or
                len(row_dict['input_prompt']) < 10):
                
                proxy_request = row_dict.get('proxy_server_request')
                if proxy_request:
                    try:
                        # Parse proxy_server_request which is a JSON string
                        proxy_data = json.loads(proxy_request)
                        # Extract the last user message from messages array
                        messages = proxy_data.get('messages', [])
                        user_messages = [msg for msg in messages if msg.get('role') == 'user']
                        if user_messages:
                            # Get the last user message
                            last_user_message = user_messages[-1]
                            content = last_user_message.get('content')
                            if content and len(content) > 0:
                                row_dict['input_prompt'] = content
                    except (json.JSONDecodeError, TypeError, KeyError) as e:
                        print(f"Error parsing proxy_server_request: {e}")
            
            # Fallback to previous readable prompt if current is unreadable
            prompt = row_dict.get('input_prompt')
            if is_unreadable(prompt):
                row_dict['input_prompt'] = last_readable_prompt or 'No prompt available'
            else:
                last_readable_prompt = prompt
            
            # Remove the proxy_server_request field from the result
            if 'proxy_server_request' in row_dict:
                del row_dict['proxy_server_request']
            
            # Include a limited subset of metadata if available
            if 'metadata' in row_dict and row_dict['metadata']:
                try:
                    # Create a simplified metadata object with only relevant information
                    row_dict['metadata'] = {
                        'completion_id': row_dict['metadata'].get('completion_id', ''),
                        'model_info': row_dict['metadata'].get('model_map_information', {}),
                    }
                except Exception as e:
                    print(f"Error processing metadata: {e}")
                    row_dict['metadata'] = {'error': 'Failed to process metadata'}
            
            items.append(QueryHistoryItem(**row_dict))
        # Reverse items to restore newest-first order
        items.reverse()
        
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