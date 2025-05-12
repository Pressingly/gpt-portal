Story Definition

Target Review due date:

, Target Approval date:

Apr 7, 2025

Author: Grace Hoang ,Status:
Apr 4, 2025
Reviewers: ; Approver:

Accepted

,

Title: User Feedback Collection Feature

Epic: User Feedback

MVP Scope: System / Subsystem / Component / Item / Subitem

Description: Enable users to easily submit feedback about their experience using the
platform, including satisfaction ratings, specific comments, and optional suggestions.
Feedback helps inform product improvements and bug fixes.

Narrative:

●  As a user, I want to provide feedback on my experience so that the service can improve.

Acceptance Criteria:

●  Feedback UI is accessible from the main interface (e.g., footer, settings menu, or

post-query screen).

●  Feedback is prompted after free-trial ends or every 10 queries

●  Users can submit feedback via free-text comment

●  Submission confirms with a success message.

●  Feedback is stored in backend database and visible to admins.

●  Duplicate or spam submissions are rate-limited or filtered.

●  (Optional) Users may opt-in to follow-up communication about their feedback.

Test Scenarios / Cases:

Test Scenario 1: Feedback Form Submission

●  Test Case 1: After free credits expire, user is prompted to give feedback
●  Test Case 2: After every 10 queries, user is prompted to give feedback
●  Test Case 3: User submits comment → confirmation + saved to backend.

●  Test Case 4: User tries to submit empty form → "please provide feedback"

warning appears.

●  Exception Case: Network/server error → "unable to submit feedback" message.

Test Scenario 2: Data Integrity & Storage

●  Test Case 1: Feedback stored with timestamp, user ID, and context.

●  Test Case 2: Admin can view feedback via admin panel or export.

●  Exception Case: Admin panel cannot retrieve data → error logged.

Test Scenario 3: Abuse Prevention

●  Test Case 1: User submits identical feedback repeatedly in short time →

second/third attempt blocked with notice.

●  Test Case 2: Feedback contains inappropriate content → flagged by filter (if

implemented).

Design: Link to a 1-2 page story technical design document
Estimation: [Story points or time estimate] ⇒ should be within 1 sprint or maximum 2
sprints

Notes:

●  Requires integration with mPass OAuth2 API.

●  Design must comply with single sign-on (SSO) and security best practices.

●  Clarify logout flow — whether logout also triggers mPass logout or just clears local session.

Owner: [Product Owner]


