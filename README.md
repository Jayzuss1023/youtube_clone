# YouTube Clone

A small video sharing app built with Django. You can sign up, upload a video, watch it on a detail page, like or dislike it, and browse a user's channel. Files are stored on ImageKit instead of the local disk.

This is a learning / portfolio project, not a full YouTube replacement.

Production: https://youtube-clone-five-nu-89.vercel.app

## What it does

- **Home feed** — newest videos first, with title, channel, thumbnail, and view count
- **Watch page** — player plus description, like/dislike, and delete (if you own the video)
- **Upload** — logged-in users pick a file mp4 / webm / mov / avi, max 100 MB, title, description, and optionally a custom thumbnail
- **Channels** — `/channel/<username>/` lists that user's videos
- **Auth** — register, login, and logout using Django's built in user system

## How it's put together

Django renders HTML templates. Uploads go to ImageKit. The database only stores metadata (`file_id`, `video_url`, thumbnail URL, counts). Playback uses ImageKit's URL when possible, plus a quality transform. If the user didn't upload a thumbnail, ImageKit can generate one from the video.

Likes and dislikes are a separate `VideoLike` row, unique per user + video. Clicking the same vote again removes it. Switching from like to dislike (or the other way) updates both counters.

## Tech

- Python 3.12 (Vercel; 3.11+ locally)
- Django
- SQLite locally. Neon Postgres in production
- ImageKit (`imagekitio`) for upload, thumbnails, and streaming
- python-dotenv for keys
- Server rendered templates + a bit of CSS
- UV for the project/env

## Routes

| Path                   | What it does                                          |
| ---------------------- | ----------------------------------------------------- |
| `/`                    | Video list                                            |
| `/upload/`             | Upload form (login required)                          |
| `/upload/submit/`      | POST the file to ImageKit + save the row              |
| `/<id>`                | Watch page                                            |
| `/<id>/vote/`          | Like or dislike                                       |
| `/<id>/delete/`        | Delete the video (and try to remove it from ImageKit) |
| `/channel/<username>/` | That user's videos                                    |
| `/accounts/register/`  | Sign up                                               |
| `/accounts/login/`     | Sign in                                               |
| `/accounts/logout/`    | Log out                                               |

## Running it locally

You'll need Python 3.11+ and an [ImageKit](https://imagekit.io/) account.

```bash
uv sync
cd youtube
```

Create `youtube/.env` with your ImageKit keys (the SDK also expects the usual ImageKit env vars, not just the public key):

```
IMAGEKIT_PUBLIC_KEY=
IMAGEKIT_PRIVATE_KEY=
IMAGEKIT_URL_ENDPOINT=
```

Then:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

App runs at `http://127.0.0.1:8000`.

## Notes

- Don't commit `.env` or `db.sqlite3`.
- View counts are on the model but aren't incremented on every watch yet.
- Large video uploads through Vercel may fail because of serverless request size limits.

## License

Personal / portfolio project.
