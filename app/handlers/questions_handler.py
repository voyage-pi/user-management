from app.services.supabase_client import supabase, supabase_admin

def get_all_questions():
    try:
        response = supabase.table("question") \
            .select("id, question, description, type, attributes_recommendations") \
            .eq("display", True) \
            .order("id", desc=False) \
            .execute()

        print(response.data)

        return response.data

    except Exception as e:
        print("Error fetching questions:", e)
        return []
