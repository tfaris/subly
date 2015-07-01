def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class Video(object):
    title = property(fget=lambda self: self._get_snippet_field('title'))
    channel_title = property(fget=lambda self: self._get_snippet_field('channelTitle'))
    description = property(fget=lambda self: self._get_snippet_field('description'))
    tags = property(fget=lambda self: self._get_snippet_field('tags'))
    publishedAt = property(fget=lambda self: self._get_snippet_field('publishedAt'))

    def __init__(self, item):
        self._item = item

    def _get_snippet_field(self, field):
        return self._item.get('snippet', {}).get(field, None)


class VideoExtractor(object):
    def __init__(self, auth):
        self._auth = auth

    def get_videos(self, user):
        """
        Get videos for the specified user.
        """
        raise NotImplemented

    def get_playlist_items(self, youtube, playlist_id, max_results=10):
        """
        Get the video ids of videos in the specified playlist.
        """
        vids = []
        pl_request = youtube.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=max_results)
        for item in pl_request.execute().get('items', []):
            vids.append(item['contentDetails']['videoId'])
        return vids

    def get_video_info(self, youtube, video_ids):
        vids = []
        vid_request = youtube.videos().list(part='snippet', id=','.join(video_ids), maxResults=50)
        return [Video(item) for item in vid_request.execute().get('items', [])]

    def get_service(self, user):
        return self._auth.get_service(user)


class UploadPlaylistsVideoExtractor(VideoExtractor):
    """
    Extract a YouTube users subscription videos using the method proposed by ali1234 here:
    https://github.com/ali1234/ytsubs

    1. Gets a list of user's subsciption IDs (using the subscription API).
    2. Gets the ID of the upload playlist for each subscription (using the channels API).
    3. Gets the X most recent video IDs in each upload playlist (using the playlistItems API), and
    4. Gets details of each of the video IDs from step 3 (using the videos API).
    """
    def get_videos(self, user):
        """
        Get subscription videos for the specified user.
        :param user:
        :return:
        """
        youtube = self.get_service(user)
        # Gather a list of all IDs of the channels that the user is subscribed to.

        request = youtube.subscriptions().list(part='snippet', mine=True, maxResults=50)
        upload_playlists = []
        while request is not None:
            sub_ids = []
            subs = request.execute()
            for item in subs.get('items', []):
                sub_ids.append(item['snippet']['resourceId']['channelId'])
            # Get the ID of the uploads playlist for each subscription.
            channels_request = youtube.channels().list(part='contentDetails', id=','.join(sub_ids), maxResults=50)
            for item in channels_request.execute().get('items', []):
                upload_playlists.append(item['contentDetails']['relatedPlaylists']['uploads'])
            # Cycle to the next page of subs
            request = youtube.subscriptions().list_next(request, subs)
        all_upload_items = []
        for playlist in upload_playlists:
            all_upload_items.extend(self.get_playlist_items(youtube, playlist))
        videos = []
        for chunk in chunks(all_upload_items, 50):
            videos.extend(self.get_video_info(youtube, chunk))
        videos.sort(key=lambda v: v.publishedAt)
        return videos
