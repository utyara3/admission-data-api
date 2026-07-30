from dataclasses import dataclass


@dataclass
class ScraperConfig:
    university_id: str
    university_name: str
    university_short_name: str
    website_url: str
    description: str = ""
