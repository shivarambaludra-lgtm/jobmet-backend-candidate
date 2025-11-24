"""
Test database models for Week 7-8 Phase 1
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    print("=" * 60)
    print("Testing Model Imports")
    print("=" * 60)
    
    try:
        from app.models.bookmark import Bookmark
        print("✓ Bookmark model imported")
        
        from app.models.saved_search import SavedSearch
        print("✓ SavedSearch model imported")
        
        from app.models.job_application import JobApplication, ApplicationStatus
        print("✓ JobApplication model imported")
        print("✓ ApplicationStatus enum imported")
        
        from app.models.user_activity import UserActivity
        print("✓ UserActivity model imported")
        
        print("\n" + "=" * 60)
        print("Testing ApplicationStatus Enum")
        print("=" * 60)
        
        statuses = list(ApplicationStatus)
        print(f"\nAvailable statuses ({len(statuses)}):")
        for status in statuses:
            print(f"  - {status.name}: '{status.value}'")
        
        print("\n" + "=" * 60)
        print("✅ All models imported successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error importing models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_attributes():
    print("\n" + "=" * 60)
    print("Testing Model Attributes")
    print("=" * 60)
    
    try:
        from app.models.bookmark import Bookmark
        from app.models.saved_search import SavedSearch
        from app.models.job_application import JobApplication
        from app.models.user_activity import UserActivity
        
        # Test Bookmark attributes
        print("\n📌 Bookmark attributes:")
        bookmark_attrs = ['id', 'user_id', 'job_posting_id', 'notes', 'created_at']
        for attr in bookmark_attrs:
            if hasattr(Bookmark, attr):
                print(f"  ✓ {attr}")
            else:
                print(f"  ❌ {attr} missing")
        
        # Test SavedSearch attributes
        print("\n💾 SavedSearch attributes:")
        search_attrs = ['id', 'user_id', 'name', 'query', 'parsed_query', 
                       'email_alerts', 'alert_frequency', 'last_run_at', 
                       'new_jobs_count', 'created_at', 'is_active']
        for attr in search_attrs:
            if hasattr(SavedSearch, attr):
                print(f"  ✓ {attr}")
            else:
                print(f"  ❌ {attr} missing")
        
        # Test JobApplication attributes
        print("\n📝 JobApplication attributes:")
        app_attrs = ['id', 'user_id', 'job_posting_id', 'status', 'cover_letter',
                    'resume_used', 'applied_at', 'last_updated', 'application_url',
                    'confirmation_email', 'interview_dates', 'notes']
        for attr in app_attrs:
            if hasattr(JobApplication, attr):
                print(f"  ✓ {attr}")
            else:
                print(f"  ❌ {attr} missing")
        
        # Test UserActivity attributes
        print("\n📊 UserActivity attributes:")
        activity_attrs = ['id', 'user_id', 'activity_type', 'activity_data',
                         'job_posting_id', 'session_id', 'ip_address', 
                         'user_agent', 'created_at']
        for attr in activity_attrs:
            if hasattr(UserActivity, attr):
                print(f"  ✓ {attr}")
            else:
                print(f"  ❌ {attr} missing")
        
        print("\n" + "=" * 60)
        print("✅ Model attribute test complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing attributes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        test_model_attributes()
