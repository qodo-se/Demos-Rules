# Test Generation Flow

1. Convert flow to test friendly instructions
2. Generate Playwright page object model for <https://flex-qa-auto-dev.stage.appsiangrc.com/App/LoginPage.aspx>
3. Log in to <https://flex-qa-auto-dev.stage.appsiangrc.com/App/LoginPage.aspx> with credentials `Username: QAAutoAdmin, Password: Admin@123$` and generate a Playwright object model for the post-login page.
4. Repeat for Workflow Page.

## 1. Convert flow to test friendly instructions

Please rewrite these instructions so that it's easier to extract end to end tests from. Introduce before and after sections, and break into sections as needed:

```md
## Test Case: Create and Verify Workflow Authorization Process

### Preconditions
- Access to Pathlock application
- Valid admin credentials (Username: QAAutoAdmin, Password: Admin@123$)
- SAP ERP system available
- Test user 'USER25062727' exists in the system

### Test Setup

#### Login to Application
1. Open a browser
2. Navigate to 'https://flex-qa-auto-dev.stage.appsiangrc.com/App/LoginPage.aspx'
3. Enter username 'QAAutoAdmin' into the username field
4. Enter password 'Admin@123$' into the password field
5. Verify that the password field is editable
6. Click the Login button

### Section 1: Create Workflow Type

#### Navigate to Workflow Types
1. Click on the Hamburger menu
2. Navigate to Admin → Workflow → Workflow Types

#### Create New Workflow
1. Click on the "New Record" tab
2. Enter the following details:
   - Workflow Name: AA_AI_Test
   - Request Title: AA AI Test Request
3. Click on the "Insert" button
4. When prompted with 'Define steps for this workflow now?', click "Yes"

#### Add First Workflow Step
1. Click on the "New Step" tab
2. Enter/select the following values:
   - Step Name: AA_AI_Test Step 1
   - Parent Step: Select 'Start'
   - Step Type: Select 'Approve By Group' from the drop-down
   - Approval Group Type: Select 'IT Team' from the drop-down
3. Click on '+' near User Input
4. Check "Enable Role Selection" checkbox
5. Click on the "Insert" button

#### Add Second Workflow Step
1. Click on the "New Step" tab again
2. Enter/Select the following values:
   - Step Name: AA_AI_Test Step 2
   - Parent Step: Select 'AA_AI_Test Step 1' from the drop-down
   - Step Type: Select 'Run actions automatically' from the drop-down
   - Action to Perform: Select "Apply workflow Authorizations" from the drop-down
3. Click on the "Insert" button
4. Click "Update"
5. Close the modal window

### Section 2: Create Workflow Request

#### Initiate Request
1. Click on the "Flow" tab
2. Click on the "Actions" button
3. Select 'Open Request page' option from dropdown
4. For "Request for System", select 'SAP ERP' from the dropdown
5. For "Username", enter 'USER25062727'
6. Click on the "Next" button
7. Enter a valid comment in the comment field
8. Click on the "Submit" button
9. Verify the entered details and click on the "Submit" button again

#### Capture Request Information
1. Note the Request ID displayed on screen
2. Click on the 'All My Requests' link
3. Find the request with the noted Request ID
4. Click on the Request ID hyperlink

### Section 3: Process Workflow Request

#### Add Role to User
1. Under 'New Roles to User' enter 'SAP_BC_USER_ADMIN' in the Role field
2. Click "Add"
3. Click "Save Changes"
4. Click "Ok" on the modal window

#### Approve Request
1. Click "Approve/Decline Request" button
2. In the modal window:
   - Select Decision: 'Approved'
   - In the comment field, enter: 'Approved'
3. Click "OK"

### Section 4: Verify Workflow Completion

#### Check Approved Requests
1. Navigate to Home
2. Navigate to Reports → Approved Requests
3. Expand Filter
4. Click "Users Filter"
5. Select "Username"
6. Select "Equals" in the adjoining field
7. Enter 'USER25062727' in the next field
8. Scroll to the bottom of the page
9. Click "Apply"
10. Click "Display"

#### Verify User Workflow Status
1. Click on the Username link
2. Click "User Profile"
3. Click "Workflows"
4. Locate the request
5. Verify the current step is 'Finish'
6. Close the modal window

#### Verify Authorization Application
1. Navigate to Reports → Access → User → Profile Center → User Profile
2. In the User field, enter 'USER25062727'
3. Click "Display"
4. Click the Request ID for the previous request
5. Verify a new tab opens
6. Under "Action", verify "Apply authorizations to USER25062727" is present
7. Verify there is a green check mark on the far right

### Teardown
1. Click the username link on the top
2. Select "Sign Out"

## Expected Results
- Workflow type "AA_AI_Test" is successfully created with two steps
- Request is successfully submitted and approved
- Role "SAP_BC_USER_ADMIN" is added to user "USER25062727"
- Workflow reaches "Finish" state
- Authorizations are successfully applied to the user
```
