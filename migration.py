# migrate_data.py
import asyncio
import pandas as pd
from typing import Optional, Type # Added Type for model hinting
import os
from dotenv import load_dotenv

from sqlmodel import SQLModel, Field, create_engine # Ensure create_engine is here
from sqlmodel.ext.asyncio.session import AsyncSession # Correct import for AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine # Correct import for AsyncEngine


# --- 1. Load Environment Variables ---
load_dotenv() # This loads variables from your .env file

# --- 2. Retrieve Clever Cloud DB Credentials ---
POSTGRESQL_ADDON_USER = os.getenv('POSTGRESQL_ADDON_USER')
POSTGRESQL_ADDON_PASSWORD = os.getenv('POSTGRESQL_ADDON_PASSWORD')
POSTGRESQL_ADDON_HOST = os.getenv('POSTGRESQL_ADDON_HOST')
POSTGRESQL_ADDON_PORT = os.getenv('POSTGRESQL_ADDON_PORT')
POSTGRESQL_ADDON_DB = os.getenv('POSTGRESQL_ADDON_DB')

# Basic validation for required environment variables
if not all([POSTGRESQL_ADDON_USER, POSTGRESQL_ADDON_PASSWORD, POSTGRESQL_ADDON_HOST, POSTGRESQL_ADDON_PORT, POSTGRESQL_ADDON_DB]):
    raise ValueError("One or more Clever Cloud PostgreSQL environment variables are not set. "
                     "Please check your .env file or environment configuration.")

# --- 3. Construct the Database URL ---
# This URL string is what SQLAlchemy/SQLModel uses to connect
DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRESQL_ADDON_USER}:"
    f"{POSTGRESQL_ADDON_PASSWORD}@"
    f"{POSTGRESQL_ADDON_HOST}:"
    f"{POSTGRESQL_ADDON_PORT}/"
    f"{POSTGRESQL_ADDON_DB}"
)

# --- 4. Initialize the AsyncEngine ---
# This is your connection pool to the database
engine = AsyncEngine(create_engine(DATABASE_URL, echo=False, future=True)) # Set echo=False to reduce log verbosity

# --- 5. Import your SQLModel definitions ---
# Make sure sqlmodels_db.py is in the same directory or accessible via PYTHONPATH
# It should contain your GameSQL and ConsoleSQL models.
try:
    from sqlmodels_db import GameSQL, ConsoleSQL
except ImportError:
    raise ImportError("Could not import GameSQL or ConsoleSQL from sqlmodels_db.py. "
                      "Ensure the file exists and models are correctly defined.")


# --- 6. Database Table Creation Function ---
async def create_db_and_tables():
    """
    Creates database tables based on SQLModel metadata if they don't already exist.
    """
    print("Attempting to create database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database tables created (if they didn't exist).")


