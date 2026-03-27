# Functional Specification: FitLife Backend Application

**Created**: 2026-01-21

## User Journeys & Acceptance Scenarios

### 1. User Registration and Authentication (Priority: P1)
A new user needs to join the FitLife ecosystem to access personalized fitness services. They provide their credentials and profile basics; the system establishes their account and manages secure, persistent sessions using industry-standard tokens.

* **Strategic Value**: This is the gateway to the entire platform. Without identity management, personalization and progress tracking are impossible.
* **Acceptance Scenarios**:
    * **Successful Registration**: When a user provides a valid email and password, the system creates the account and initializes a secure session.
    * **Secure Login**: When an existing user provides correct credentials, the system validates the identity and grants access to protected resources.
    * **Session Continuity**: The system allows a user with an active (but expired) short-term session to renew access using a long-term refresh mechanism without re-entering credentials.
    * **Conflict Handling**: If a user attempts to register with an email already present in the system, the process is rejected with a clear conflict notification.

---

### 2. Initial Physical Assessment (Priority: P1)
A newly registered user completes a progressive physical evaluation covering fitness levels, functional capacity, habits, and health alerts. The system calculates a Fitness Score (0-100) and an estimated "Body Age".

* **Strategic Value**: This provides the "challenging diagnosis" that drives user engagement and baseline personalization.
* **Acceptance Scenarios**:
    * **Assessment Completion**: Upon receiving all required evaluation responses, the system calculates and returns a Fitness Score, Body Age, and a category (Excellent, Good, Fair, or Poor).
    * **Body Age Comparison**: The system identifies if a user's "Body Age" is older, younger, or equal to their chronological age based on health indicators.
    * **Longitudinal View**: The system provides a chronological history of all past assessments to visualize health trends over time.

---

### 3. Instructor Selection and Assignment (Priority: P1)
Users browse available professionals, viewing certifications and ratings, to select a guide for their journey. The system manages the formal link between the professional and the client.

* **Strategic Value**: The instructor-user relationship is the core business model.
* **Acceptance Scenarios**:
    * **Professional Directory**: Users can browse all instructors, viewing names, certifications, average ratings, and current client load.
    * **Formal Assignment**: The system establishes a dedicated link between a user and an instructor, marking it as the primary active relationship.
    * **Instructor Migration**: When a user switches instructors, the system terminates the previous active relationship (archiving it for history) and activates the new one.
    * **Feedback Loop**: Users can rate their active instructor, which the system uses to dynamically update the professional’s global average.

---

### 4. Physical Progress Tracking (Priority: P2)
Users regularly log metrics (weight, body fat %, measurements) to track their transformation. The system derives secondary metrics like BMI and stores historical data.

* **Acceptance Scenarios**:
    * **Metric Logging**: The system accepts and timestamps weight, height, body fat, and circumferences (waist/hip).
    * **Historical Analysis**: Users can retrieve a full timeline of their physical data, ordered by date.
    * **Derived Calculations**: Upon logging weight and height, the system calculates the BMI for display purposes but does not store the static result.

---

### 5. Training Routine Management (Priority: P2)
Instructors design personalized routines. Users receive these plans, execute them, and log completions including perceived exertion.

* **Acceptance Scenarios**:
    * **Routine Deployment**: Once assigned, the system makes the routine the "Active Plan" for the user.
    * **Execution Logging**: Users mark specific sessions as complete, providing feedback on difficulty (RPE 1-10) and qualitative notes.
    * **Educational Guidance**: For every exercise, the system provides descriptions, muscle groups targeted, and instructional video links.

---

### 6. Nutrition Plan Management (Priority: P2)
Instructors provide weekly meal suggestions (breakfast, lunch, dinner, snacks). Users follow these guidelines within the app.

* **Acceptance Scenarios**:
    * **Weekly Planning**: Instructors generate plans organized by ISO weeks, detailing daily meal suggestions and general hydration or supplement notes.
    * **Plan Access**: Users view their current weekly nutrition guide.

---

### 7. Messaging and Communication (Priority: P3)
A channel for asynchronous communication regarding routine adjustments or motivation.

* **Acceptance Scenarios**:
    * **Direct Messaging**: Instructors can send text updates to their assigned clients.
    * **Automated Notifications**: The system automatically generates a message/notification whenever a new routine or nutrition plan is assigned.

---

### 8. Training Reminders (Priority: P3)
Automated prompts to ensure adherence to training, logging, or check-ins via push notifications.

* **Acceptance Scenarios**:
    * **Scheduled Prompts**: Users set specific times for "Training" or "Physical Logging" reminders.
    * **Push Delivery**: The system triggers external notifications at the scheduled time, accounting for the user's local time zone.

---

### 9. Password Recovery and Security Management (Priority: P1)
A critical security layer allowing users to regain account access or update credentials.

* **Acceptance Scenarios**:
    * **Reset Request**: If a user forgets their password, the system generates a unique, time-limited (1-hour) secure token and delivers it via email.
    * **Secure Update**: Using a valid token, a user can set a new password. The system then invalidates the token and all existing sessions.
    * **Re-use Prevention**: The system prevents the use of any of the last 5 passwords used by that account.

---

### 10. User Profile Customization (Priority: P2)
Management of personal data, fitness goals, and preferences.

* **Acceptance Scenarios**:
    * **Profile Visibility**: Users can view their full data set (name, age, height, activity level, goals).
    * **Email Verification**: If a user changes their email, the system marks the new address as "pending" and requires verification before the change becomes final.
    * **Audit Logging**: Every change to a profile is logged, showing the modified field, the old value, the new value, and the timestamp.

---

## System Requirements & Business Logic

### Identity & Access Logic
* **Security**: All passwords must be hashed using industry-standard algorithms (e.g., bcrypt).
* **Session Management**: Use a dual-token system (short-term access/long-term refresh). Refresh tokens must be stored in a high-speed volatile store for instant revocation.
* **Role-Based Access (RBAC)**: Distinguish between `USER`, `INSTRUCTOR`, and `ADMIN`.
* **Password Complexity**: Minimum 8 characters, including uppercase, lowercase, numbers, and special characters.

### Assessment & Calculation Logic
* **Fitness Score**: A weighted calculation (0-100) across Physical, Functional, Habits, and Alert categories.
* **Body Age Formula**: Calculated as $RealAge + BMI_{adj} + BodyFat_{adj} + Functional_{adj} + Habits_{adj}$.
* **BMI Logic**: Purely functional; calculated as: $weight / (height/100)^2$.

### Data Integrity & Performance
* **Validation**: All incoming data must be validated against strict schemas (e.g., Age: 13-120; Height: 100-250cm).
* **Concurrency**: Implement optimistic locking to prevent data loss during simultaneous profile updates.
* **Caching**: High-frequency data (instructor lists, exercise libraries) must be cached to ensure sub-second response times.

---

## Success Metrics

| Metric | Target |
| :--- | :--- |
| **Registration Flow** | < 60 seconds with 95% success rate |
| **Assessment Calculation** | Processed in < 500ms |
| **System Availability** | 99.9% uptime (6 AM - 11 PM) |
| **API Response Time** | < 200ms for 90% of requests |
| **Security Adherence** | 100% of password resets expire at exactly 60 minutes |
| **Audit Coverage** | 100% of profile modifications logged |