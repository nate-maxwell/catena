# Application Preferences

Herein is the internal preferences classes. These are dataclasses to store, read,
and write preference data to the appdata roaming folder.

The preferences class is a singleton that any system can access at any time.
When the preferences singleton saves updates to disk it emits a blank event
over the broker.
