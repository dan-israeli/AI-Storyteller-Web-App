# AI Storyteller Web App :robot: :book:

## Overview 

This project is an AI-powered storytelling web app, developed using Flask, designed to create personalized and interactive stories for children. It features built-in narration, a library for managing and sharing favorite stories, and secure user authentication, ensuring an engaging and user-friendly experience.

In building this application, I integrated APIs such as OpenAI for story generation and ElevenLabs for natural-sounding narration. The project also incorporates a SQLite3 database for efficient data storage and retrieval. These technical elements allowed me to explore key aspects of backend development, API integration, and database management.

This project demonstrates my ability to design and develop practical applications that merge creativity with technology. In addition, it showcases my skills in designing a system with multiple interconnected components and integrating them seamlessly to work together as a smooth application.

---

## Key Features  

### **Story Creation**
During the story creation phase, users can choose the story's location, genre, and hero name, adding a personal touch to their narratives. The app integrates the OpenAI API to generate personalized and interactive stories based on the provided input. Each story is unique (even when the the same settings are selected) ensuring a fresh and new experience every time. This feature tailors the story to the user's preferences while maintaining the element of surprise and variety. The interactive element further enhance user engagement, making the story both dynamic and more immersive.

### **Built-in Narration**  
To enhance the storytelling experience, the app uses the ElevenLabs API to provide natural-sounding, AI-powered narration. This feature allows users to listen to their stories being read aloud, bringing them to life in a new dimension.

### **Regeneration Button**  
The app includes a **Regeneration Button** feature, allowing users to rewrite a specific section of a story they are not satisfied with. This functionality gives users the flexibility to modify sections without starting over, ensuring the story aligns with their preferences. It enhances creativity and control during the storytelling process, making the experience more dynamic and user-friendly.


### **Customizable Settings**  
The app offers a range of settings to further tailor the storytelling experience to user preferences, including:  
- **Narration Voice Selection**: Choose from various narration voices to find the perfect tone for your story.  
- **Story Sections**: Decide the number of sections your story will have, allowing to customize its length and structure.  
- **Narration**: Enable or disable the built-in narration for your story.  
- **Voice Guidance**: Enable or disable voice guidance during the story creation phase. Designed with young users in mind, this feature allows children, who may not yet know how to read, to independently create their own stories.

### **Library for Managing and Sharing Stories**  
The app offers a dedicated library, where users can:
- Save a newly created story.
- Manage story collection (e.g. view, delete).
- Share favoriate stories via email directly from the app.

### **Database**  
The app relies on a lightweight yet powerful SQLite3 database to store essintial information such as user data, stories, and more. This ensures fast and reliable access to data while keeping the project easy to deploy and maintain.

### **User Authentication**  
Security is always a crucial aspect, and the app implements user authentication using SHA-256 encryption. This ensures that user credentials are securely stored, providing a safe and reliable environment for all users.

---

## Running Instructions

Follow these steps to set up and run the AI Storyteller Web App:

---

### 1. **Download the Files**
- Download all files from the `code` directory.
- Ensure all files downloaded are located in the `code` directory on your local machine.

---

### 2. **Set Up the Database**
1. Create a new SQLite database named `database.db`. in the `code` directory.
2. Run the `db_tables.py` file to create the necessary database tables.

---

### 3. **Set Up Email Credentials**
1. Create a text file named `email.txt` in the `code/static` directory.
2. Add the email and password of the account you want to use (each in a new line).

---

### 4. **Set Up API Keys**
1. Create a directory named `api_keys` inside the `code/static` directory.
2. Inside the `api_keys` directory, create the following text files:
   - `ElevenLabs.txt`
   - `OpenAI.txt`
3. Add the corresponding API key to each file:
   - Get an OpenAI API key: https://openai.com/blog/openai-api
   - Get an ElevenLabs API key: (free) https://elevenlabs.io/api

---

After completing these steps, the application is ready to be executed!
