from django.contrib import admin
from django.utils.html import format_html
from .models import Test, Question, Answer, TestAttempt, UserAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    fields = ('label', 'text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_count', 'duration_minutes', 'passing_score', 'is_active', 'is_premium', 'premium_badge', 'created_by', 'created_at', 'bulk_upload_link')
    list_filter = ('is_active', 'is_premium', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'is_premium')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    inlines = [QuestionInline]
    fieldsets = (
        ('Test Info', {'fields': ('title', 'description', 'is_active', 'is_premium')}),
        ('Settings', {'fields': ('duration_minutes', 'passing_score')}),
        ('Meta', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def bulk_upload_link(self, obj):
        return format_html('<a class="btn btn-sm btn-info" href="{}">⬆ Bulk Upload</a>', '/admin/bulk-upload/')
    bulk_upload_link.short_description = 'Bulk'

    def question_count(self, obj):
        return obj.question_count()
    question_count.short_description = 'Questions'

    def premium_badge(self, obj):
        if obj.is_premium:
            return format_html('<span style="color:#c9a84c;font-weight:bold">👑 Premium</span>')
        return format_html('<span style="color:#888">Free</span>')
    premium_badge.short_description = 'Access'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'test', 'order', 'answer_count')
    list_filter = ('test',)
    search_fields = ('text', 'test__title')
    inlines = [AnswerInline]
    ordering = ('test', 'order')

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Question'

    def answer_count(self, obj):
        return obj.answers.count()
    answer_count.short_description = 'Answers'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'question', 'label', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Answer'


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    # FIX: score_display used format_html with {:.1f} which breaks on SafeString.
    # Use plain string formatting instead.
    list_display = ('user', 'test', 'score_display', 'correct_count', 'total_questions', 'passed', 'status', 'started_at')
    list_filter = ('status', 'passed', 'test')
    search_fields = ('user__username', 'user__full_name', 'test__title')
    readonly_fields = ('user', 'test', 'score', 'correct_count', 'total_questions', 'status', 'started_at', 'finished_at', 'passed')

    def score_display(self, obj):
        if obj.score is not None:
            color = 'green' if obj.passed else 'red'
            score_str = '{:.1f}%'.format(float(obj.score))
            return format_html('<span style="color:{};font-weight:bold;">{}</span>', color, score_str)
        return '-'
    score_display.short_description = 'Score'