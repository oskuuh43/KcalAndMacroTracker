import pandas as pd

def load_food_data():
    # Path to the Excel file
    file_path = 'app/data/resultset.xlsx'
    # Load the data into a DataFrame
    df = pd.read_excel(file_path, engine='openpyxl')

    # Convert kilojoules to calories
    df['Calories'] = df['energia, laskennallinen (kJ)'] * 0.239006

    # Select needed columns and rename for consistency
    df = df[['name', 'Calories', 'proteiini (g)']]
    df.columns = ['Name', 'Calories', 'Protein']

    # Convert 'Calories' and 'Protein' to numeric
    df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce')
    df['Protein'] = pd.to_numeric(df['Protein'], errors='coerce')

    return df

def get_high_protein_options(df, min_protein_ratio=0.1):
    """
    Find food items with a high protein-to-calorie ratio.

    :param df: DataFrame containing the food data.
    :param min_protein_ratio: Minimum ratio of protein to calories to consider.
    :return: List of dictionaries of food items meeting the criteria.
    """
    # Ensure that 'Protein' and 'Calories' columns exist
    if 'Protein' not in df.columns or 'Calories' not in df.columns:
        raise ValueError("DataFrame must contain 'Protein' and 'Calories' columns.")

    df = df.dropna(subset=['Protein', 'Calories'])

    # Calculate protein-to-calorie ratio
    df['Protein_to_Calories'] = df['Protein'] / df['Calories']

    # Filter for high protein-to-calorie ratio
    high_protein_df = df[df['Protein_to_Calories'] >= min_protein_ratio].copy()

    # Round the 'Calories', 'Protein', and 'Protein_to_Calories' columns to two decimals
    high_protein_df['Calories'] = high_protein_df['Calories'].round(2)
    high_protein_df['Protein'] = high_protein_df['Protein'].round(2)
    high_protein_df['Protein_to_Calories'] = high_protein_df['Protein_to_Calories'].round(2)

    return high_protein_df[['Name', 'Calories', 'Protein', 'Protein_to_Calories']].to_dict(orient='records')
