from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Video, VideoLike
from .forms import VideoUploadForm
from .imagekit_client import get_client_upload_auth



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

@login_required
def video_upload_auth(request):
    return JsonResponse(get_client_upload_auth())


# Save ImageKit metadata after the browser uploads the file directly.
@login_required
@require_POST
def video_upload(request):
    form = VideoUploadForm(request.POST)
    if form.is_valid():
        video = Video.objects.create(
            user=request.user,
            title=form.cleaned_data["title"],
            description=form.cleaned_data["description"],
            file_id=form.cleaned_data["file_id"],
            video_url=form.cleaned_data["video_url"],
            thumbnail_url=form.cleaned_data.get("thumbnail_url") or "",
        )
        return JsonResponse({
            "success": True,
            "video_id": video.id,
            "message": "Video uploaded successfully"
        })

    errors = []
    for field, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(f"{field}: {error}" if field != "__all__" else error)
    return JsonResponse({"success": False, "error": "; ".join(errors)})


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

# Video Voting Action
@login_required
@require_POST
def video_vote(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    vote_type = request.POST.get("vote")

    print("VOTE_TYPE", vote_type)
    print(VideoLike.LIKE_CHOICES)

    if vote_type not in ["like", "dislike"]:
        print("NOT IN LIKE CHOICES")
        return JsonResponse({"success": False, "error": "Invalid vote"}, status=400)

    # convert the given vote_type "like" or "dislike" to a value "1" or "-1"
    value = VideoLike.LIKE if vote_type == "like" else VideoLike.DISLIKE
    
    # Check if user vote for video exists
    existing_vote = VideoLike.objects.filter(user=request.user, video=video).first()


    if existing_vote:
        # Removing the user vote if they click on there same vote_type
        if existing_vote.value == value:
            if value == VideoLike.LIKE:
                video.like -=1
            else:
                video.dislikes -= 1
            existing_vote.delete()
            user_vote = None
        # Determine whether to like or dislike a video 
        else:
            if value == VideoLike.LIKE:
                video.like += 1
                video.dislikes -= 1
            else:
                video.like -= 1
                video.dislikes += 1
            existing_vote.value = value
            existing_vote.save()
            user_vote = value
    else:
        # Create a new VideoLike object and add to Video's likes or dislikes
        VideoLike.objects.create(user=request.user, video=video, value=value)
        if value == VideoLike.LIKE:
            video.like += 1
        else:
            video.dislikes += 1
        user_vote = value

    video.save(update_fields=["like", "dislikes"])

    return JsonResponse({
        "likes": video.like,
        "dislikes": video.dislikes,
        "user_vote": user_vote
    })
            
            

