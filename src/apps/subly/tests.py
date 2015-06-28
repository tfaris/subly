from django.test import TestCase

from models import VideoFilter


class TestVideo(object):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.channel_title = kwargs.get('channel_title')
        self.description = kwargs.get('description')
        self.tags = kwargs.get('tags', [])
        self.publishedAt = kwargs.get('publishedAt')


test_video = TestVideo(title='Exact Match',
                       channel_title='channel',
                       description='Long description of the video.',
                       tags=['tags', 'are', 'useful', 'categorizations'],
                       publishedAt='2015-06-28T17:09:32.000Z')


class FilterTests(TestCase):
    def test_exact(self):
        self.assertTrue(VideoFilter(string='Exact Match',
                                    exact=True,
                                    field=VideoFilter.VIDEO_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='channel',
                                    exact=True,
                                    field=VideoFilter.CHANNEL_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='Long description of the video.',
                                    exact=True,
                                    field=VideoFilter.VIDEO_DESC).matches_video(test_video))
        self.assertTrue(VideoFilter(string='useful',
                                    exact=True,
                                    field=VideoFilter.TAGS).matches_video(test_video))

    def test_ignore_case(self):
        self.assertTrue(VideoFilter(string='exact',
                                    exact=False,
                                    ignore_case=True,
                                    field=VideoFilter.VIDEO_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='channel',
                                    exact=False,
                                    ignore_case=True,
                                    field=VideoFilter.CHANNEL_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='long description',
                                    exact=False,
                                    ignore_case=True,
                                    field=VideoFilter.VIDEO_DESC).matches_video(test_video))
        self.assertTrue(VideoFilter(string='categoriz',
                                    exact=False,
                                    ignore_case=True,
                                    field=VideoFilter.TAGS).matches_video(test_video))

    def test_regex(self):
        self.assertTrue(VideoFilter(string='^Exact Match$',
                                    is_regex=True,
                                    ignore_case=False,
                                    field=VideoFilter.VIDEO_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='chan*el',
                                    is_regex=True,
                                    ignore_case=True,
                                    field=VideoFilter.CHANNEL_TITLE).matches_video(test_video))
        self.assertTrue(VideoFilter(string='Long.*video\.',
                                    is_regex=True,
                                    ignore_case=True,
                                    field=VideoFilter.VIDEO_DESC).matches_video(test_video))
        self.assertTrue(VideoFilter(string='tags|are',
                                    is_regex=True,
                                    field=VideoFilter.TAGS).matches_video(test_video))
