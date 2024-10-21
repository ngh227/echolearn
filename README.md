# Echolearn Project: 
Learn it. Explain it. Master it!

This project aims to help students deeply understand material by encouraging them to explain it in their own words. It includes both a backend built with Python and a frontend built with React.

Survey:

<img width="759" alt="Screenshot 2024-10-20 at 1 21 23 PM" src="https://github.com/user-attachments/assets/865d3200-338e-4105-b523-aac238c582ba">

- Find out more here: https://docs.google.com/presentation/d/1I_zl_7M6E_cbLyrWe55y9e2yRw9Wq3tM9C_itqg0ZAE/edit#slide=id.g30cc4a8b9eb_0_0



## Click to see demo


[![Watch the Demo on YouTube](https://img.youtube.com/vi/JCcmNNLoctY/0.jpg)](https://youtu.be/JCcmNNLoctY)



## Table of Contents

- [Prerequisites](#prerequisites)
- [Back-End Setup](#back-end-setup)
- [Front-End Setup](#front-end-setup)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Front-End Available Scripts](#front-end-available-scripts)
- [Learn More](#learn-more)

## Prerequisites

For this solution, you need the following prerequisites:

- **Python 3.9 or later**
  *Note*: It is recommended that you use a [virtual environment](https://docs.python.org/3.9/library/venv.html) or [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to isolate the solution from the rest of your Python environment.
- An [IAM](https://aws.amazon.com/iam/) user with enough permissions to use [Amazon Bedrock](https://aws.amazon.com/bedrock/), [Amazon Transcribe](https://aws.amazon.com/pm/transcribe), and [Amazon Polly](https://aws.amazon.com/polly/).
  *Note*: Please ensure that the underlying Foundational Model in Amazon Bedrock, that you plan to use, is enabled in your AWS Account. To enable access, please see [Model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).
- MongoDB Atlas account for vector database
- Jina API setup (if required by your project)

## Back-End Setup

1. **Clone the Repository**: 
   Ensure you have the project's repository cloned locally.

2. **Set Up Environment Variables**: 
   Create a `.env` file in the root directory of the project. Use the `env.example` file as a template and fill in the necessary information. The `.env` file should contain:

   ```
   MONGODB_CONNECTION_STRING=your_mongo_connection_string
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   S3_BUCKET_NAME=your_bucket_name
   MODEL_ID=your_model_id  # Optional
   ```

3. **Install Dependencies**: 
   Navigate to the backend directory and run the following command:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Backend App**:
   To start the backend, use the following command:
   ```bash
   python backend/app/services/main.py
   ```
## Front-End Setup

1. **Navigate to the Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Frontend Dependencies**:
   ```bash
   npm install
   ```

3. **Run the Frontend App**:
   ```bash
   npm start
   ```
   This will start your React app in development mode. You can open http://localhost:3000 to view it in your browser.

## Installation

To install Python libraries required for the project, run the following command:
```bash
python install -r ./requirements.txt
```

## Running the App

### Setting AWS Credentials

Before running the app, set your AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=<...>
export AWS_SECRET_ACCESS_KEY=<...>
export AWS_DEFAULT_REGION=<...> # Optional, defaults to us-east-1
```

You can optionally set the Foundational Model (FM) to be used:
```bash
export MODEL_ID=<...>
```

### Sign Up for Required Accounts

1. **AWS Account**: Sign up for an AWS account to access services like Amazon Bedrock, Transcribe, and S3.
2. **MongoDB Atlas**: Sign up for MongoDB Atlas as your vector database.
3. **Jina API**: Ensure that Jina API is set up if your project requires it.

## Front-End Available Scripts

The following commands can be run within the frontend directory:

- `npm start`: Runs the app in development mode. Open http://localhost:3000 to view it in your browser.
- `npm test`: Launches the test runner in the interactive watch mode.
- `npm run build`: Builds the app for production in the build folder.
- `npm run eject`: Ejects the configuration files to give full control.

## References

- [Python Documentation](https://docs.python.org/)
- [React Documentation](https://reactjs.org/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Transcribe Documentation](https://docs.aws.amazon.com/transcribe/)
- [Amazon Polly Documentation](https://docs.aws.amazon.com/polly/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Jina AI Documentation](https://docs.jina.ai/)


