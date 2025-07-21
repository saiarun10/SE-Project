# GrowUp Richie

## Introduction
GrowUp Richie is a single-page application (SPA) designed to teach financial literacy to children aged 8-14. It provides interactive lessons, quizzes, expense tracking, three calculators (Simple, Simple Interest Rate, Compound Interest Rate), an AI-driven chatbot, and an awareness section to educate users about financial risks and strategies. With admin and user roles, the platform ensures a secure, scalable, and engaging experience. 

## Features

### Flagship Features
- **Chatbot**
  - **AI-Driven Interaction**: Provides tailored financial advice for children through dedicated components.
  - **Session History**: Stores and retrieves conversation history in the `ChatbotMessages` table, linked to `UserSessions`.
  - **Usage Statistics**: Premium users access chatbot interaction analytics, visualized with Chart.js.
- **Premium Features**
  - **Unlimited Chatbot Access**: Premium users enjoy unrestricted chatbot interactions.
  - **Advanced Analytics**: Offers detailed reports on quiz performance, expense patterns, and learning progress.
  - **Passcode-Protected Expense Tracking**: Premium users secure their expense tracker with a passcode, managed via the `UserProfile` table.
  - **Stripe Integration**: Processes secure payments for premium membership via Stripe.
- **Analytics**
  - **User Engagement**: Tracks quiz attempts, lesson progress, and chatbot interactions in `QuizAttempts`, `UserModuleProgress`, and `ChatbotMessages` tables.
  - **Expense Visualizations**: Displays spending patterns using Chart.js, based on `Transactions` data.
  - **Admin Insights**: Admins access aggregated analytics (e.g., user growth, premium subscriptions) in the admin dashboard.
  - **CSV Reports**: Users and admins can export analytics as CSV files.
- **Parental Controls**
  - **Parent Verification**: Parents set an email and password in the `UserProfile` table to monitor activity.
  - **Access Restrictions**: Parents can limit access to premium features or sensitive data.
  - **Age Validation**: Ensures users are aged 8-14 years using the `birth_date` field in `UserProfile`.
- **Calculators**
  - **Simple Calculator**: Supports basic arithmetic for learning financial calculations.
  - **Simple Interest Rate Calculator**: Teaches interest calculation concepts.
  - **Compound Interest Rate Calculator**: Introduces advanced interest concepts for young learners.
- **Awareness Section**
  - **Financial Education Content**: Displays articles on financial risks and strategies (e.g., trading losses, investment alternatives) with sources, dates, and key insights.
  - **Interactive Navigation**: Allows users to browse articles with previous/next buttons and a progress counter.
  - **Responsive Design**: Ensures accessibility across devices with animated transitions for content changes.

### Additional Features
- **Interactive Learning**: Lessons, modules, and topics cover financial literacy (e.g., Money Management, Financial Planning) with PDF content support.
- **Quizzes**: Tests knowledge with progress tracking and question management.
- **Expense Tracking**: Allows users to log and categorize expenses, with visualizations for premium users.
- **PDF Content**: Supports upload and download of topic PDFs for learning materials.
- **Swagger Documentation**: Enables interactive API testing as YAML file at [swagger documentation.yaml](supplementary_files/swagger%20documentation.yaml).
- **Input Validation**: Enforces data integrity on frontend (Vue.js) and backend (Flask).
- **API Testing**: Pytest in `backend/tests` ensures robust API functionality.

## Technology Stack
- **Backend**: Flask (RESTful API framework), SQLite (data storage with SQLAlchemy ORM), pytest (API testing).
- **Frontend**: Vue.js 3 with CLI (dynamic SPA), Axios (API communication), Bootstrap (responsive design).
- **Authentication**: JWT (JSON Web Tokens) for secure role-based access.
- **API Documentation**: Swagger (interactive API documentation as YAML file at [swagger documentation.yaml](supplementary_files/swagger%20documentation.yaml)).
- **Payment Processing**: Stripe (secure premium membership transactions).
- **Visualization**: Chart.js (expense, quiz, and chatbot analytics visualizations).
- **Templating**: Limited to initial page loads in Flask.

## System Architecture
- **Backend**: Flask powers RESTful APIs for authentication, content management, quizzes, expense tracking, calculators, chatbot interactions, and awareness content. SQLite, managed via SQLAlchemy, stores data, with pytest ensuring API reliability in the `backend/tests` folder. Swagger provides interactive API documentation.
- **Frontend**: Vue.js 3 drives a dynamic SPA, rendering components for dashboards, chatbot, calculators, and awareness articles using Axios for API calls. Bootstrap ensures responsive layouts with styled components for article navigation.
- **Authentication**: JWT tokens secure endpoints, distinguishing admin and user roles, with parental controls for child safety.
- **Request-Response**: Axios handles HTTP requests (e.g., fetching lessons, submitting expenses, retrieving awareness articles) and processes JSON responses from Flask APIs.

