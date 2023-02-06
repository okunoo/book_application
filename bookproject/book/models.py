from django.db import models
from .consts import MAX_RATE

RATE_CHOICES = [(x,str(x)) for x in range(0,MAX_RATE+1)]

#右側=htmlファイル上で表示される項目。
# 左側=pythonの実装やhtmlファイルのコード上で表示される項目
CATEGORY = (('business','ビジネス'),
            ('life','生活'),
            ('other','その他')
        )

class Book(models.Model):
    title = models.CharField(max_length=100)
    #TextField・・・長い文字情報を扱う場合に使用する、複数行の入力である
    #textareaが表示される
    text = models.TextField()
    thumbnail = models.ImageField(null = True,blank=True)
    #choicesは入力されるフィールドを
    # プルダウンの選択肢にすることができる
    category = models.CharField(
        max_length=100,
        choices=CATEGORY,
    )
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    #__str__オブジェクトの文字列表現を返す。
    # オブジェクトをself.titleという文字列で表現する
    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rate = models.IntegerField(choices = RATE_CHOICES)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    