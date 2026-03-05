from src.database.connection import DatabaseManager
from src.database.models import User, Candidate, Company, Application

def cleanup_user(email):
    db = DatabaseManager.get_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
            return

        print(f"Found user: {user.name} (ID: {user.id}, Role: {user.role})")
        
        # Cleanup associated data
        if user.role.value == 'CANDIDATE':
            candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
            if candidate:
                # Delete applications
                db.query(Application).filter(Application.candidate_id == candidate.id).delete()
                db.delete(candidate)
                print(f"Deleted candidate profile for ID {user.id}")
        
        elif user.role.value == 'RECRUITER':
            company = db.query(Company).filter(Company.recruiter_id == user.id).first()
            if company:
                # Note: Jobs might be linked to company. For thoroughness:
                # db.query(Job).filter(Job.company_id == company.id).delete()
                db.delete(company)
                print(f"Deleted company profile for ID {user.id}")

        db.delete(user)
        db.commit()
        print(f"Successfully deleted user {email}")
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_user("habeeb@gmail.com")
