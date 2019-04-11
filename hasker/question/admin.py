from django.contrib import admin

from .models import Question, Answer, Tag


class AnsweraInline(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnsweraInline
    ]


class TagAdmin(admin.ModelAdmin):
    pass


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
