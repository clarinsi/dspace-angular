# Documentation pages for a repository

This directory contains static HTML pages that document the repository, its policies and licences.
This version is adapted for the CLARIN.SI repository.
It contains the HTML files in English, while translations into Slovenian are in the [sl/](sl/) directory.

## Current status

The files in this directory, i.e. the English static HTML pages were modified for CLARIN.SI V7 and
are currently drafts: not all needed changes were fully implemented yet and they have not yet been
tested on a live installation.

The workflow consisted of manually comparing the new LINDAT V7 pages with the CLARIN.SI V5 pages,
and modifying the V7 pages to include the CLARIN.SI specific information. The files have been
checked with xmllint for well-formedness, however, links have not been checked.

## Content

The static HTML files in this directory are:

- [error.html](error.html):
  Generic error message (unchanged from V5).
- [terms-of-service.html](terms-of-service.html):
  Terms of service (unchanged from V5).
- [cookies.html](cookies.html):
  Information about cookies (unchanged from V5).  Note that it makes reference to
  Google analytics which, @TomazErjavec thought are are not used at CLARIN.SI - however, it seems we
  do call `https://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js` although this is not
  enough to actually track via Google. On the other hand, LINDAT does track via Google, see the
  footer of any of their pages,
  e.g. [https://lindat.mff.cuni.cz/repository/static/terms-of-service](https://lindat.mff.cuni.cz/repository/static/terms-of-service).
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
   installation is available for testing.
- [faq.html](faq.html):
  Frequenty Asked Questions. Note that there is some confusion on the status of the
  GitHub V7 FAQ, as it is very different from the live one on 
  [LINDAT](https://lindat.cz/faq-repository): the GitHub one has pointers to citation and deposit
  guidelines, while the live one has this information included directly, and the filenames also differ.
- [item-lifecycle.html](item-lifecycle.html):
  Explains the different states of a repository item.
- [metadata.html](metadata.html):
  Information about metadata requirements, dissemination and mapping.
- [data.html](data.html):
  Information about data formar requirements (CLARIN.SI only, not part of LINDAT DSpace - unchanged from V5).
- [license-templateXXXX-versionXX.html](license-templateXXXX-versionXX.html):
  Template for forming new licence texts.
- [licence-aca-id-by-inf-nored-1.0.html](licence-aca-id-by-inf-nored-1.0.html):
  CLARIN.SI licence texts (CLARIN.SI only, not part of LINDAT DSpace).
- [licence-aca-id-by-nc-inf-nored-1.0.html](licence-aca-id-by-nc-inf-nored-1.0.html):
  CLARIN.SI licence texts (CLARIN.SI only, not part of LINDAT DSpace).

## Translator workflow (testing changes on the live server)

Static HTML files are served as plain HTTP assets — they are **not** compiled into the Angular
bundle. This means you can update a page in the running container without rebuilding the Docker image.

**For each file you edit:**

1. Edit the file on the host, e.g. `src/static-files/about.html`.
2. Copy it into the running container:
   ```bash
   docker cp src/static-files/about.html dspace-angular0:/app/src/static-files/
   ```
3. Reload the page in your browser — the change is **immediately visible**, no recompile needed.

Pages are accessible at `http://fedo.ijs.si/static/<filename-without-.html>`,
e.g. `about.html` → `http://fedo.ijs.si/static/about`.

> **Note:** This is different from editing interface strings (`sl.json5`), which do trigger a
> webpack recompile (~30–60 s). See `src/assets/i18n/README.md` for that workflow.

## References

- v5 English originals: `clarin-dspace:dspace-xmlui/src/main/webapp/themes/UFAL/lib/html/`
- v5 Slovenian translations: `clarin-dspace:dspace-xmlui/src/main/webapp/themes/UFAL/lib/html/sl/`
- v7 English originals: `src/static-files/`
- v7 Czech translations: `src/static-files/cs/`
