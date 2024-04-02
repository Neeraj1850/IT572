# Energy Calculator

## Introduction
The Energy Calculator is an innovative tool designed to predict the energy consumption of household appliances simply by analyzing their pictures. Utilizing advanced image recognition and energy consumption data, this application offers users insights into their appliances' efficiency, encouraging energy conservation and helping in making informed decisions about their usage.

## Environment Setup
To run the project, you need to set up the environment variables. Create a `.env` file in the root directory and populate it with the following values:

DATABASE_USER='your-database'
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT='port-no'
DATABASE_NAME='database-name'
TESSERACT_CMD='path-to-tesseract'
MODEL_PATH='path-to-model'
CORS_ORIGIN='cors-url'
UNIT_COST_PER_KWH='as-per-province'

## Data Sources
The application leverages two main data sources for energy consumption:
- **Average Energy Consumption by Appliances**: [Dataset Link](https://open.canada.ca/data/dataset/4aa13365-c077-46dd-a62b-166ffc651e6f/resource/05ab565f-fec1-469f-95ae-40ddf5032f91)
- **Individual Appliance Energy Consumption with Model Numbers and Brand**: [Dataset Link](https://open.canada.ca/data/dataset/fbfdf946-8dd1-4830-a5c9-f8a72d8fabda)

## Project Structure
- `IT572.ipynb`: Notebook used for training the model on appliance images.
- `server.py`: Python server file to handle backend requests.
- `/frontend`: Directory containing the React application for the frontend interface.
- Additional files and directories should be documented similarly, providing a brief description of their purpose and functionality.

## Database Setup
Before running the application, set up your database by creating tables for each appliance, including fields for name, brand name, and average energy consumed. Additionally, create a table to hold the average energy consumption data for all appliances.

## Training the Model
Use the `IT572.ipynb` notebook to train your model. Ensure you have collected the necessary appliance images and have set the correct path in the notebook according to the `MODEL_PATH` variable in your `.env` file.

## Running the Application
Install the dependencies (if you haven't already): npm install

To start the backend server:
1. Navigate to the server directory: cd ./backend
2. Run the server with: python server.py

To start the frontend application:
3. Start the application: npm start
