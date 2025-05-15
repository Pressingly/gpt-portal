# Technical Design for Epic 4: Subscription Management

## Overview

This document outlines the technical design for implementing subscription management features in the GPT Portal application. The implementation includes integrating with Lago for subscription management, displaying subscription plans in a storefront iframe, and automatically enrolling new users in a trial plan.

## Storefront Iframe Integration

### Implementation Checklist for Storefront Iframe Integration

1. **Backend Configuration**
   1. Add environment variables in `docker-compose.yaml`:
      - `STOREFRONT_URL`: URL of the storefront service
      - `HAS_STOREFRONT`: Boolean flag to enable/disable storefront integration
      - `STOREFRONT_SECRET`: Secret key for JWT token generation
      - `STOREFRONT_TOKEN_KEY`: Cookie name for the storefront token
      - `STOREFRONT_EMBED_HEIGHT`: Default height for the iframe

2. **Backend Utilities**
   1. Create `backend/open_webui/moneta/utils/storefront.py` with the following functions:
      - `should_use_storefront()`: Check if storefront integration is enabled
      - `storefront_redirect_url()`: Generate the URL for the storefront iframe
      - `save_storefront_token_to_cookies()`: Set cookies for storefront authentication
      - `_encode_jwe()`: Helper function to encode JWT tokens
      - `_get_storefront_cookie_domain()`: Helper function to determine cookie domain

3. **Backend API Endpoints**
   1. Modify `backend/open_webui/main.py` to import storefront utilities:
      ```python
      from open_webui.moneta.utils.storefront import HAS_STOREFRONT, STOREFRONT_URL, storefront_redirect_url
      ```
   2. Update the `/api/config` endpoint to include storefront configuration:
      ```python
      # Add storefront configuration
      **(
          {
              "moneta": {
                  "storefront": {
                      "enabled": HAS_STOREFRONT,
                      "url": STOREFRONT_URL,
                      "redirect_url": storefront_redirect_url()
                  }
              }
          }
          if HAS_STOREFRONT else {}
      ),
      ```   

4. **Frontend Implementation**
   1. Create a new page at `src/routes/(app)/subscriptions/+page.svelte` with:
      - Script section for handling iframe communication
      - Template section with conditional rendering for loading/error states
      - Iframe element with proper security attributes
      - Message event listener for iframe height adjustment

5. **Security Considerations**
   1. Update `backend/open_webui/utils/security_headers.py` to handle CSP headers:
      - Modify `set_content_security_policy()` function to allow iframe embedding
      - Add environment variable for CSP configuration in `docker-compose.yaml`
   2. Implement origin validation in the frontend message handler:
      ```javascript
      if (!storefrontUrl || !event.origin.includes(new URL(storefrontUrl).hostname)) {
          console.warn('Received message from untrusted origin:', event.origin);
          return;
      }
      ```
   3. Add proper sandbox attributes to the iframe:
      ```html
      sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
      ```

6. **Error Handling**
   1. Implement loading state with timeout:
      ```javascript
      loadTimeout = setTimeout(() => {
          if (loading) {
              loading = false;
              error = true;
              errorMessage = i18n.t('Subscription plans are taking too long to load. Please try again later.');
              toast.error(errorMessage);
          }
      }, 30000); // 30 seconds timeout
      ```
   2. Add error handling for iframe loading failures:
      ```javascript
      const handleIframeError = () => {
          loading = false;
          error = true;
          errorMessage = i18n.t('Failed to load subscription plans. Please try again later.');
          clearTimeout(loadTimeout);
          toast.error(errorMessage);
      };
      ```
   3. Display user-friendly error messages with retry option

7. **Testing**
   1. Test iframe loading with valid storefront URL
   2. Test error handling when storefront is unavailable
   3. Test message event handling for height adjustment
   4. Test security features (CSP, sandbox attributes)
   5. Test responsive design on different screen sizes


## Auto-Subscription Feature

The auto-subscription feature automatically enrolls new users in a trial subscription plan with 25 cent credit when they sign up for the application.

### Implementation Checklist for Auto-Subscription Feature

1. Add the `LAGO_TRIAL_PLAN_CODE` environment variable to `backend/open_webui/moneta/utils/lago.py` to specify which subscription plan new users should be automatically enrolled in
2. Create a new `create_subscription(user_id: str)` function in `backend/open_webui/moneta/utils/lago.py` that will handle the API call to Lago to create a subscription for the specified user
3. Update the `upsert_customer` function to call the new `create_subscription` function after successfully creating or updating a customer in Lago
4. Add appropriate error handling and logging throughout the implementation to ensure failures are properly captured and don't affect the user experience
5. Update documentation to reflect the new environment variable and functionality, including any changes to deployment requirements
6. Test the implementation to ensure users are automatically subscribed to the trial plan with 25 cent credit when they sign up
