# User Module

This module is responsible for handling user related operations.

## TODO's

### Security

- [x] Secure the fact that only the user can update his **own** data
- [x] Implement a 2 way role system:
  - one role in the user database for the instance managing (create new events, delete events, etc.)
  - one role for each user in each event to manage the event (update event, delete event, etc.)

  => For the roles and their impact on JWT scopes, a user in the database should have only a single role that will be translated into a list of scopes in the jwt to control the access to the endpoints. This should be modified and reimplemented.
- [ ] Storing the current user token in the database and invalidating it when the user logs out or when the time deltas are expired
- [ ] Implement a way to blacklist tokens if the user has modified his email or if his roles have changed

### Functionality

- [x] Implement the user registration functionality
- [x] Implement the user login functionality
- [x] Implement the user update of their first and last name
- [x] Implement the way the password is updated by having a separate endpoint for it and checking the old password
- [x] Implement the way the email is updated by checking if the email is already in use and invalidate the user session if it is
- [x] Implement the user deletion functionality
- [x] Implement a way to store the user's profile picture in the database
- [ ] Implement a user email verification process when the user registers
