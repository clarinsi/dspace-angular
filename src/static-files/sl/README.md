# Documentation pages for a repository: translation to Slovenian

This directory contains static HTML pages in Slovenian that document the repository, its policies and licences.
This version is adapted for the CLARIN.SI repository.
The [parent directory](../) contains the same pages in English, while this directory should contain the files with
the same names but translated to Slovenian.

## Current status

The files in this directory, i.e. the Slovenian static HTML pages are currently still for V5.
The translations should be compared to the English files in the parent directory and the translation modified where it
differs from the English page.

The static HTML files in this directory are:

- [error.html](error.html):
  Generic error message (**unchanged from V5**).
- [terms-of-service.html](terms-of-service.html):
  Terms of service (**unchanged from V5**).
- [cookies.html](cookies.html):
  Information about cookies (**unchanged from V5**).
- [about.html](about.html):
  General information about the repository.
- [cite.html](cite.html):
  Citation guidelines.
- [deposit.html](deposit.html):
  Explanation of the deposition workflow.  CLARIN.SI V5 pages have extensive
   guidelines for metadata content in [deposit.html](deposit.html); they are encoded in
   `div[@class="alert"]` elements. As the V7 English deposit page has much simpler structure than in
   V5, it is currently not clear where to insert these gulidelines, so they have been left in the V7
   English page as comments. They need to be de-commented and moved to the appropriate place once a live
   installation is available for testing. They can be translated only once this has been done.
- [faq.html](faq.html):
  Frequenty Asked Questions.
- [item-lifecycle.html](item-lifecycle.html):
  Explains the different states of a repository item.
- [metadata.html](metadata.html):
  Information about metadata requirements, dissemination and mapping.
- [data.html](data.html):
  Information about data formar requirements (CLARIN.SI only, not part of LINDAT DSpace).
- [license-templateXXXX-versionXX.html](license-templateXXXX-versionXX.html):
  Template for forming new licence texts. **Not translated**.
- [licence-aca-id-by-inf-nored-1.0.html](licence-aca-id-by-inf-nored-1.0.html):
  CLARIN.SI licence texts (CLARIN.SI only, not part of LINDAT DSpace). **Not translated**.
- [licence-aca-id-by-nc-inf-nored-1.0.html](licence-aca-id-by-nc-inf-nored-1.0.html):
  CLARIN.SI licence texts (CLARIN.SI only, not part of LINDAT DSpace). **Not translated**.

## Translator workflow (testing changes on the live server)

Static HTML files are served as plain HTTP assets — they are **not** compiled into the Angular
bundle. This means you can update a Slovenian page in the running container without rebuilding
the Docker image.

**For each file you edit:**

1. Edit the file on the host, e.g. `src/static-files/sl/about.html`.
2. Copy it into the running container:
   ```bash
   docker cp src/static-files/sl/about.html dspace-angular0:/app/src/static-files/sl/
   ```
3. Reload the page in your browser — the change is **immediately visible**, no recompile needed.

Pages are accessible at `http://fedo.ijs.si/static/<filename-without-.html>`,
e.g. `sl/about.html` → `http://fedo.ijs.si/static/about` (the language is selected via the
flag in the top bar, not the URL).

> **Note:** This is different from editing interface strings (`sl.json5`), which do trigger a
> webpack recompile (~30–60 s). See `src/assets/i18n/README.md` for that workflow.
