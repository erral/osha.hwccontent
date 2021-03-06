*** Settings ***

Resource          resource/settings.robot

Suite Setup     Start browser
Suite Teardown  Close All Browsers

*** Variables ***

${BROWSER} =  firefox

*** Test Cases ***

Anonymous can add Organisation
    Given I'm logged in as a Site Administrator
      And I add an Organisations folder
     Then I log out
      And I go to the Organisations folder
      And I register an Organisation
     Then Page Should Contain  The Organisations Title

Organisations can create news and events
    Given I'm logged in as a Site Administrator
      And I add an Organisations folder
      And I go to the Organisations folder
      And I register an Organisation
      And I go to the Organisation
      And I add a News Item
      And I go to the Organisation
      And I add an Event
     When I go to the Organisation
     Then Page Should Contain  The Event Title
      And Page Should Contain  The News Item Title