## Roles and Functionalities

### Admin
- **Access**: Logs in with superuser credentials, redirects to the admin dashboard.
- **Functionalities**:
  - **Content Management**: Creates, updates, and deletes lessons, modules, topics, quizzes, questions, stories, and awareness articles.
  - **Dashboard**: Displays real-time statistics (e.g., user count, quiz completions, premium memberships, chatbot usage) with Chart.js visualizations.
  - **Reports**: Exports CSV reports for user engagement, financial summaries, and awareness interaction analytics.
  - **Content Upload**: Manages PDF content for topics and articles, enabling upload and download.
  - **Testing**: Validates backend APIs using pytest in the `backend/tests` folder.

### User (Child Aged 8-12)
- **Access**: Registers and logs in, accessing features through the user dashboard.
- **Functionalities**:
  - **Learning**: Explores lessons, modules, and topics (e.g., Stock Market, Budgeting).
  - **Quizzes**: Takes quizzes to test knowledge, with results displayed.
  - **Expense Tracking**: Logs expenses, categorizes transactions, and views Chart.js visualizations.
  - **Chatbot**: Interacts with an AI-driven chatbot for financial guidance, with history accessible for review.
  - **Premium Features**: Unlocks advanced analytics, unlimited chatbot access, and passcode-protected expense tracking via Stripe payments.
  - **Parental Controls**: Parents monitor activity via email and password verification.
  - **Calculators**: Uses three calculators (Simple, Simple Interest Rate, Compound Interest Rate) to explore financial concepts.
  - **Awareness Section**: Reads articles on financial risks and strategies, navigating through interactive controls with key insights highlighted.

## Database Schema (SQLite)
- **Users**: Stores profiles (email, username, user_role) and links to relationships (`profile`, `sessions`, `topic_progress`, `quiz_attempts`, `transactions`, `chatbot_messages`, `story_interactions`).
- **UserProfiles**: Manages user details (full_name, birth_date, parent_email, parent_password_hash, is_premium_user, premium_passcode) with age validation (8-100 years).
- **UserSessions**: Tracks active sessions (session_token, login_at, is_active) and links to chatbot messages.
- **ChatbotMessages**: Logs chatbot interactions (message_content, message_type) per session.
- **Transactions**: Records expenses/income (amount, category, transaction_date) for analytics.
- **Lessons**: Contains financial literacy topics (e.g., lesson_name, lesson_description).
- **Modules**: Organizes lessons into sections (module_title, module_description) with soft delete (deleted_at).
- **Topics**: Stores content (topic_title, topic_content as LargeBinary for PDFs) with soft delete.
- **UserModuleProgress**: Tracks user progress (progress_percentage, started_at, completed_at) with constraints.
- **Quizzes**: Saves quiz details (quiz_title, duration_minutes, is_visible) with soft delete.
- **Questions**: Stores quiz questions (question_text, options, correct_answer) with soft delete.
- **QuizAttempts**: Tracks quiz attempts (total_score_possible, score_earned, time_taken_seconds).
- **QuestionAttempts**: Records answers (selected_answer, is_correct) per attempt.
- **Stories**: Stores interactive stories (story_title, story_content, story_type) with soft delete.
- **StoryInteractions**: Tracks user engagement (viewed_at, is_liked) with unique constraints.

## Setup Instructions
For detailed instructions on setting up the project, including installation and configuration steps, refer to the [Project Setup Guide.md](documentation/Project%20Setup%20Guide.md) in the [documentation](documentation) folder.



## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, collaborations, or further details, please reach out:
- **Name:** Shib Kumar Saraf
- **LinkedIn:** [Shib Kumar Saraf][https://www.linkedin.com/in/shibkumarsaraf/]
- **Email:** [shibkumarsaraf05@gmail.com](mailto:shibkumarsaraf05@gmail.com)  
- **GitHub:** [@shib1111111](https://github.com/shib1111111)

  
## Conclusion
GrowUp Richie aims to empower children with essential financial knowledge through engaging and interactive learning experiences. The platform's features, from quizzes to chatbot interactions, are designed to make financial literacy accessible and enjoyable for young learners.

