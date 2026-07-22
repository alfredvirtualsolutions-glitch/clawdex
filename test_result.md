#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Test all the Juan Operating System dashboard API endpoints"

backend:
  - task: "Dashboard Stats API - GET /api/dashboard/stats"
    implemented: true
    working: false
    file: "/app/app/api/dashboard/stats/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "testing"
        comment: "CRITICAL: Endpoint returns 500 error. Database connection failed with 'connect ECONNREFUSED 127.0.0.1:5432'. The NEON_DATABASE_URL environment variable is missing from .env file. The endpoint code is properly implemented and would return agentsOnline, workflowsRunning, signalsToday, successRate, and systemHealth if database was connected. PostgreSQL database is required but not configured."

  - task: "Dashboard Workflows API - GET /api/dashboard/workflows"
    implemented: true
    working: false
    file: "/app/app/api/dashboard/workflows/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "testing"
        comment: "CRITICAL: Endpoint returns 500 error. Database connection failed with 'connect ECONNREFUSED 127.0.0.1:5432'. The NEON_DATABASE_URL environment variable is missing from .env file. The endpoint code is properly implemented and would return array of workflows with id, name, type, status, progress if database was connected."

  - task: "Dashboard Signals API - GET /api/dashboard/signals"
    implemented: true
    working: false
    file: "/app/app/api/dashboard/signals/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "testing"
        comment: "CRITICAL: Endpoint returns 500 error. Database connection failed with 'connect ECONNREFUSED 127.0.0.1:5432'. The NEON_DATABASE_URL environment variable is missing from .env file. The endpoint code is properly implemented and would return array of signals with id, type, title, campaign, timeAgo, score if database was connected."

  - task: "Dashboard Analytics API - GET /api/dashboard/analytics"
    implemented: true
    working: false
    file: "/app/app/api/dashboard/analytics/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "testing"
        comment: "CRITICAL: Endpoint returns 500 error. Database connection failed with 'connect ECONNREFUSED 127.0.0.1:5432'. The NEON_DATABASE_URL environment variable is missing from .env file. The endpoint code is properly implemented and would return signalsByCampaign, signalClassification, leadsPipeline, dailyTrend if database was connected."

frontend:
  - task: "Frontend testing not requested"
    implemented: false
    working: "NA"
    file: "N/A"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "testing"
        comment: "Frontend testing was not part of the review request. Only backend dashboard API endpoints were tested."

metadata:
  created_by: "testing_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Dashboard Stats API - GET /api/dashboard/stats"
    - "Dashboard Workflows API - GET /api/dashboard/workflows"
    - "Dashboard Signals API - GET /api/dashboard/signals"
    - "Dashboard Analytics API - GET /api/dashboard/analytics"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "testing"
    message: "Completed testing of all 4 dashboard API endpoints. All endpoints are properly implemented with correct code structure, error handling, and response formatting. However, ALL endpoints are failing with database connection errors. Root cause: NEON_DATABASE_URL environment variable is missing from /app/.env file. The pg library defaults to localhost:5432 when no connection string is provided, causing 'connect ECONNREFUSED 127.0.0.1:5432' errors. REQUIRED ACTION: Add NEON_DATABASE_URL to .env file with valid PostgreSQL connection string. The database should contain tables: search_jobs, retirement_signal_searches, extracted_leads, and outreach_queue. Once database is configured, all endpoints should work correctly as the code implementation is sound."