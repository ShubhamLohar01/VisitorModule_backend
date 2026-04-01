"""
Database initialization script.
Creates all tables and optionally seeds initial data.
"""

from sqlalchemy import inspect
from app.core.database import engine, Base, SessionLocal
from app.core.auth import AuthUtils
from app.models.approver import Approver
from app.models.visitor import Visitor
from app.models.icard import ICard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize the database by creating all tables.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def seed_initial_data():
    """
    Seed the database with initial data (default superuser).
    """
    db = SessionLocal()

    try:
        # Check if any approvers exist
        existing_approvers = db.query(Approver).count()

        if existing_approvers == 0:
            logger.info("No approvers found. Creating default superuser...")

            # Create default superuser
            default_superuser = Approver(
                username="admin",
                email="admin@example.com",
                name="System Administrator",
                hashed_password=AuthUtils.hash_password("admin123"),
                superuser=True,
                is_active=True
            )

            db.add(default_superuser)
            db.commit()

            logger.info("Default superuser created successfully!")
            logger.info("Username: admin")
            logger.info("Password: admin123")
            logger.info("IMPORTANT: Please change the default password after first login!")
        else:
            logger.info(f"Database already has {existing_approvers} approver(s). Skipping seed data.")

    except Exception as e:
        logger.error(f"Error seeding initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_icards():
    """
    Seed the database with initial ICards if they don't exist.
    """
    db = SessionLocal()

    try:
        # Check if any ICards exist
        existing_icards = db.query(ICard).count()

        if existing_icards == 0:
            logger.info("No ICards found. Creating default ICards...")

            # Define the ICards to create
            icards_to_create = []

            # Customer Cards (CU001-CU005)
            for i in range(1, 6):
                icards_to_create.append(ICard(
                    card_name=f"CU{i:03d}",
                    icard_name=f"customer_{i}_card",
                    occ_status=False,
                    occ_to=None
                ))

            # Vendor Cards (VE001-VE005)
            for i in range(1, 6):
                icards_to_create.append(ICard(
                    card_name=f"VE{i:03d}",
                    icard_name=f"vendor_{i}_card",
                    occ_status=False,
                    occ_to=None
                ))

            # Visitor Cards (VI001-VI005)
            for i in range(1, 6):
                icards_to_create.append(ICard(
                    card_name=f"VI{i:03d}",
                    icard_name=f"visitor_{i}_card",
                    occ_status=False,
                    occ_to=None
                ))

            # Add all ICards to the database
            db.add_all(icards_to_create)
            db.commit()

            logger.info(f"Successfully created {len(icards_to_create)} ICards!")
            logger.info("ICard types created:")
            logger.info("  - Customer Cards: CU001-CU005")
            logger.info("  - Vendor Cards: VE001-VE005")
            logger.info("  - Visitor Cards: VI001-VI005")
        else:
            logger.info(f"Database already has {existing_icards} ICard(s). Skipping ICard seed data.")

    except Exception as e:
        logger.error(f"Error seeding ICards: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_tables():
    """
    Check which tables exist in the database.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    logger.info("Existing tables in database:")
    for table in tables:
        logger.info(f"  - {table}")

    return tables


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Database Initialization Script")
    logger.info("=" * 50)

    # Check existing tables
    check_tables()

    # Initialize database
    init_db()

    # Seed initial data
    seed_initial_data()

    # Seed ICards
    seed_icards()

    # Check tables again
    check_tables()

    logger.info("=" * 50)
    logger.info("Database initialization complete!")
    logger.info("=" * 50)
