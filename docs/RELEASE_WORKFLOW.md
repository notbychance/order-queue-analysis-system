# Release workflow

GitHub Actions workflow:

```text
.github/workflows/release.yml
```

## What it does

The workflow:

```text
1. Runs server tests.
2. Runs web tests, type-check and production build.
3. Runs desktop tests.
4. Builds Windows EXE for desktop client.
5. Validates Docker Compose.
6. Creates GitHub Release.
7. Uses docs/RELEASE_NOTES.md as release description.
8. Attaches release artifacts.
```

## Release notes source

The GitHub Release description is read from:

```text
docs/RELEASE_NOTES.md
```

Before creating a new release, update this file with actual release notes.

## Automatic release by tag

Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow will create a release with:

```text
title: Release v1.0.0
description: docs/RELEASE_NOTES.md
```

## Manual release

You can start the workflow manually from GitHub Actions:

```text
Actions → Release → Run workflow
```

Required input:

```text
tag_name: v1.0.0
```

Optional input:

```text
prerelease: true / false
```

## Release artifacts

The workflow attaches:

```text
queue-analysis-web-dist.zip
QueueAnalysisDesktop-windows.zip
```

## Docker images

Docker images are published by a separate workflow:

```text
.github/workflows/docker-publish.yml
```

Documentation:

```text
docs/DOCKER_PUBLISHING.md
```

Published images:

```text
ghcr.io/<owner>/<repository>/queue-analysis-server:<tag>
ghcr.io/<owner>/<repository>/queue-analysis-web:<tag>
```

## Important

If a release with the same tag already exists, GitHub CLI will fail the release creation step. Delete the old release or use a new tag.
