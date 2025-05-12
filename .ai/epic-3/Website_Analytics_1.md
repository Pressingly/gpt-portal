**Story Definition**

**Author:** Grace Hoang ,**Status**: Accepted,
**Target Review due date**: Apr 4, 2025, **Target Approval date**: Apr 7, 2025
**Reviewers**: ; **Approver**:

**Title:** User Behavior Tracking System A side

**Epic:** Website Analytics

**MVP Scope**: System / Subsystem / Component / Item / Subitem

**Description**: Implement behavior tracking infrastructure to collect anonymized data about user interactions across GPTPortal. This includes usage patterns, query history, clicks, feedback, plan selections, and conversion metrics, enabling admins to drive UX improvements and strategic product enhancements.

**Narrative:**

* As an admin, I want to track user behavior on the platform so that I can improve the product, the user experience, and add features.

**Acceptance Criteria:**

The platform should track the following metrics to evaluate performance and user behavior:

1. Usage Metrics
   * Admin dashboard
     1. Contains all that user dashboard contains AND
     2. Total queries per hour/day/week/month
     3. Total queries by user per hour/day/week/month
     4. Queries per LLM per day/week/month
     5. Total number of queries that are multi-LLM as well as the percentage
     6. Number of times each LLM combination is used sorted from most commonly used to least
   * Peak usage times/days and patterns → reporting on total queries per hour/day
2. Financial Metrics
   * Admin dashboard
     1. Contains all that user dashboard contains AND
     2. Total revenue per hour/day/week/month
     3. Total revenue per LLM per hour/day/week/month
     4. Rank users based on revenue per hour/day/week/month
        1. Who spent the most…
     5. Rank LLMs based on revenue per hour/day/week/month
        1. Which LLM gave the most…
     6. Total average cost per query

* Data is collected with privacy compliance
* Admin dashboard displays aggregated behavior data over time.
* Supports the addition of future analytics
* Behavior data can be exported in CSV or JSON format.
* Events include timestamps and basic metadata (browser, device, etc.).
* Dashboard supports filtering by date range, LLM.
* Spike detection or outlier activity triggers admin alerts (optional).

**Test Scenarios / Cases:**

Test Scenario 1: Basic Usage Metrics Tracking

* Test Case 1: Admin views total queries per day → dashboard shows accurate daily totals with timestamp breakdown.
* Test Case 2: Admin views queries per user per day → dashboard shows accurate per-user breakdown.
* Test Case 3: Admin views queries per LLM per day → dashboard shows accurate breakdown by LLM type.
* Exception Case: No data available for selected period → appropriate "no data" message displayed.

Test Scenario 2: Advanced Usage Analytics

* Test Case 1: Admin views average queries per user session → dashboard displays correct calculation.
* Test Case 2: Admin views multi-LLM query statistics → dashboard shows accurate count, percentage, and ranking.
* Test Case 3: Admin views peak usage patterns → dashboard highlights peak usage times/days.
* Exception Case: Abnormal usage spike detected → system flags potential outlier.

Test Scenario 3: Financial Metrics

* Test Case 1: Admin views total revenue per day/week/month → dashboard shows accurate revenue totals.
* Test Case 2: Admin views revenue per LLM → dashboard shows accurate breakdown by LLM.
* Test Case 3: Admin views user ranking by revenue → dashboard shows users sorted by spending.
* Exception Case: Refund processed during period → revenue calculations adjust accordingly.

Test Scenario 4: Data Management Features

* Test Case 1: Admin exports usage data as CSV → file downloads with correct format and data.
* Test Case 2: Admin exports usage data as JSON → file downloads with correct format and data.

**Design:** Link to a 1-2 page [story technical design](https://docs.google.com/document/d/1Wf5yDHEA9-Vd58E1XASmBtFrHSQd0c9V2XCwjAZURnc/edit?usp=sharing) document

**Estimation:** [Story points or time estimate] ⇒ should be within 1 sprint or maximum 2 sprints

**Notes:**

* Requires integration with mPass OAuth2 API.
* Design must comply with single sign-on (SSO) and security best practices.
* Clarify logout flow — whether logout also triggers mPass logout or just clears local session.

**Owner**: [Product Owner]