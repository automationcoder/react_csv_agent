from pydantic import BaseModel, Field
from typing import Dict, List


class CalculatorParams(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate, example: '2 + 3 * 4'.", min_length=1)


class ListDataFilesParams(BaseModel):
    folder: str = Field(default="project/data", description="Folder where uploaded local files are stored.")


class ReadFileParams(BaseModel):
    path: str = Field(description="Path to a local text file.", min_length=1)
    max_chars: int = Field(default=3000, description="Maximum characters returned from the file.", ge=100, le=20000)


class ReadCsvParams(BaseModel):
    path: str = Field(description="Path to the local CSV file.", min_length=1)
    sample_rows: int = Field(default=5, description="Number of sample rows to return.", ge=1, le=20)


class AggregateCsvParams(BaseModel):
    path: str = Field(description="Path to the local CSV file.", min_length=1)
    group_by: List[str] = Field(description="Columns used for grouping, example: ['region'].", min_length=1)
    aggregations: Dict[str, str] = Field(description="Aggregation map, example: {'quantity': 'sum'}. Supported: sum, mean, count, min, max.")
