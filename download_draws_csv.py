import pandas as pd
import glob

FOR_MAX = True
ALLOWED_NUMBER_OF_FILES = 2 if FOR_MAX else 1

day_column_map = {
    0: "Sun_Draw",
    1: "Mon_Draw",
    2: "Tues_Draw",
    3: "Wed_Draw",
    4: "Thur_Draw",
    5: "Fri_Draw",
    6: "Sat_Draw",
}

try:
    # Load the first spreadsheet (person and routes)
    person_routes_df = pd.read_excel('Carrier_Map.xlsx')
    person_routes_df = person_routes_df.where(pd.notna(person_routes_df), None)

    # Load the process IDs
    file_pattern = 'ProcessID*.csv'
    matching_files = glob.glob(file_pattern)

    if len(matching_files) == 0 or len(matching_files) > ALLOWED_NUMBER_OF_FILES:
        raise Exception("More than one Process ID file")

    dataframes = []
    for file_path in matching_files:
        process_id_df = pd.read_csv(file_path)
        dataframes.append(process_id_df)

    process_id_df = pd.concat(dataframes, ignore_index=True)

    print("0 - SUNDAY")
    print("1 - MONDAY")
    print("2 - TUESDAY")
    print("3 - WEDNESDAY")
    print("4 - THURSDAY")
    print("5 - FRIDAY")
    print("6 - SATURDAY")
    day = input("WHAT DAY DO YOU WANT DRAWS FOR?\n")

    try:
        day = int(day)
        if day not in range (0, 7):
            raise ValueError("Invalid day number provided. Exiting.")
    except Exception:
        raise ValueError("Invalid day number provided. Exiting.")

    # Sum up route totals and get values for the selected day
    process_id_df = process_id_df.groupby(['Route', 'Product'])[list(day_column_map.values())].sum().reset_index()
    process_id_df = process_id_df[['Route', 'Product', day_column_map[day]]]
    process_id_df = process_id_df.rename(columns={day_column_map[day]: 'Values'})
    process_id_df = process_id_df.pivot(index='Route', columns='Product', values='Values')
    process_id_df = process_id_df.fillna(0)

    # Convert column to integers
    for column in process_id_df.columns:
        process_id_df[column] = process_id_df[column].astype(int)

    # Drop columns that are entirely zero - that is no product for today
    process_id_df = process_id_df.loc[:, (process_id_df != 0).any(axis=0)]

    # Reshape carrier dataframe to join with process ID DF
    person_routes_df = pd.melt(person_routes_df, id_vars=['CARRIER'], value_name='Route')
    person_routes_df = person_routes_df.dropna(subset=['Route'])

    # Join the two dataframes
    merged_df = process_id_df.merge(person_routes_df, on='Route')

    # Collapse on carrier
    merged_df = merged_df.groupby(['CARRIER']).sum(numeric_only=True).reset_index()

    # Export to a CSV
    merged_df.to_csv(f"{day_column_map[day]}s.csv", index=False)
    print(f"Successfully exported {day_column_map[day]}")

except Exception:
    print("Something went wrong. Please fix and try again.")
