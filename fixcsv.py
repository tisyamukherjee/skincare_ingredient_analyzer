import pandas as pd

# Load the CSV file
file_path = "oldpaula.csv"  # Replace with the path to your file
output_file_path = "paula.csv"  # Specify the output file path

# Read the CSV file
df = pd.read_csv(file_path)

# Convert the column containing lists to plain text
# Replace 'ingredients' with the name of the column containing the lists
df['ingredients'] = df['ingredients'].apply(lambda x: ', '.join(eval(x)) if isinstance(x, str) else x)

# Save the modified DataFrame to a new CSV
df.to_csv(output_file_path, index=False)

print(f"Converted CSV saved to {output_file_path}")
