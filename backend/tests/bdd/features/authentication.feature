Feature: User Authentication
    As a user of the GenAI chatbot application
    I want to be able to authenticate securely
    So that I can access protected features and maintain my sessions

    Background:
        Given the application is running
        And the database is initialized
        And a test tenant exists with name "Test Company"

    Scenario: Successful user registration
        Given I am not authenticated
        When I register with valid credentials:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
            | name     | Test User            |
        Then the registration should be successful
        And I should receive a confirmation response
        And the user should exist in the database
        And the user should be assigned to the default role

    Scenario: Registration with invalid email format
        Given I am not authenticated
        When I register with invalid credentials:
            | field    | value              |
            | email    | invalid-email      |
            | password | SecurePassword123! |
            | name     | Test User          |
        Then the registration should fail
        And I should receive an error message "Invalid email format"

    Scenario: Registration with weak password
        Given I am not authenticated
        When I register with invalid credentials:
            | field    | value             |
            | email    | test@example.com  |
            | password | weak              |
            | name     | Test User         |
        Then the registration should fail
        And I should receive an error message containing "Password does not meet requirements"

    Scenario: Successful user login
        Given a user exists with:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
            | name     | Test User            |
            | verified | true                 |
        When I login with correct credentials:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
        Then the login should be successful
        And I should receive an access token
        And I should receive a refresh token
        And the tokens should be valid
        And my user profile should be included in the response

    Scenario: Login with incorrect password
        Given a user exists with:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
            | name     | Test User            |
            | verified | true                 |
        When I login with incorrect credentials:
            | field    | value                |
            | email    | test@example.com     |
            | password | WrongPassword        |
        Then the login should fail
        And I should receive an error message "Invalid credentials"
        And no tokens should be issued

    Scenario: Login with unverified account
        Given a user exists with:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
            | name     | Test User            |
            | verified | false                |
        When I login with correct credentials:
            | field    | value                |
            | email    | test@example.com     |
            | password | SecurePassword123!   |
        Then the login should fail
        And I should receive an error message "Account not verified"

    Scenario: Access protected resource with valid token
        Given I am authenticated as a user with:
            | field    | value                |
            | email    | test@example.com     |
            | name     | Test User            |
            | role     | user                 |
        When I access a protected resource "/api/auth/profile"
        Then the request should be successful
        And I should receive my user profile information

    Scenario: Access protected resource with invalid token
        Given I have an invalid authentication token
        When I access a protected resource "/api/auth/profile"
        Then the request should fail with status 401
        And I should receive an error message "Invalid or expired token"

    Scenario: Token refresh with valid refresh token
        Given I am authenticated with tokens:
            | token_type    | status  |
            | access_token  | expired |
            | refresh_token | valid   |
        When I refresh my tokens using the refresh token
        Then the token refresh should be successful
        And I should receive a new access token
        And I should receive a new refresh token
        And the old tokens should be invalidated

    Scenario: Token refresh with invalid refresh token
        Given I have an invalid refresh token
        When I refresh my tokens using the refresh token
        Then the token refresh should fail
        And I should receive an error message "Invalid refresh token"

    Scenario: User logout
        Given I am authenticated as a user
        When I logout
        Then the logout should be successful
        And my tokens should be invalidated
        And I should not be able to access protected resources

    Scenario: Change password with valid current password
        Given I am authenticated as a user with password "OldPassword123!"
        When I change my password:
            | field            | value            |
            | current_password | OldPassword123!  |
            | new_password     | NewPassword123!  |
        Then the password change should be successful
        And I should be able to login with the new password
        And I should not be able to login with the old password

    Scenario: Change password with incorrect current password
        Given I am authenticated as a user with password "OldPassword123!"
        When I change my password:
            | field            | value            |
            | current_password | WrongPassword    |
            | new_password     | NewPassword123!  |
        Then the password change should fail
        And I should receive an error message "Current password is incorrect"
        And I should still be able to login with the old password

    Scenario: Multiple failed login attempts trigger account lockout
        Given a user exists with email "test@example.com"
        When I attempt to login 5 times with incorrect password
        Then the account should be temporarily locked
        And subsequent login attempts should fail with "Account temporarily locked"
        And I should receive information about lockout duration

    Scenario: Admin user can access admin resources
        Given I am authenticated as an admin user
        When I access an admin resource "/api/admin/users"
        Then the request should be successful
        And I should receive the requested admin data

    Scenario: Regular user cannot access admin resources
        Given I am authenticated as a regular user
        When I access an admin resource "/api/admin/users"
        Then the request should fail with status 403
        And I should receive an error message "Insufficient permissions"
