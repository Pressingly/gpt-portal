# User Feedback Collection - Implementation Task List

## Backend Tasks

### 1. Create User Query Counter Model and API

- [x] **1.1** Create `backend/open_webui/models/user_stats.py` with UserStats model
  - [x] Define UserStats class with user_id and query_count fields
  - [x] Add created_at and updated_at timestamps
  - [x] Add methods for incrementing and getting the query count

- [x] **1.2** Create `backend/open_webui/routers/user_stats.py` with API endpoints
  - [x] Add GET endpoint to retrieve a user's query count
  - [x] Add POST endpoint to increment a user's query count
  - [x] Add authentication requirements
  - [x] Add appropriate error handling

- [x] **1.3** Add the user_stats router to `backend/open_webui/main.py`
  - [x] Import the router
  - [x] Add the router to the FastAPI app with appropriate prefix

- [x] **1.4** Modify chat completion endpoint to increment query counter
  - [x] Identify the appropriate endpoint in `backend/open_webui/main.py`
  - [x] Add logic to increment the query counter after successful completion
  - [x] Ensure error handling doesn't break existing functionality

## Frontend Tasks

### 2. PostHog Integration

- [x] **2.1** Install PostHog JS package
  - [x] Run `pnpm add posthog-js`

- [x] **2.2** Create `src/lib/posthog.ts` for PostHog configuration
  - [x] Initialize PostHog with API key and host
  - [x] Add utility functions for common PostHog operations
  - [x] Add event tracking functions for surveys

- [x] **2.3** Update `src/routes/+layout.svelte` to initialize PostHog
  - [x] Import PostHog from the configuration file
  - [x] Initialize PostHog on app load
  - [x] Ensure user identification is handled properly

- [x] **2.4** Add PostHog configuration to environment variables
  - [x] Add VITE_POSTHOG_API_KEY to `.env`
  - [x] Add VITE_POSTHOG_HOST to `.env`
  - [x] Update documentation for environment variables

### 3. Query Counter Tracking

- [x] **3.1** Add functions to `src/lib/apis/user_stats.ts`
  - [x] Create function to get a user's query count
  - [x] Create function to increment a user's query count
  - [x] Add appropriate error handling and types

- [x] **3.2** Create `src/lib/apis/chat_with_tracking.ts` to track queries
  - [x] Create wrapper for chat completion API
  - [x] Add call to increment the query counter
  - [x] Ensure error handling doesn't break existing functionality

- [x] **3.3** Add function to check if it's time to show the survey
  - [x] Create function that checks if query count is a multiple of 10
  - [x] Add logic to check if the survey was recently shown
  - [x] Return boolean indicating whether to show the survey

### 4. Survey Triggering

- [ ] **4.1** Update code to use programmatic rendering for PostHog surveys
  - [ ] Create a FeedbackSurvey component to display the survey
  - [ ] Modify the checkAndTriggerFeedbackSurvey function to use getActiveMatchingSurveys
  - [ ] Implement logic to prevent showing the survey too frequently
  - [ ] Add appropriate error handling

- [ ] **4.2** Add event tracking for survey interactions
  - [ ] Track when the survey is shown using 'survey shown' event
  - [ ] Track when the survey is dismissed using 'survey dismissed' event
  - [ ] Track when feedback is submitted using 'survey sent' event

## PostHog Configuration Tasks

### 5. PostHog Survey Setup

- [ ] **5.1** Create a feedback survey in the PostHog dashboard
  - [x] Log in to the PostHog dashboard
  - [ ] Navigate to Surveys section
  - [ ] Create a new survey with appropriate settings

- [ ] **5.2** Configure the survey appearance
  - [ ] Set colors to match the application's design
  - [ ] Configure fonts and spacing
  - [ ] Set appropriate size and position

- [ ] **5.3** Set up the survey question
  - [ ] Add a free-text question for feedback
  - [ ] Configure any additional settings

- [ ] **5.4** Configure the survey for programmatic rendering
  - [ ] Set the survey type to "API"
  - [ ] No need to configure event-based targeting
  - [ ] Ensure the survey is active and available

## Testing Tasks

### 6. Testing

- [ ] **6.1** Test the query counter functionality
  - [ ] Test incrementing the counter
  - [ ] Test retrieving the counter
  - [ ] Test error handling

- [ ] **6.2** Test the survey triggering logic
  - [ ] Test that the survey appears after 10 queries
  - [ ] Test that the survey doesn't appear too frequently
  - [ ] Test error handling

- [ ] **6.3** Test the complete feedback flow
  - [ ] Test submitting feedback
  - [ ] Test dismissing the survey
  - [ ] Test that feedback appears in the PostHog dashboard

## Documentation Tasks

### 7. Documentation

- [x] **7.1** Update documentation to include information about the feedback feature
  - [x] Add information to the user guide
  - [x] Add information to the developer documentation

- [x] **7.2** Document the PostHog integration
  - [x] Document the PostHog configuration
  - [x] Document the event tracking

- [x] **7.3** Create admin documentation
  - [x] Document how to access the PostHog dashboard
  - [x] Document how to analyze feedback
  - [x] Document how to configure the survey

## Deployment Tasks

### 8. Deployment

- [ ] **8.1** Deploy backend changes
  - [ ] Deploy the new models and API endpoints
  - [ ] Run any necessary database migrations

- [ ] **8.2** Deploy frontend changes
  - [ ] Deploy the PostHog integration
  - [ ] Deploy the survey triggering logic

- [ ] **8.3** Configure PostHog in production
  - [ ] Set up the survey in the production PostHog instance
  - [ ] Configure appropriate targeting and appearance

- [ ] **8.4** Monitor the feedback collection
  - [ ] Set up monitoring for the feedback collection
  - [ ] Set up alerts for any issues
  - [ ] Review initial feedback and adjust as needed
