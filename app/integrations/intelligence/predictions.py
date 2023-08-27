import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import pickle
import os
from pathlib import Path

current_dir = Path(__file__).parent

# Load the pre-trained model and tokenizer
def load_model_and_tokenizer(model_path, tokenizer_path):
    model = tf.keras.models.load_model(model_path)
    with open(tokenizer_path, 'rb') as tokenizer_file:
        tokenizer = pickle.load(tokenizer_file)
    return model, tokenizer

# Function to extract information from text
def extract_info_from_text(text):
    ticket_pattern = r'\b[A-Za-z]+-[A-Za-z0-9]+\b'
    name_pattern = r'\bto\s+([A-Za-z][A-Za-z\s]+)\b'

    extracted_tickets = re.findall(ticket_pattern, text, re.IGNORECASE)
    ticketNumber = extracted_tickets[0] if extracted_tickets else ""

    match = re.search(name_pattern, text, re.IGNORECASE)
    userName = match.group(1).title() if match else ""

    return {"Assignee": userName, "TicketNo": ticketNumber}

# Function to make predictions using the loaded model and tokenizer
def make_predictions(model, tokenizer, max_sequence_length, test_data):
    test_sequences = tokenizer.texts_to_sequences(test_data)
    padded_test_sequences = pad_sequences(test_sequences, maxlen=max_sequence_length, padding='post')
    predictions = model.predict(padded_test_sequences)

    result = []
    for i, prediction in enumerate(predictions):
        if prediction >= 0.5:
            label = "Update Ticket"
        else:
            label = "Create Ticket"
        
        userName, ticketNumber = extract_info_from_text(test_data[i])
        info_dict = extract_info_from_text(test_data[i])
        info_dict["Text"] = test_data[i]
        info_dict["Task"] = label
        result.append(info_dict)
    
    return result

# Paths for the saved model and tokenizer
model_path = str(current_dir) + '/ticket_prediction_model.h5'
tokenizer_path = str(current_dir) + '/tokenizer.pkl'



# Load the model and tokenizer
loaded_model, loaded_tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)



###### below code is the example for how to use this model

# # Define the test dataset
# test_data = [
#     "Create a new ticket for the server maintenance scheduled for this weekend.",
#     "Update ticket IT-7823 with the latest information and assign it to Sarah Wilson.",
#     # ... (other test data)
# ]

# # Maximum sequence length
max_sequence_length = loaded_model.layers[0].input_length

# # Make predictions
def generate_results(user_input):
    predictions = make_predictions(loaded_model, loaded_tokenizer, max_sequence_length, user_input)
    return predictions
# # Print predictions
# for prediction in predictions:
#     print(prediction)
#     print()
