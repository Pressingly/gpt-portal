/**
 * Session management utilities for tracking user sessions
 */

import { browser } from '$app/environment';
import { captureEvent } from '$lib/posthog';
import { v4 as uuidv4 } from 'uuid';

// Session timeout (30 minutes of inactivity)
const SESSION_TIMEOUT = 30 * 60 * 1000;

/**
 * Generate a new session ID
 * @returns A new session ID
 */
export function generateSessionId(): string {
  const sessionId = uuidv4();
  if (browser) {
    localStorage.setItem('session_id', sessionId);
    localStorage.setItem('session_start', Date.now().toString());
    localStorage.setItem('session_last_activity', Date.now().toString());
    localStorage.setItem('session_query_count', '0');
    localStorage.setItem('session_total_cost', '0');
  }
  return sessionId;
}

/**
 * Track session start
 */
export function trackSessionStart(): void {
  if (!browser) return;
  
  const userId = localStorage.getItem('user_id');
  const sessionId = localStorage.getItem('session_id') || generateSessionId();
  
  // Get device and browser info
  const deviceInfo = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    screenSize: `${window.screen.width}x${window.screen.height}`
  };
  
  const browserInfo = {
    language: navigator.language,
    cookiesEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack
  };
  
  // Track session start event
  captureEvent('session_started', {
    user_id: userId,
    session_id: sessionId,
    device_info: deviceInfo,
    browser_info: browserInfo
  });
}

/**
 * Update session activity
 * @param queryCost Cost of the query to add to the session total
 */
export function updateSessionActivity(queryCost: number = 0): void {
  if (!browser) return;
  
  const now = Date.now();
  const lastActivity = parseInt(localStorage.getItem('session_last_activity') || '0');
  
  // Check if session has timed out
  if (now - lastActivity > SESSION_TIMEOUT) {
    // End the previous session
    trackSessionEnd();
    // Start a new session
    trackSessionStart();
  } else {
    // Update session activity
    localStorage.setItem('session_last_activity', now.toString());
    
    // Update query count
    const queryCount = parseInt(localStorage.getItem('session_query_count') || '0');
    localStorage.setItem('session_query_count', (queryCount + 1).toString());
    
    // Update total cost
    const totalCost = parseFloat(localStorage.getItem('session_total_cost') || '0');
    localStorage.setItem('session_total_cost', (totalCost + queryCost).toString());
  }
}

/**
 * Track session end
 */
export function trackSessionEnd(): void {
  if (!browser) return;
  
  const userId = localStorage.getItem('user_id');
  const sessionId = localStorage.getItem('session_id');
  const sessionStart = parseInt(localStorage.getItem('session_start') || '0');
  const lastActivity = parseInt(localStorage.getItem('session_last_activity') || '0');
  const queryCount = parseInt(localStorage.getItem('session_query_count') || '0');
  const totalCost = parseFloat(localStorage.getItem('session_total_cost') || '0');
  
  if (sessionId && sessionStart) {
    const sessionDuration = lastActivity - sessionStart;
    
    // Track session end event
    captureEvent('session_ended', {
      user_id: userId,
      session_id: sessionId,
      session_duration: sessionDuration,
      query_count: queryCount,
      total_cost: totalCost
    });
  }
}

/**
 * Initialize session tracking
 */
export function initializeSessionTracking(): void {
  if (!browser) return;
  
  // Check if there's an existing session
  const sessionId = localStorage.getItem('session_id');
  const lastActivity = parseInt(localStorage.getItem('session_last_activity') || '0');
  
  if (!sessionId || Date.now() - lastActivity > SESSION_TIMEOUT) {
    // Start a new session
    trackSessionStart();
  }
  
  // Set up event listeners for tracking session activity
  window.addEventListener('beforeunload', () => {
    trackSessionEnd();
  });
  
  // Update session activity periodically
  setInterval(() => {
    const lastActivity = parseInt(localStorage.getItem('session_last_activity') || '0');
    if (Date.now() - lastActivity > SESSION_TIMEOUT) {
      trackSessionEnd();
    }
  }, SESSION_TIMEOUT / 2);
}
