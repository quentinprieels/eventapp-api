# EventApp - API

This is the API for the EventApp project: a web application that allows users to create and manage events (tickets creation, registrations, activities, materials, etc).

## TODO's

### Logging

- [ ] Implement the logging system with a BackgroundTask instead of using the current sequential system
- [ ] Store the logs in a dedicated database to simplify management and log analysis
- [ ] Consider upgrading the logging system to a more advanced one with a open-source log analysis and management tool (like ELK stack)

## Modules of each event

### Inscriptions

- **Tickets**: Module responsible for creating and managing tickets
- **Registrations**: Module responsible for managing the registrations
- **Food**: Module responsible for managing the food, like the diets of the participants
- **Transports**: Module responsible for managing the transports, like the transports of the participants

### Logistics

- **Activities**: Module responsible for managing the activities
- **Materials**: Module responsible for managing the materials
- **Locations**: Module responsible for managing the locations and create a global map of the event

### Human Resources

- **Mission**: Module responsible for managing the missions (things to do during the event that can be asked to anyone, but that needs some instructions to be done)

### Finance

- **Payments**: Module responsible for managing the payments
- **Invoices**: Module responsible for managing the invoices (create financial prevision and indicates what comes in and what goes out)

### Checkpoints

- **Checkpoints**: Module responsible for managing the checkpoints (checkpoints could be applied to registration, transport, activities, materials, locations, etc)

### Communication

- **Notes**: Module to create collaborative notes (like decisions, meetings resume, etc)
- **Tasks**: Module to create tasks and assign them to users, along with a deadline and dependencies between tasks (to create a Gantt chart)

### Game

- **Game**: Module responsible for managing the game (like a treasure hunt, a quiz, etc)
- **Players**: Module responsible for managing the players of the game (like the teams, the players, etc)
- **Ranking**: Module responsible for managing the ranking of the game

## Modules global to all events

- **Users**: Module responsible for managing the users
- **Events**: Module responsible for managing the different events
