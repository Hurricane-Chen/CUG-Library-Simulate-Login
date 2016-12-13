# CUG-Library
<p>测试运行环境：python3.5.1</p>
<h3>依赖包与软件</h3>
<p>除了python3的内置模块外，仅需要再安装Flask组件</p>
<p>需要安装tesseract: $sudo apt-get install tesseract-ocr</p>
<h3>运行前的注意事项</h3>
<p>libApi.py 与 cuglib.py 需要在同一文件夹内</p>
<p>建议cd到文件夹内运行libApi.py</p>
<h3>关于api</h3>
<p>对于所有方法，都只需要post两个参数:</p>
<p>userid(一般是学号)</p>
<p>password(如果用户之前没有登陆过图书馆主页修改密码，那么它应该与学号相同)</p>
<p></p>
<p>对不同url post参数意义分别是:</p>
<p>/VerifyPassword: 验证用户的图书馆登录密码是否正确，正确则返回{result:1}, 否则result为0并在reason中附上错误原因</p>
<p>/GetNowBooks: 建议在已经验明密码之前之后再post，返回 result:1 及 list:用户当前借阅书目</p>
<p>/GetHistoryBooks: 同上，不过返回的是用户的历史借阅书目</p>
<p>/RebookAll: 一键续借用户的全部书目。如果全部借阅成功直接返回 result:1 否则返回 result:0 及 failure:借阅失败书籍的书名(注意！只是书名！)</p>
<p></p>
<p>需要注意的是，每一本书都有如下参数： 书名 条形码 借阅日期 归还日期(如果是现在借阅的书籍，那么它实际上就是应还日期) </p>
