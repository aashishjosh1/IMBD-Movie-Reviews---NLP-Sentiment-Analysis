# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:17:00 2024

@author: aashi
"""
import io
import pickle
from flask import Flask, request, send_file
from flasgger import Swagger
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pandas as pd

#Downloading the necessary NLTK resources
nltk.download('punkt_tab')
nltk.download('stopwords')

#Load the trained Tf-Idf Logistic Regression model using pickle
with open(r'../sentiment_analysis_text_classification/model_artifacts/lr2.pkl', 'rb') as model_pkl:
    model = pickle.load(model_pkl)

#Load the saved Tf-Idf object using pickle
with open(r'../sentiment_analysis_text_classification/model_artifacts/tfidf.pkl', 'rb') as tfidf_pkl:
    tfidf = pickle.load(tfidf_pkl)


app = Flask(__name__)
swagger = Swagger(app)


# Define a function to clean the data using natural language processing
def clean_reviews(dataset):
    clean_data = []
    ps = PorterStemmer()  # Initialize PorterStemmer once
    stop_words = set(stopwords.words('english'))  # Initialize stop words once
    
    for review in dataset['review']:
        # Remove non-letter characters
        review = re.sub('[^a-zA-Z]', ' ', review)
        # Convert to lowercase
        review = review.lower()
        # Tokenize the review
        review = word_tokenize(review)
        # Stem and remove stop words
        review = [ps.stem(word) for word in review if word not in stop_words]
        # Join back into a string
        clean_data.append(' '.join(review))
    
    return clean_data

# Define the API endpoint to handle file upload
@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the prediction endpoint.
    It takes a CSV file as input and returns predictions.
    ---
    parameters:
      - name: input_file
        in: formData
        type: file
        required: true
        description: The CSV file containing the input data.
    responses:
      200:
        description: Sentiment analysis of movie reviews (1=Postive review, 0=Negative review)
    """
    #reading the input file
    input_data = pd.read_csv(request.files.get("input_file"))
    
    #retaining the original input data
    original_input_data = input_data.copy()
    
    #applying natural language processing to obtain cleaned reviews
    input_data['cleaned_review'] = clean_reviews(input_data)
    
    #transforming the cleaned reviews with the saved tfidf object
    input_data = tfidf.transform(input_data['cleaned_review'])
    
    #performing predictions using the pre-trained model
    predictions = model.predict(input_data)
    
    #appending predictions to the original input data
    original_input_data['Predictions'] = predictions
    
    #creating an in-memory CSV file with both input data and predictions
    output = io.BytesIO()
    original_input_data.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    #sending the CSV file as a response
    return send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename='predictions_output.csv')
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug=True)