from typing import List
from pydantic import BaseModel, Field


class SQLGenerationResponse(BaseModel):
    sql_query: str = Field(
        description="The formatted, production-ready SQL query answering the user request"
    )
    dialect: str = Field(
        description="Database dialect used (e.g., PostgreSQL, MySQL, SQLite, Snowflake)"
    )
    explanation: str = Field(
        description="Clear 2-sentence explanation of how the query works and joins tables"
    )
    tables_involved: List[str] = Field(
        description="List of database tables referenced in the query"
    )
    potential_edge_cases: List[str] = Field(
        description="Notes on performance, null handling, indexing, or edge cases"
    )
