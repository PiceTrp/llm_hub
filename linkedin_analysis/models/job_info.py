from pydantic import BaseModel

class JobDescription:
    """
    Job data fields
    """
    job_title: str
    location: str
    company_name: str
    job_level: str
    job_description: str
