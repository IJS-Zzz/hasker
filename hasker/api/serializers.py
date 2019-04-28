from rest_framework import serializers

from hasker.question.models import Answer, Question, Tag


class QuestionsListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:question-detail")

    class Meta:
        model = Question
        fields = ('pk', 'title', 'url',)


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    pub_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    answers = serializers.HyperlinkedIdentityField(view_name="api:question-answers-list")

    class Meta:
        model = Question
        fields = ('pk', 'title', 'text', 'author', 'slug', 'rating',
                  'pub_date', 'tags', 'has_answer', 'answers',)


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    pub_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)

    class Meta:
        model = Answer
        fields = ('pk', 'text', 'author', 'pub_date', 'rating',)


class TagSerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedIdentityField(view_name="api:tag-questions-list")

    class Meta:
        model = Tag
        fields = ('pk', 'name', 'questions',)


class VoteSerializer(serializers.Serializer):
    value = serializers.BooleanField()
