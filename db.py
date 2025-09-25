import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(url, key)

# ============================
# USERS CRUD
# ============================

# Create a new user
def create_user(username, email, password_hash):
    data = {
        "username": username,
        "email": email,
        "password_hash": password_hash
    }
    response = supabase.table("users").insert(data).execute()
    return response

# Get all users
def get_all_users():
    response = supabase.table("users").select("*").execute()
    return response

# Get a single user by ID
def get_user_by_id(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response

# Update a user
def update_user(user_id, username=None, email=None, password_hash=None):
    data = {}
    if username:
        data["username"] = username
    if email:
        data["email"] = email
    if password_hash:
        data["password_hash"] = password_hash

    response = supabase.table("users").update(data).eq("id", user_id).execute()
    return response

# Delete a user
def delete_user(user_id):
    response = supabase.table("users").delete().eq("id", user_id).execute()
    return response


# ============================
# JOURNAL ENTRIES CRUD
# ============================

# Create a new journal entry
def create_entry(user_id, content, mood=None, tags=None):
    data = {
        "user_id": user_id,
        "content": content,
        "mood": mood,
        "tags": tags if tags else []  # store tags as an array
    }
    response = supabase.table("entries").insert(data).execute()
    return response

# Get all entries (with optional filters)
def get_all_entries(limit=50, offset=0):
    response = (
        supabase.table("entries")
        .select("*")
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response

# Get entries by user
def get_entries_by_user(user_id, limit=50, offset=0):
    response = (
        supabase.table("entries")
        .select("*")
        .eq("user_id", user_id)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response

# Filter entries by mood
def filter_entries_by_mood(mood, limit=50, offset=0):
    response = (
        supabase.table("entries")
        .select("*")
        .eq("mood", mood)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response

# Filter entries by tag
def filter_entries_by_tag(tag, limit=50, offset=0):
    response = (
        supabase.table("entries")
        .select("*")
        .contains("tags", [tag])  # checks if tag is inside array
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response

# Update a journal entry
def update_entry(entry_id, content=None, mood=None, tags=None):
    data = {}
    if content:
        data["content"] = content
    if mood:
        data["mood"] = mood
    if tags is not None:
        data["tags"] = tags  # full overwrite of tags array

    response = supabase.table("entries").update(data).eq("id", entry_id).execute()
    return response

# Delete a journal entry
def delete_entry(entry_id):
    response = supabase.table("entries").delete().eq("id", entry_id).execute()
    return response


# ============================
# SEARCH & ANALYTICS
# ============================

# Full-text search on entries (title + content)
def search_entries(query, limit=50, offset=0):
    response = (
        supabase.table("entries")
        .select("*")
        .text_search("content", query)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response

# Get mood statistics for a user
def get_mood_statistics(user_id):
    response = (
        supabase.rpc("get_mood_statistics", {"p_user_id": user_id}).execute()
    )
    return response
