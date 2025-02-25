# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2023-12-07

### Changed

-   Dictionaries are now stored as SQLite databases, which should fix importing issues with some words containing letters illegal in filenames ([#6](https://github.com/abdnh/anki-wiktionary/issues/6))

### Fixed

-   Do not disable editor button when no field is focused.

## [1.1.1] - 2023-05-22

### Fixed

-   Fixed the add-on failing to extract the definitions of some words

## [1.1.0] - 2022-12-22

## Added

-   Added new fields: IPA, Audio, Etymology, and Declension.

## Fixed

-   Fixed empty HTML lists added in fields where no contents were found.
-   Fixed wrong gender being detected in many cases.

## Changed

-   Ignore empty word fields without warning about them.

## [1.0.2] - 2022-11-14

### Changed

-   Minor improvements to the GUI made and shortcuts added

## [1.0.1] - 2022-09-17

### Changed

-   Format definitions and examples as HTML lists
-   Strip HTML from queried words
-   Remember last used GUI options

## [1.0.0] - 2022-04-29

Initial release

[1.2.0]: https://github.com/abdnh/anki-wiktionary/compare/1.1.1...1.2.0
[1.1.1]: https://github.com/abdnh/anki-wiktionary/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/abdnh/anki-wiktionary/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/abdnh/anki-wiktionary/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/abdnh/anki-wiktionary/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/abdnh/anki-wiktionary/commits/1.0.0
