import os
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://book_catalog_l1mv_user:HMb59Hj8vzIgb3IyLtQTKy9rQ0bN8lDy@dpg-d0ns64buibrs73c4dacg-a.singapore-postgres.render.com/book_catalog_l1mv")

settings = Settings()
print(settings.DATABASE_URL)
