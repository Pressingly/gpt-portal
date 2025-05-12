# PostHog Survey Configuration Guide

This guide provides step-by-step instructions for configuring a feedback survey in PostHog that will be shown to users after every 10 queries.

## Prerequisites

- PostHog account with admin access
- PostHog project API key
- PostHog host URL (e.g., https://app.posthog.com)

## Creating a Feedback Survey

### 1. Access the PostHog Dashboard

1. Log in to your PostHog account
2. Select your project
3. Navigate to "Surveys" in the left sidebar
4. Click "New survey"

### 2. Select Survey Type

1. Choose "API" as the survey type
2. Click "Next"

### 3. Configure Survey Questions

1. Set the survey name to "User Feedback Survey"
2. Add a description (optional)
3. Configure the question:
   - Question text: "How can we improve your experience?"
   - Question type: "Open text"
   - Make the question required
4. Click "Next"

### 4. Configure Survey Targeting

1. Select "Show to users who trigger a specific event"
2. Choose the `feedback_survey_trigger` event
3. Set the survey to "Can reappear" with a minimum time between appearances of 24 hours
4. Click "Next"

### 5. Configure Survey Appearance

1. Set the position to "Bottom Right"
2. Choose colors that match your application's design:
   - Background color: Match your app's background
   - Text color: Match your app's text color
   - Button color: Match your app's primary button color
3. Configure the thank you message:
   - Enable the thank you message
   - Set the header to "Thank you for your feedback!"
4. Click "Next"

### 6. Review and Launch

1. Review all settings
2. Click "Launch survey"

## Targeting Configuration Details

### Event-Based Targeting

The survey is configured to appear when the `feedback_survey_trigger` event is captured. This event is triggered in our application when a user's query count reaches a multiple of 10.

### Reappearance Settings

To prevent survey fatigue while still collecting regular feedback:

1. Set the survey to "Can reappear"
2. Set the minimum time between appearances to 24 hours
3. Our application also tracks survey interactions in localStorage to provide additional control

## Survey Appearance Customization

### Matching Your Application's Design

For a seamless user experience, customize the survey appearance to match your application:

1. Use the same font family as your application
2. Match the background color to your application's card or modal background
3. Match the text color to your application's primary text color
4. Match the button colors to your application's primary button colors

### Mobile Responsiveness

Ensure the survey displays well on mobile devices:

1. Test the survey on various screen sizes
2. Adjust the width and position as needed
3. Ensure text is readable on small screens

## Testing the Survey

### Manual Testing

1. In the PostHog dashboard, click "Preview" on your survey
2. The survey will appear in your current browser window
3. Test submitting feedback and dismissing the survey

### Integration Testing

1. Implement the PostHog integration in your application
2. Trigger the `feedback_survey_trigger` event manually
3. Verify that the survey appears
4. Test submitting feedback and dismissing the survey
5. Verify that the feedback appears in the PostHog dashboard

## Viewing Survey Results

### Accessing Survey Results

1. Navigate to "Surveys" in the PostHog dashboard
2. Click on your survey name
3. View the "Results" tab

### Creating a Dashboard for Survey Results

1. Navigate to "Dashboards" in the PostHog dashboard
2. Click "New dashboard"
3. Add panels for:
   - Survey response rate
   - Survey completion rate
   - Recent feedback submissions
   - Feedback trends over time

## Troubleshooting

### Survey Not Appearing

1. Verify that the `feedback_survey_trigger` event is being captured
   - Check the "Events" tab in PostHog
   - Filter for the `feedback_survey_trigger` event
   - Verify that the event has the expected properties

2. Check the survey targeting settings
   - Verify that the survey is targeting the correct event
   - Ensure the survey is active and not paused

3. Check for JavaScript errors
   - Open the browser console
   - Look for any errors related to PostHog or surveys

### Feedback Not Being Recorded

1. Verify that the survey is being submitted correctly
   - Check the "Events" tab in PostHog
   - Filter for the `survey_sent` event
   - Verify that the event has the expected properties

2. Check the survey configuration
   - Verify that the survey is configured to collect responses
   - Ensure the question is set up correctly

## Best Practices

1. **Keep the survey short**: One question is ideal for a feedback survey
2. **Use clear language**: Make the question easy to understand
3. **Respect user privacy**: Only collect necessary information
4. **Prevent survey fatigue**: Don't show surveys too frequently
5. **Act on feedback**: Regularly review and act on the feedback received
6. **Test thoroughly**: Ensure the survey appears correctly and doesn't disrupt the user experience
