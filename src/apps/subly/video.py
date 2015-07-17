import json

from googleapiclient.http import BatchHttpRequest


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class SnippetItem(object):
    id = property(fget=lambda self: self._item.get('id'))
    title = property(fget=lambda self: self._get_snippet_field('title'))
    channel_title = property(fget=lambda self: self._get_snippet_field('channelTitle'))
    description = property(fget=lambda self: self._get_snippet_field('description'))
    tags = property(fget=lambda self: self._get_snippet_field('tags'))
    publishedAt = property(fget=lambda self: self._get_snippet_field('publishedAt'))

    def __init__(self, item):
        self._item = item

    def dumps(self):
        return json.dumps(self._item)

    def _get_snippet_field(self, field):
        return self._item.get('snippet', {}).get(field)

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        else:
            return super(SnippetItem, self).__eq__(other)


class Playlist(SnippetItem):
    item_count = property(fget=lambda self: self._item.get('contentDetails', {}).get('itemCount', None))


class Video(SnippetItem):
    pass


class VideoExtractor(object):
    PLAYLIST_MAX = 200

    def __init__(self, auth):
        self._auth = auth

    def get_videos(self, user):
        """
        Get videos for the specified user.
        """
        raise NotImplementedError

    def get_playlists(self, youtube, playlist_ids):
        pl_items = youtube.playlists().list(part='snippet,contentDetails',
                                            id=','.join(playlist_ids),
                                            maxResults=50).execute().get('items', [])
        return [Playlist(item) for item in pl_items]

    def get_playlist_items(self, youtube, playlist_id, max_results=10, batch=None, callback=None):
        """
        Get the video ids of videos in the specified playlist.
        """
        def handle_request(request_id, response, exception):
            if exception:
                raise exception
            else:
                vids = []
                for item in response.get('items', []):
                    vids.append(item['contentDetails']['videoId'])
                if callback:
                    callback(vids)
                else:
                    return vids
        pl_request = youtube.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=max_results)
        if batch:
            batch.add(pl_request, callback=handle_request)
        else:
            return handle_request(1, pl_request.execute(), None)

    def get_video_info(self, youtube, video_ids, batch=None, callback=None):
        def handle_request(request_id, response, exception):
            if exception:
                raise exception
            else:
                video_info_list = [Video(item) for item in response.get('items', [])]
                if callback:
                    callback(video_info_list)
                else:
                    return video_info_list
        vid_request = youtube.videos().list(part='snippet', id=','.join(video_ids), maxResults=50)
        if batch:
            batch.add(vid_request, callback=handle_request)
        else:
            return handle_request(1, vid_request.execute(), None)

    def get_service(self, user):
        return self._auth.get_service(user)

    def get_playlist_insert_request(self, youtube, playlist_id, video_id):
        """
        Create a google api request to insert the video with the specified id into
        the playlist with the specified id.
        """
        snippet = dict(
            playlistId=playlist_id,
            resourceId=dict(
                kind='youtube#video',
                videoId=video_id
            )
        )
        return youtube.playlistItems().insert(
            part='snippet',
            body={'snippet': snippet}
        )

    def create_playlist(self, youtube, title, description='', tags=None, privacy_status='private'):
        snippet = dict(
            title=title,
            description=description,
            privacyStatus=privacy_status
        )
        if tags:
            snippet['tags'] = tags
        return Playlist(youtube.playlists().insert(
            part='snippet',
            body={'snippet': snippet}
        ).execute())


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
        playlist_items_batch = BatchHttpRequest()
        for playlist in upload_playlists:
            # TODO: Find a suitable max_results. 15 seems to miss videos, skips over recent ones for older ones
            # TODO: 50 max_results * 22 subscribers = 1100-ish videos, taking around 30 seconds. Batching might help.
            self.get_playlist_items(youtube,
                                    playlist,
                                    max_results=50,
                                    batch=playlist_items_batch,
                                    callback=lambda vids: all_upload_items.extend(vids))
        playlist_items_batch.execute(http=youtube._http)
        videos = []
        vid_info_batch = BatchHttpRequest()
        for chunk in chunks(all_upload_items, 50):
            self.get_video_info(youtube, chunk, batch=vid_info_batch, callback=lambda info: videos.extend(info))
        vid_info_batch.execute(youtube._http)
        videos.sort(key=lambda v: v.publishedAt)
        return videos
