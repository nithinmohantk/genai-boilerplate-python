Feature: Chat Functionality
    As an authenticated user
    I want to engage in conversations with AI models
    So that I can get helpful responses and maintain conversation history

    Background:
        Given the application is running
        And the database is initialized
        And I am authenticated as a user with:
            | field  | value             |
            | email  | user@example.com  |
            | name   | Chat User         |
            | role   | user              |
        And AI models are configured and available

    Scenario: Create a new chat session
        Given I don't have any existing chat sessions
        When I create a new chat session with:
            | field | value                    |
            | title | My First Chat Session    |
            | model | gpt-4                    |
        Then the chat session should be created successfully
        And I should receive a session ID
        And the session should be associated with my user account
        And the session should have the correct title and model

    Scenario: Send a message in a chat session
        Given I have a chat session with ID "session-123"
        When I send a message:
            | field   | value                    |
            | content | Hello, how are you?      |
            | type    | user                     |
        Then the message should be saved successfully
        And I should receive a message ID
        And the message should be associated with the correct session
        And the AI should generate a response
        And the AI response should be saved to the session

    Scenario: Retrieve chat session history
        Given I have a chat session with messages:
            | sender | content                  | timestamp           |
            | user   | Hello, how are you?      | 2024-01-01T10:00:00 |
            | ai     | I'm doing well, thanks!  | 2024-01-01T10:00:05 |
            | user   | What can you help with?  | 2024-01-01T10:01:00 |
            | ai     | I can help with various tasks | 2024-01-01T10:01:05 |
        When I retrieve the chat session history
        Then I should receive all messages in chronological order
        And each message should contain sender, content, and timestamp
        And the total message count should be 4

    Scenario: List my chat sessions
        Given I have multiple chat sessions:
            | title              | model  | created_at          | message_count |
            | Python Help        | gpt-4  | 2024-01-01T09:00:00 | 8             |
            | Creative Writing   | claude | 2024-01-01T10:00:00 | 15            |
            | Code Review        | gpt-4  | 2024-01-01T11:00:00 | 3             |
        When I request my chat sessions list
        Then I should receive all my sessions
        And sessions should be ordered by last activity (most recent first)
        And each session should include title, model, message count, and timestamps

    Scenario: Update chat session title
        Given I have a chat session with title "Untitled Session"
        When I update the session title to "Python Development Help"
        Then the session title should be updated successfully
        And I should be able to retrieve the session with the new title

    Scenario: Delete a chat session
        Given I have a chat session with ID "session-to-delete"
        When I delete the chat session
        Then the session should be marked as deleted
        And I should not be able to retrieve the session
        And all associated messages should be marked as deleted

    Scenario: Archive a chat session
        Given I have a chat session with ID "session-to-archive"
        When I archive the chat session
        Then the session should be marked as archived
        And the session should not appear in my active sessions list
        And I should be able to retrieve archived sessions separately

    Scenario: WebSocket connection for real-time messaging
        Given I have established a WebSocket connection
        And I have a chat session with ID "session-ws-123"
        When I send a message via WebSocket:
            | field     | value                    |
            | session_id| session-ws-123           |
            | content   | Hello via WebSocket!     |
            | type      | user                     |
        Then I should receive a WebSocket confirmation
        And the AI response should be delivered via WebSocket
        And both messages should be saved to the database

    Scenario: WebSocket typing indicator
        Given I have established a WebSocket connection
        And I have a chat session with ID "session-typing-123"
        When I send a typing indicator via WebSocket
        Then other connected clients should receive the typing notification
        And the typing indicator should stop after message is sent

    Scenario: Handle AI model unavailability
        Given I have a chat session configured for model "unavailable-model"
        When I send a message to the unavailable model
        Then I should receive an error response
        And the error should indicate "AI model temporarily unavailable"
        And the user message should still be saved
        And I should be suggested to try a different model

    Scenario: Message with file attachment
        Given I have a chat session with ID "session-file-123"
        When I send a message with a file attachment:
            | field    | value                      |
            | content  | Please analyze this file   |
            | file     | document.pdf               |
            | type     | user                       |
        Then the message should be saved with the file reference
        And the file should be processed and stored securely
        And the AI should receive the file context
        And the AI response should reference the file content

    Scenario: Long conversation context management
        Given I have a chat session with 100 previous messages
        When I send a new message
        Then the system should maintain appropriate context window
        And older messages should be summarized if needed
        And the AI response should be contextually relevant
        And performance should remain acceptable

    Scenario: Concurrent message sending
        Given I have a chat session with ID "session-concurrent-123"
        When I send multiple messages simultaneously:
            | content                    | order |
            | First message              | 1     |
            | Second message             | 2     |
            | Third message              | 3     |
        Then all messages should be processed in order
        And each message should receive an appropriate AI response
        And no messages should be lost or duplicated

    Scenario: Message search within session
        Given I have a chat session with various messages about Python
        When I search for messages containing "function"
        Then I should receive all messages with that keyword
        And results should be highlighted and ranked by relevance
        And search should include both user and AI messages

    Scenario: Export chat session
        Given I have a chat session with 20 messages
        When I request to export the chat session
        Then I should receive the export in the requested format
        And the export should contain all messages with metadata
        And sensitive information should be properly handled

    Scenario: Chat session sharing (if enabled)
        Given I have a chat session I want to share
        When I create a shareable link for the session
        Then a secure sharing URL should be generated
        And the shared session should be read-only for others
        And I should be able to revoke sharing access

    Scenario: Rate limiting for messages
        Given I am sending messages rapidly
        When I exceed the rate limit of 10 messages per minute
        Then subsequent messages should be rate limited
        And I should receive appropriate error messages
        And the rate limit should reset after the time window

    Scenario: Message content moderation
        Given content moderation is enabled
        When I send a message with inappropriate content
        Then the message should be flagged or blocked
        And I should receive a content policy warning
        And the AI should not generate a response to inappropriate content

    Scenario: AI model switching during conversation
        Given I have an ongoing chat session using GPT-4
        When I switch the AI model to Claude
        Then subsequent messages should use the new model
        And the model change should be logged in the session
        And previous context should be appropriately transferred
