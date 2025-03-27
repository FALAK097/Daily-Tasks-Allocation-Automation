You are writing code to interact with Google Sheets for a task allocation system.

CONTEXT:
- Service reads daily task data from Google Sheets
- Sheets are named by date (e.g., "24 March")
- Uses Google Sheets API v4
- Requires service account authentication

REQUIREMENTS:
1. Sheet Access:
   - Read-only access to sheets
   - Find sheets by date
   - Handle sheet metadata
   - Support GID-based access

2. Data Format:
   - Parse task data
   - Handle project groupings
   - Support status fields
   - Handle empty cells

3. Authentication:
   - Use service account credentials
   - Handle token refresh
   - Secure credential storage
   - Support scoped access

4. Error Handling:
   - Handle missing sheets
   - Handle API quota limits
   - Handle permission issues
   - Log errors appropriately

CONSTRAINTS:
- Minimize API calls
- Cache when possible
- Handle rate limits
- Support weekend detection

RESPONSE FORMAT:
When writing code for this component:
1. Use Google API best practices
2. Include proper error handling
3. Add performance optimizations
4. Document API interactions
5. Include retry logic
6. Handle edge cases
