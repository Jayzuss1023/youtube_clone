from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Video


class ImageKitUploadAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "a@example.com", "secret")

    def test_auth_requires_login(self):
        response = self.client.get("/upload/auth/")
        self.assertEqual(response.status_code, 302)

    @patch("videos.views.get_client_upload_auth")
    def test_auth_returns_imagekit_params(self, mock_auth):
        mock_auth.return_value = {
            "token": "tok",
            "expire": 123,
            "signature": "sig",
            "publicKey": "pk",
        }
        self.client.force_login(self.user)
        response = self.client.get("/upload/auth/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "token": "tok",
                "expire": 123,
                "signature": "sig",
                "publicKey": "pk",
            },
        )


class VideoMetadataSubmitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("bob", "b@example.com", "secret")
        self.client.force_login(self.user)

    def test_submit_saves_video_from_imagekit_metadata(self):
        response = self.client.post(
            "/upload/submit/",
            {
                "title": "My clip",
                "description": "Eleven seconds",
                "file_id": "ik_file_123",
                "video_url": "https://ik.imagekit.io/demo/videos/clip.mp4",
                "thumbnail_url": "https://ik.imagekit.io/demo/thumbnails/clip.jpg",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        video = Video.objects.get(id=payload["video_id"])
        self.assertEqual(video.title, "My clip")
        self.assertEqual(video.file_id, "ik_file_123")
        self.assertEqual(video.user, self.user)

    def test_submit_rejects_missing_file_id(self):
        response = self.client.post(
            "/upload/submit/",
            {
                "title": "Missing file",
                "description": "",
                "video_url": "https://ik.imagekit.io/demo/videos/clip.mp4",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["success"])
        self.assertEqual(Video.objects.count(), 0)
