from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Book, Review
from .consts import ITEM_PER_PAGE


# ListView・・データ一覧を表示させるのに適したview
# templateView・・・最小限の機能が入っているview
def index_view(request):
    # render関数→responseオブジェクトを作成する引数1→requestで固定
    # 引数2→テンプレートを指定
    # 引数3→引数2のテンプレートで使うデータを指定する。
    # ソートに-をつけると、降順に並び替えることができる
    object_list = Book.objects.order_by('-id')
    # annotate・・・集計したデータを追加する
    ranking_list = Book.objects.annotate(
        avg_rating=Avg('review__rate')).order_by('-avg_rating')
    paginator = Paginator(ranking_list, ITEM_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.page(page_number)
    return render(request,
                  'book/index.html',
                  {'object_list': object_list,'ranking_list': ranking_list,'page_obj': page_obj},
                )


class ListBookView(LoginRequiredMixin, ListView):
    template_name = 'book/book_list.html'
    model = Book
    paginate_by = ITEM_PER_PAGE


class DetailBookView(LoginRequiredMixin, DetailView):
    template_name = 'book/book_detail.html'
    model = Book


class CreateBookView(LoginRequiredMixin, CreateView):
    template_name = 'book/book_create.html'
    model = Book
    # fieldsに、表示させるテーブルの列を指定する
    fields = ('title', 'text', 'category', 'thumbnail')
    # list-bookという名前からurlを得る
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)


class DeleteBookView(LoginRequiredMixin, DeleteView):
    template_name = 'book/book_confirm_delete.html'
    model = Book
    success_url = reverse_lazy('list-book')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied


class UpdateBookView(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ('title', 'text', 'category', 'thumbnail')
    template_name = 'book/book_update.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            # 強制的に例外を出し、例外の設定によってブラウザに例外情報を出すことができる
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk': self.object.id})


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ('book', 'title', 'text', 'rate')
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        # 同関数を上書き,context・・・render関数の三つ目の引数(データ部分)
        # super()・・・継承元、つまりCreateViewクラスのget_context_dataを呼び出す
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk': self.object.book.id})
