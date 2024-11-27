import ollama
import pandas as pd

# Load CSV file
filename = input("Enter csv filename: ")
data = pd.read_csv(filename)

# Assuming there's a column called 'text' that contains the data to be cleaned
def clean_data(ingredients):
    try:
        # Use Ollama to process and clean the text
        response = ollama.chat(model="llama2", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Clean this data by removing phrases and words that do not belong in the ingredient list: {ingredients}"}
        ])
        cleaned_ingredients = response.get('response', '')  # Adjust this as per your response structure
        return cleaned_ingredients
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return ingredients  # Return original text if something goes wrong

# Apply the cleaning function to the 'text' column
data['cleaned'] = data['ingredients'].apply(clean_data)

# Display the cleaned data
print(data[['ingredients', 'cleaned']].head())

# Optionally, save the cleaned data back to a new CSV
data.to_csv('clean_{filename}', index=False)
