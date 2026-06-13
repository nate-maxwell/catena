# Application Preferences

Herein is the internal preferences classes. These are dataclasses to store, read,
and write preference data to the appdata roaming folder.

The preferences class is a singleton that any system can access at any time.
When the preferences singleton saves updates to disk it emits a blank event
over the broker.

## GUI

Preference data is necessary for the application to run but displaying preferences
data and interacting with the user at this level is not strictly necessary for
the application to run. Therefore, all preferences menus have been placed in the
components' folder.
