# Gmail Administration Bot

This Python script acts as a bot designed to help manage your Gmail account automatically. It utilizes the Gmail API and OpenAI's GPT-3.5 model for email classification, response generation, and organization.

## Overview

The script offers two distinct modes:

1. **Automatic Email Management:**
    - Classifies incoming emails into categories such as Work, Personal, Urgent, or Not Relevant.
    - Generates responses or summaries based on email content and classification.
    - Block email address if it has send more than five irrelkevant emails

2. **Email Retrieval by Date Range:**
    - Retrieves emails from a specific date range or from a particular sender.
  
## Setup and Usage

### Prerequisites

- Python 3.x
- Dependencies: `evadb`, `openai`, `imaplib`, `smptlib`
- Gmail account credentials
- OpenAI API key

### Configuration

1. Install necessary dependencies: `evadb`, `openai`, etc.
2. Set up your Gmail account and ensure the necessary permissions.
3. Set the OpenAI API key in the script.
4. Modify the username, password, and status variables in the script (for demo purposes only).

### Usage

1. Run the script and choose the mode (1 or 2) based on your requirements.
2. For Mode 1: The script automatically manages and categorizes incoming emails.
3. For Mode 2: Input the date range and, optionally, the sender's email to retrieve relevant emails.

### Note

- The script uses the OpenAI GPT-3.5 model for email classification and response generation.
- Ensure proper error handling and exception management for a seamless user experience.

## License

This project is licensed under [MIT License](LICENSE).
