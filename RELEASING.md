Some notes for myself to have in mind when making releases:

-   Test changes in some Anki versions we support and decide whether we need to update the minimum/maximum supported versions. Update the versions in `requirements.txt`, `setup.py`, `addon.json` and the AnkiWeb page accordingly.
-   Update `ankiweb_page.html` if needed and list major changes and bug fixes in the changelog.
-   Tag the release, e.g. `git tag -a -m "Release" 0.0.3`
-   Download the GitHub build artifacts from the last commit and make a GitHub release from them.
-   Publish the relevant .ankiaddon files from the build process to AnkiWeb. Make sure to update the correct branch! Also do not forget to paste the updated `ankiweb_page.html`.
-   Bump add-on version. Currently we only keep a version string in `setup.py`.
