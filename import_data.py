# VOPS-Hub/import_data.py
import os
import django
import pandas as pd
from datetime import datetime
from django.utils import timezone # NEW IMPORT

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vops_info_hub.settings')
django.setup()

# Import your models after Django setup
from core_app.models import VesselParticulars, VesselDeckHeight, VesselComment

def import_data_from_excel(file_path):
    """
    Imports data from a multi-sheet Excel file into Django models
    based on the simplified structure and latest column headers.
    """
    try:
        # --- Import VesselParticulars ---
        print("Importing Vessel Details...")
        df_vessels = pd.read_excel(file_path, sheet_name='Vessel Details')
        for index, row in df_vessels.iterrows():
            capacity_value = pd.to_numeric(row.get('Capacity'), errors='coerce')
            if pd.isna(capacity_value):
                capacity_value = None

            VesselParticulars.objects.create(
                vessel_name=row['Vessel Name'],
                capacity=capacity_value,
                number_of_decks=row.get('Number of Decks'),
                general_notes=row.get('General Notes'),
                additional_hazards=row.get('Additional Hazards'),
                deck_layout_link=row.get('Deck Layout Link'),
                risk_assessment_document_link=row.get('Risk Assessment Document Link'),
            )
        print(f"Successfully imported {len(df_vessels)} Vessel Details.")

        # --- Import VesselDeckHeight ---
        print("Importing Deck Heights...")
        df_decks = pd.read_excel(file_path, sheet_name='Deck Heights')
        for index, row in df_decks.iterrows():
            try:
                vessel_name = row['Vessel']
                vessel = VesselParticulars.objects.get(vessel_name=vessel_name)

                deck_number_value = str(row['Deck Number']) if pd.notna(row.get('Deck Number')) else ''

                VesselDeckHeight.objects.create(
                    vessel=vessel,
                    deck_number=deck_number_value,
                    average_deck_height_m=row.get('Average Deck Height (m)'),
                    deck_type=row.get('Deck Type'),
                    notes=row.get('Notes'),
                )
            except VesselParticulars.DoesNotExist:
                print(f"Warning: Vessel '{row['Vessel']}' not found for deck height entry (row {index}). Skipping.")
            except KeyError as e:
                print(f"Error: Missing expected column in 'Deck Heights' sheet for row {index}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred importing Deck Height for row {index}: {e}")
        print(f"Successfully imported {len(df_decks)} Deck Heights (some might be skipped if vessel not found).")

        # --- Import VesselComment ---
        print("Importing Comments...")
        df_comments = pd.read_excel(file_path, sheet_name='Comments')
        for index, row in df_comments.iterrows():
            related_vessel_obj = None
            if 'Related Vessel' in row and pd.notna(row['Related Vessel']):
                try:
                    vessel_name_comment = row['Related Vessel']
                    related_vessel_obj = VesselParticulars.objects.get(vessel_name=vessel_name_comment)
                except VesselParticulars.DoesNotExist:
                    print(f"Warning: Related vessel '{row['Related Vessel']}' not found for comment (row {index}). Comment will be saved without vessel link.")

            date_of_comment_excel = row.get('Date of Comment')
            if pd.notna(date_of_comment_excel):
                if isinstance(date_of_comment_excel, (datetime, pd.Timestamp)):
                    # Ensure it's a datetime object for make_aware
                    naive_dt = date_of_comment_excel.to_pydatetime() if isinstance(date_of_comment_excel, pd.Timestamp) else date_of_comment_excel
                    date_of_comment = timezone.make_aware(naive_dt) # MAKE AWARE
                else:
                    try:
                        naive_dt = pd.to_datetime(str(date_of_comment_excel))
                        date_of_comment = timezone.make_aware(naive_dt) # MAKE AWARE
                    except ValueError:
                        print(f"Warning: Could not parse 'Date of Comment' '{date_of_comment_excel}' for row {index}. Using current aware time.")
                        date_of_comment = timezone.now() # Fallback to current aware time
            else:
                date_of_comment = timezone.now() # Fallback to current aware time if blank/missing

            VesselComment.objects.create(
                comment_title=row['Comment Title'],
                comment_details=row['Comment Details'],
                date_of_comment=date_of_comment,
                comment_by=row.get('Comment By'),
                related_vessel=related_vessel_obj,
            )
        print(f"Successfully imported {len(df_comments)} Comments (some might be unlinked).")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the project root.")
    except KeyError as e:
        print(f"Error: Missing expected column in Excel file. Please check column names in your Excel sheets: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during import: {e}")

# --- Main execution ---
if __name__ == "__main__":
    excel_file_name = "Vessel Hazards.xlsx" # <--- IMPORTANT: Change this to your actual Excel file name if different!
    import_data_from_excel(excel_file_name)