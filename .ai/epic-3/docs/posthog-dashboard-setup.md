# PostHog Dashboard Setup Guide

## Overview

This guide explains how to set up PostHog dashboards to visualize the analytics data collected from GPT Portal. The dashboards are designed to provide insights into usage metrics and financial metrics as specified in the Website Analytics epic.

## Prerequisites

- Access to the PostHog dashboard
- GPT Portal configured to send events to PostHog

## Dashboard Setup

### 1. Usage Metrics Dashboard

Create a new dashboard in PostHog called "GPT Portal - Usage Metrics" with the following insights:

#### Total Queries Over Time

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Line chart
- **Breakdown**: None
- **Filters**: None
- **Time Range**: Last 30 days
- **Group By**: Day/Week/Month (configurable)

#### Queries Per User

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Table
- **Breakdown By**: `user_id`
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Count

#### Queries Per LLM

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Bar chart
- **Breakdown By**: `model_id`
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Count

#### Multi-LLM Usage

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Pie chart
- **Breakdown By**: `model_id`
- **Filters**: `is_multi_llm = true`
- **Time Range**: Last 30 days
- **Calculation**: Count

#### Peak Usage Times

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Heatmap
- **Breakdown By**: Hour of day
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Count

### 2. Financial Metrics Dashboard

Create a new dashboard in PostHog called "GPT Portal - Financial Metrics" with the following insights:

#### Total Revenue Over Time

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Line chart
- **Breakdown**: None
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Sum of `query_cost`
- **Group By**: Day/Week/Month (configurable)

#### Revenue Per LLM

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Bar chart
- **Breakdown By**: `model_id`
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Sum of `query_cost`

#### Top Users By Spending

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Table
- **Breakdown By**: `user_id`
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Sum of `query_cost`
- **Sort**: Descending by sum of `query_cost`

#### Average Cost Per Query

- **Insight Type**: Trends
- **Event**: `query_completed`
- **Display**: Number
- **Breakdown**: None
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Average of `query_cost`

### 3. User Behavior Dashboard

Create a new dashboard in PostHog called "GPT Portal - User Behavior" with the following insights:

#### Session Duration

- **Insight Type**: Trends
- **Event**: `session_ended`
- **Display**: Histogram
- **Breakdown**: None
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Average of `session_duration`

#### Model Selection Patterns

- **Insight Type**: Trends
- **Event**: `model_selected`
- **Display**: Bar chart
- **Breakdown By**: `model_id`
- **Filters**: None
- **Time Range**: Last 30 days
- **Calculation**: Count

#### User Retention

- **Insight Type**: Retention
- **Event**: `session_started`
- **Display**: Retention matrix
- **Breakdown**: None
- **Filters**: None
- **Time Range**: Last 30 days

## Data Export

PostHog provides built-in functionality for exporting data in CSV or JSON format:

1. Navigate to the dashboard you want to export data from
2. Click on the insight you want to export
3. Click the "Export" button in the top-right corner
4. Select the format (CSV or JSON)
5. Click "Export" to download the file

## Filtering and Date Ranges

All dashboards support filtering by date range and other properties:

1. Click on the date range selector in the top-right corner of the dashboard
2. Select the desired date range (e.g., Last 7 days, Last 30 days, Custom range)
3. Click "Apply"

To filter by other properties:

1. Click on the "Filter" button in the top-right corner of the dashboard
2. Select the property to filter by (e.g., `model_id`, `user_id`)
3. Select the operator (e.g., equals, contains)
4. Enter the value to filter by
5. Click "Apply"

## Alerts

PostHog supports setting up alerts for specific metrics:

1. Navigate to the insight you want to set an alert for
2. Click the "..." menu in the top-right corner
3. Select "Subscribe to alerts"
4. Configure the alert conditions (e.g., threshold, frequency)
5. Select the notification method (e.g., email, Slack)
6. Click "Save"

This can be used to set up alerts for abnormal activity or usage spikes as mentioned in the Website Analytics epic.
