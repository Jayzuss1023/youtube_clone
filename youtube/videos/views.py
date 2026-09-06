from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Video
from .forms import VideoUploadForm
from .imagekit_client import upload_video, upload_thumbnail



# Rendering the template where user will submit the form
@login_required
def video_upload_page(request):
    return render(request, "videos/upload.html", {"form": VideoUploadForm()})

# List all videos
def video_list(request):
    videos = Video.objects.all()
    return render(request, 'videos/list.html', {"videos": videos})

# Get a video
def video_detail(request, video_id):
    video = get_object_or_404(Video.objects, id=video_id)

    return render(request, "videos/detail.html", {"video": video})

def channel_videos(request, username):
    videos = Video.objects.filter(user__username=username)
    return render(request, "videos/channel.html", {"videos": videos, "channel_name": username})

# Call function that will create a video when the form is submitted on the video upload page
@login_required
@require_POST
def video_upload(request):
    # Django auto cleans the data and makes sure it's valid
    form = VideoUploadForm(request.POST, request.FILES)
    if form.is_valid():
        # extract the video_file from the form field object and assign it to a variable
        video_file = form.cleaned_data['video_file']
        # Pull thumbnail_data from HTTP POST
        custom_thumbnail = request.POST.get("thumbnail_data", "")

        try:
            # Uplaod video to imagekit
            result = upload_video(
                file_data=video_file.read(),
                file_name=video_file.name
            )

            thumbnail_url = ""

            # Attempt to upload thumbnail to imagekit
            if custom_thumbnail and custom_thumbnail.startswith("data:image"):
                try:
                    # Return the name without the file extension: "mp4, mov, mkv, wmv, etc"
                    base_name = video_file.name.rsplit(".", 1)[0]
                    thumb_result = upload_thumbnail(
                        file_data=custom_thumbnail,
                        file_name=base_name + "_thumb.jpg"
                    )
                    thumbnail_url=thumb_result["url"]     
                except Exception as e:
                    print(e)
                    pass
            # Create and add video to db
            video = Video.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                file_id=result['file_id'],
                video_url=result['url'],
                thumbnail_url=thumbnail_url
            )

            return JsonResponse({
                "success": True,
                "video_id": video.id,
                "message": "Video uploaded successfully"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    
    # Handle any incoming errors to hand back to the front-end
    errors = []
    for field, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(f"{field}: {error}" if field != "__all__" else error)
    return JsonResponse({"success": False, "errors": ";".join(errors)})


# Delete video
@login_required
@require_POST
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    try:
        delete_video(video.file_id)
    except Exception as e:
        print(e)
        pass
    
    video.delete()

    return JsonResponse({"success": True, "message": "video deleted"})