# --- 7. CSV Import Functions ---
async def import_data_from_csv(file_path: str, model: Type[SQLModel], session: AsyncSession):
    """
    Imports data from a specified CSV file into the corresponding SQLModel table.
    Handles column normalization, type conversion, and error reporting.
    """
    model_name = model.__name__
    table_name = model.__tablename__ if hasattr(model, '__tablename__') else model_name.lower()
    print(f"\n--- Importing '{model_name}' data from '{file_path}' into table '{table_name}' ---")

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ERROR: CSV file '{file_path}' not found. Skipping import for {model_name}.")
        return
    except Exception as e:
        print(f"ERROR: Could not read CSV file '{file_path}': {e}. Skipping import for {model_name}.")
        return

    # Normalize CSV column names to match SQLModel fields (PascalCase, e.g., 'Game_Title')
    # This loop converts 'game title' -> 'Game_Title', 'released_year' -> 'Released_Year' etc.
    df.columns = [
        '_'.join([word.capitalize() for word in col.replace(' ', '_').replace('.', '').replace('-', '_').split('_')])
        for col in df.columns
    ]

    total_rows = len(df)
    imported_count = 0
    errors_count = 0
    batch_size = 500 # Commit in batches for efficiency

    instances_to_insert = []

    for index, row in df.iterrows():
        try:
            # Convert pandas NaN to Python None for optional fields
            data = row.where(pd.notnull(row), None).to_dict()

            if model == GameSQL:
                # Type conversions and field mapping for GameSQL
                # 'index' is the autoincrementing PK, so we don't provide it here.
                # 'Year' and 'Rank' are integers, sales figures are floats, 'Review' is optional string.
                game_instance = GameSQL(
                    Rank=int(data['Rank']) if data.get('Rank') is not None else None,
                    Game_Title=str(data['Game_Title']),
                    Platform=str(data['Platform']),
                    Year=int(data['Year']) if data.get('Year') is not None else None,
                    Genre=str(data['Genre']),
                    Publisher=str(data['Publisher']),
                    North_America=float(data['North_America']) if data.get('North_America') is not None else None,
                    Europe=float(data['Europe']) if data.get('Europe') is not None else None,
                    Japan=float(data['Japan']) if data.get('Japan') is not None else None,
                    Rest_of_World=float(data['Rest_of_World']) if data.get('Rest_of_World') is not None else None,
                    Global=float(data['Global']) if data.get('Global') is not None else None,
                    Review=str(data['Review']) if data.get('Review') is not None else None
                )
                instances_to_insert.append(game_instance)

            elif model == ConsoleSQL:
                # Type conversions and field mapping for ConsoleSQL
                # 'id' is the autoincrementing PK, so we don't provide it here.
                # 'Released_Year' is int, 'Discontinuation_Year' is optional int, 'Units_Sold' is optional float.
                console_instance = ConsoleSQL(
                    Console_Name=str(data['Console_Name']),
                    Type=str(data['Type']),
                    Company=str(data['Company']),
                    Released_Year=int(data['Released_Year']) if data.get('Released_Year') is not None else None,
                    Discontinuation_Year=int(data['Discontinuation_Year']) if data.get('Discontinuation_Year') is not None else None,
                    Units_Sold=float(data['Units_Sold']) if data.get('Units_Sold') is not None else None
                )
                instances_to_insert.append(console_instance)

            else:
                print(f"WARNING: Model '{model_name}' not supported for CSV import. Skipping row {index}.")
                errors_count += 1
                continue

        except KeyError as e:
            errors_count += 1
            print(f"ERROR: Missing CSV column '{e}' for {model_name} at row {index}. Data: {row.to_dict()}")
            continue
        except ValueError as e:
            errors_count += 1
            print(f"ERROR: Data type conversion failed for {model_name} at row {index}: {e}. Data: {row.to_dict()}")
            continue
        except Exception as e:
            errors_count += 1
            print(f"ERROR: Unexpected error processing row {index} for {model_name}: {e}. Data: {row.to_dict()}")
            continue

        # Add to session and commit in batches
        if len(instances_to_insert) >= batch_size:
            session.add_all(instances_to_insert)
            await session.commit()
            print(f"  --> Inserted {len(instances_to_insert)} {model_name} (total: {imported_count + len(instances_to_insert)})")
            imported_count += len(instances_to_insert)
            instances_to_insert = [] # Clear the batch list

    # Insert any remaining items in the last batch
    if instances_to_insert:
        session.add_all(instances_to_insert)
        await session.commit()
        print(f"  --> Inserted final {len(instances_to_insert)} {model_name} (total: {imported_count + len(instances_to_insert)})")
        imported_count += len(instances_to_insert)

    print(f"--- Import finished for '{model_name}'. Processed: {total_rows} rows, Imported: {imported_count}, Failed: {errors_count}. ---")


# --- 8. Main Migration Function ---
async def main():
    """
    Main function to orchestrate database table creation and CSV data import.
    """
    # Create tables first
    await create_db_and_tables()

    # Define paths to your CSV files
    # IMPORTANT: Adjust these paths if your CSVs are in a different location!
    games_csv_path = "./data/games.csv"
    consoles_csv_path = "./data/consoles.csv"

    # Use a single async session for the import process
    async with AsyncSession(engine) as session:
        await import_data_from_csv(games_csv_path, GameSQL, session)
        await import_data_from_csv(consoles_csv_path, ConsoleSQL, session)

    print("\n--- All CSV data migration complete! ---")


# --- 9. Run the Script ---
if __name__ == "__main__":
    asyncio.run(main())