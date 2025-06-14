# VOPS-Hub/import_data.py
import os
import django
import pandas as pd
from datetime import datetime
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vops_info_hub.settings')
django.setup()

# Import your models after Django setup
from core_app.models import VesselParticulars, VesselDeckHeight, VesselComment

# Helper function to safely get values from DataFrame rows
def get_safe_value(row, column_name, default_value=None, data_type=None):
    """
    Retrieves a value from a DataFrame row, handling NaN/NaT,
    and optionally converting to a specific type.
    """
    value = row.get(column_name)
    if pd.isna(value): # Checks for NaN, NaT (Not a Time), None
        return default_value

    if data_type == 'int':
        try:
            # pandas might read numbers as floats, convert to int, then handle empty
            return int(value) if pd.notna(value) and str(value).strip() != '' else default_value
        except (ValueError, TypeError):
            return default_value
    elif data_type == 'float':
        try:
            return float(value) if pd.notna(value) and str(value).strip() != '' else default_value
        except (ValueError, TypeError):
            return default_value
    elif data_type == 'str':
        return str(value).strip() # Convert to string and remove leading/trailing whitespace

    return value


def import_data_from_excel(file_path):
    """
    Imports data from a multi-sheet Excel file into Django models
    based on the simplified structure and latest column headers.
    """
    try:
        # --- Import VesselParticulars ---
        print("Importing Vessel Details...")
        df_vessels = pd.read_excel(file_path, sheet_name='Vessel Details') # Updated sheet name to 'Vessel details'
        for index, row in df_vessels.iterrows():
            # Capacity is numeric, so NaN should become None
            capacity_value = get_safe_value(row, 'Capacity', default_value=None, data_type='float')

            # Number of decks is numeric, so NaN should become None
            number_of_decks_value = get_safe_value(row, 'Number of Decks', default_value=None, data_type='int')

            VesselParticulars.objects.create(
                vessel_name=get_safe_value(row, 'Vessel Name', default_value='', data_type='str'),
                capacity=capacity_value,
                number_of_decks=number_of_decks_value,
                general_notes=get_safe_value(row, 'General Notes', default_value='', data_type='str'),
                additional_hazards=get_safe_value(row, 'Additional Hazards', default_value='', data_type='str'),
                deck_layout_link=get_safe_value(row, 'Deck Layout Link', default_value='', data_type='str'),
                risk_assessment_document_link=get_safe_value(row, 'Risk Assessment Document Link', default_value='', data_type='str'),
                vessel_info_link=get_safe_value(row, 'Vessel Info Link', default_value='', data_type='str'), # NEW FIELD
            )
        print(f"Successfully imported {len(df_vessels)} Vessel Details.")

        # --- Import VesselDeckHeight ---
        print("Importing Deck Heights...")
        df_decks = pd.read_excel(file_path, sheet_name='Deck Heights')
        for index, row in df_decks.iterrows():
            try:
                vessel_name = get_safe_value(row, 'Vessel', default_value='', data_type='str')
                vessel = VesselParticulars.objects.get(vessel_name=vessel_name)

                # Deck Id is integer
                deck_id_value = get_safe_value(row, 'Deck Id', default_value=None, data_type='int')
                # Deck is alphanumeric name
                deck_name_value = get_safe_value(row, 'Deck', default_value='', data_type='str')
                # Average deck height is numeric, so NaN should become None
                average_deck_height_m_value = get_safe_value(row, 'Average Deck Height (m)', default_value=None, data_type='float')

                VesselDeckHeight.objects.create(
                    vessel=vessel,
                    deck_id=deck_id_value, # NEW FIELD MAPPING
                    deck_name=deck_name_value, # NEW FIELD MAPPING
                    average_deck_height_m=average_deck_height_m_value,
                    deck_type=get_safe_value(row, 'Deck Type', default_value='', data_type='str'),
                    notes=get_safe_value(row, 'Notes', default_value='', data_type='str'),
                )
            except VesselParticulars.DoesNotExist:
                print(f"Warning: Vessel '{get_safe_value(row, 'Vessel', default_value='N/A', data_type='str')}' not found for deck height entry (row {index}). Skipping.")
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
                    vessel_name_comment = get_safe_value(row, 'Related Vessel', default_value='', data_type='str')
                    related_vessel_obj = VesselParticulars.objects.get(vessel_name=vessel_name_comment)
                except VesselParticulars.DoesNotExist:
                    print(f"Warning: Related vessel '{vessel_name_comment}' not found for comment (row {index}). Comment will be saved without vessel link.")

            date_of_comment_excel = row.get('Date of Comment')
            if pd.notna(date_of_comment_excel):
                if isinstance(date_of_comment_excel, (datetime, pd.Timestamp)):
                    naive_dt = date_of_comment_excel.to_pydatetime() if isinstance(date_of_comment_excel, pd.Timestamp) else date_of_comment_excel
                    date_of_comment = timezone.make_aware(naive_dt)
                else:
                    try:
                        naive_dt = pd.to_datetime(str(date_of_comment_excel))
                        date_of_comment = timezone.make_aware(naive_dt)
                    except ValueError:
                        print(f"Warning: Could not parse 'Date of Comment' '{date_of_comment_excel}' for row {index}. Using current aware time.")
                        date_of_comment = timezone.now()
            else:
                date_of_comment = timezone.now()

            VesselComment.objects.create(
                comment_title=get_safe_value(row, 'Comment Title', default_value='', data_type='str'),
                comment_details=get_safe_value(row, 'Comment Details', default_value='', data_type='str'),
                date_of_comment=date_of_comment,
                comment_by=get_safe_value(row, 'Comment By', default_value='', data_type='str'), # Use '' for text fields
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
    excel_file_name = "VOPS.xlsx"
    import_data_from_excel(excel_file_name)