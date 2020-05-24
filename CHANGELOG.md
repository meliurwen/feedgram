## Version 0.6

### Additions

+ Added buttons support
+ Added support to update a message
+ Added button to the help page
+ Added framework for easy integration of future functionalities trough menu interface
+ Added "/list" command
+ Added support to button "List"
+ Added "/unsub" command
+ Added numbered list functionality
+ Added unsubscribe from a SN functionality via menu interface
+ Added error and edge cases handling when unsubscribing from a SN profile
+ Added "/mute" command
+ Added support to button "Mute"
+ Added functionality to clean of expired states
+ Added feedback at "/unsub" command
+ Added feedback at "/sub" command
+ Added feedback at interface for unsubscribing
+ Added warning upon entering unsubscribe mode via interface
+ Added halt (mute) functionality
+ Added feedback at "/halt" command
+ Added "/halt" command
+ Added feedback at interface for halting a subscription
+ Added pause (mute) functionality
+ Added feedback at "/pause" command
+ Added "/pause" command
+ Added feedback at interface for pause a subscription

### Changes

+ Updated list menu

### Fixes

+ Fixed `KeyError` issue #15

## Version 0.1.5

### Bug fix

+ Fixed Instagram `KeyError` issue #11 
+ Added rate limiting handling in Instagram
+ Improved get_url method in `feedgram.lib.util` module
+ Improved `/status` command reply
+ Updated Instagram tests
+ Increased overall coverage
+ Some cleaning and fixes here and there
+ Moved constants to the new `test.constants` module
+ Some minor cleaning to the test files (spaces and comments)
+ Fixed grammatical error in `README.md`
+ Minor fix to the `/help` text message

## Version 0.1

### Initial release

+ Add `\start` and `\stop` commands
+ Add `\sub <social> <username>` and `\sub <social link>`
+ Add Link recognition
+ Add Instagram support
