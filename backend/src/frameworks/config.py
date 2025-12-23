import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        Ensure the URL uses the asyncpg driver and removes unsupported 'sslmode'.
        """
        url = self.DATABASE_URL
        if not url:
            return ""

        # Switch driver
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Remove sslmode param as asyncpg doesn't use it in URL query
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            params_to_remove = ["sslmode", "channel_binding", "options"]
            for param in params_to_remove:
                if param in qs:
                    del qs[param]

            # Rebuild query
            new_query = urlencode(qs, doseq=True)
            parsed = parsed._replace(query=new_query)
            url = urlunparse(parsed)
        except Exception:
            # Fallback if parsing fails, mostly just return the url as is (with driver switched)
            pass

        return url

settings = Settings()
