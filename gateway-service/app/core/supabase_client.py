from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Get a Supabase client using the anon key (respects RLS).
    Used for user-facing operations like auth.
    """
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase


def get_service_client() -> Client:
    """
    Get a Supabase client using the service-role key (bypasses RLS).
    Used for backend operations like inserting scan_jobs and scan_results.
    """
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    supabase: Client = create_client(settings.SUPABASE_URL, key)
    return supabase


# Global clients for reuse
supabase_client = get_supabase_client()
service_client = get_service_client()
