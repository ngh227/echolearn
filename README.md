# Echolearn Project

This project aims to help students deeply understand material by encouraging them to explain it in their own words. It includes both a backend built with Python and a frontend built with React.

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
  _Note_: It is recommended that you use a [virtual environment](https://docs.python.org/3.9/library/venv.html) or [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to isolate the solution from the rest of your Python environment.
- An [IAM](https://aws.amazon.com/iam/) user with enough permissions to use [Amazon Bedrock](https://aws.amazon.com/bedrock/), [Amazon Transcribe](https://aws.amazon.com/pm/transcribe), and [Amazon Polly](https://aws.amazon.com/polly/).  
  _Note_: Please ensure that the underlying Foundational Model in Amazon Bedrock, that you plan to use, is enabled in your AWS Account. To enable access, please see [Model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).

## Back-End Setup

1. **Clone the Repository**: Ensure you have the project's repository cloned locally.

2. **Set Up Environment Variables**: Create a .env file contains information in env.example


