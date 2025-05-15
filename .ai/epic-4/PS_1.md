**Story Definition**

**Author:** Grace Hoang ,**Status**: Accepted,
**Target Review due date**: Apr 4, 2025, **Target Approval date**: Apr 7, 2025
**Reviewers**: ; **Approver**:

**Title:** Provide Initial Trial Access for New Users

**Epic:** Payment System

**MVP Scope**: System / Subsystem / Component / Item / Subitem

**Description**: Enable first-time users to experience the service for free through a credited trial of $0.25, helping them evaluate its value before committing to a paid plan.

**Narrative:**

* As a user, I want to have an initial trial to test out the service before I decide to pay, so that I can evaluate its usefulness without financial risk.

**Acceptance Criteria:**

* New users receive a trial balance of $0.25 upon account creation.
* Trial usage is clearly indicated via a progress bar or balance indicator.
* Users are notified when they are approaching the trial limit (e.g., 80% consumed).
* Users are locked out of query access once the trial is fully used unless they upgrade.
* Users can view how much of the trial balance was used and for what queries.
* A call-to-action (CTA) to upgrade is shown prominently once trial ends.
* Trial is available only once per user/account/device.
* Edge case: Trial abuse (e.g., multi-accounting) is flagged via backend safeguards.

**Test Scenarios / Cases:**

**Test Scenario 1: Trial Activation**

* Test Case 1: User signs up → automatically receives $0.25 trial balance.
* Test Case 2: Trial credit is displayed above search bar.
* Exception Case: Trial already consumed on same device → no free access.

**Test Scenario 2: Usage Tracking & Lockout**

* Test Case 1: Trial queries reduce remaining balance accurately.
* Test Case 2: User is notified at 80%, 95%, and 100% consumption thresholds.
* Test Case 3: Query blocked after trial fully used → upgrade prompt appears.
* Exception Case: Query fails but still deducts trial budget → rollback mechanism is triggered.

**Test Scenario 3: Upgrade Prompting**

* Test Case 1: On trial end, display modal with pricing options.
* Test Case 2: Trial history is preserved even after upgrade.

**Design:** Link to a 1-2 page [story technical design](https://docs.google.com/document/d/1Wf5yDHEA9-Vd58E1XASmBtFrHSQd0c9V2XCwjAZURnc/edit?usp=sharing) document

**Estimation:** [Story points or time estimate] ⇒ should be within 1 sprint or maximum 2 sprints

**Notes:**

* Trial amount set to $0.25 for MVP; may adjust based on usage analytics.
* Option to disable trial for org-managed enterprise accounts.
* Future extension could include referral-based bonus trials

**Owner**: [Product Owner]