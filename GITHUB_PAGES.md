# Publish on GitHub Pages

The app is ready for GitHub Pages, but it has not been published there yet. This session had no connected GitHub tool, authenticated GitHub CLI or usable signed-in browser.

The included workflow publishes only `site/dist`. Its relative asset URLs work at a project URL such as `https://USERNAME.github.io/REPOSITORY/`. No Python server, paid API or secret is required for the hosted predictor.

## Repository layout

Upload the **contents** of this project folder to the root of your chosen repository on the `main` branch. Include the hidden `.github` directory. Do not upload the enclosing `SIT720_8_1D` folder as another nested directory. The expected paths are:

```
.github/workflows/pages.yml
site/dist/index.html
site/dist/model.json
site/dist/app.js
site/dist/predict.js
site/dist/style.css
README.md
```

The remaining dataset, notebook, report and Python files can also go in this repository so its URL satisfies the task's archive/source-link requirement. Do not upload `.venv`, `.git`, caches or credentials. The submission ZIP already excludes these.

## Enable and publish

1. In the repository, open **Settings > Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Open **Actions > Publish housing predictor to GitHub Pages > Run workflow** and choose `main`. Later pushes to `main` will publish automatically.
4. Wait for the workflow to succeed and open its deployment URL.
5. Try Parramatta, Apartment, 2 bedrooms, 2 bathrooms, 1 parking and 1 August 2026. The result should be **$692,333**.
6. Check the site and repository links from a signed-out browser before giving them to the marker.

GitHub Free supports Pages for public repositories. Other account plans may support private source repositories. Check your account's available settings.

After successful deployment, replace `application_url` and `application_access` in `submission_links.json`, set `archive_url` to the accessible repository URL and clear the pending GitHub status. Rebuild the PDF and ZIP. The report builder detects the GitHub Pages URL and updates its access description automatically.

Official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
