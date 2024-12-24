from app import create_app, db
from app.models import ScrapedData
import csv

# Create the app instance
app = create_app()

def import_csv_to_db(file_path):
    """
    Imports data from a CSV file into the ScrapedData table in the database.

    Args:
        file_path (str): The path to the CSV file.
    """
    try:
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            
            # Prepare data for bulk insertion
            data = [
                ScrapedData(
                    name=row['name'],
                    link=row['link'],
                    ingredients=row.get('cleaned_ingredients', row.get('ingredients')),  # Use available column
                    brand=row['brand']
                )
                for row in reader
            ]
            
            # Add and commit data to the database
            with app.app_context():
                db.session.bulk_save_objects(data)
                db.session.commit()
            print(f"Successfully imported {len(data)} records from {file_path}")
    except KeyError as e:
        print(f"Missing column in CSV file {file_path}: {e}")
    except Exception as e:
        print(f"Error importing data from {file_path}: {e}")

if __name__ == "__main__":
    csv_files = [
        'cerave.csv',  # Adjusted to the root directory
        'krave.csv',
        'peachandlily.csv',
        'glossier.csv',
        'paula.csv'
    ]
    for file in csv_files:
        import_csv_to_db(file)
