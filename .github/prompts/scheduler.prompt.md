You are implementing scheduling logic for a daily task allocation system.

CONTEXT:
- Service runs daily at specific times
- Handles email scheduling
- Uses APScheduler
- Supports graceful shutdown

REQUIREMENTS:
1. Scheduling:
   - Run at specific times
   - Handle timezone awareness
   - Skip weekends
   - Support manual triggers

2. Job Management:
   - Handle job failures
   - Prevent duplicate runs
   - Support job cancellation
   - Monitor job status

3. Error Recovery:
   - Handle crash recovery
   - Support job retries
   - Log failed attempts
   - Notify on failures

4. Performance:
   - Minimize resource usage
   - Handle concurrent jobs
   - Proper cleanup
   - Memory management

CONSTRAINTS:
- Single instance running
- Graceful shutdown
- Resource efficient
- Proper logging

RESPONSE FORMAT:
When writing scheduler code:
1. Use proper job definitions
2. Include error handling
3. Add monitoring hooks
4. Document configurations
5. Handle edge cases
