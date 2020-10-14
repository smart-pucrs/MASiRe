## [Unreleased]
### Added
- Changelog to keep track of changes
- New metrics: victim discovered, hidden, known
- Sends to the api and monitor a partial report at every step
- New way to navigate through steps
- Max and minimum speed
- On click in units now highlights the agent/event
- Map follow on the highlighted unit
- Hovering now displays the unit type
- New icons for some menu options
- Params in functions description to be more clear what is expected to receive
### Changed
- Graphical interface
- Inline functions to arrow functions for better readability
- Concatenated strings to string literals
- Event listeners for buttons instead of JS functions in HTML
### Fixed
- Analysed photo was not adding the victims in the step perceptions
- Route path was not changing size when zooming out the map
- Interaction bugs between updateSpeed and pause functions
- Entity info pannel was not properly displaying information inside nested objects
### Removed
- Unnecessary info in screen
- Navigation through matches
- Zoom buttons on the map
