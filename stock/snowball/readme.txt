
# 分享-2022-6-4 更新本地数据
https://gitlab.com/wendy.yang1009/stock_pj
前几天说的分享下我本地更新股票数据的代码，这俩天抽出来了，
本地需要依赖数据库mongodb，目前如果仅更新股票数据的话需要Tushare的股票接口一年200块钱吧，
如果要更新板块信息差不多是500块钱，
也可以自己换成雪球，或者同花顺的,具体使用参考代码，这个群应该都懂代码。我电脑更新4800条数据差不多需要5-6分钟，数据样式即使用可以参考readme
参考：db-format.png
代码有 hk 社保 基金 qfii的持仓代码：https://gitlab.com/wendy.yang1009/stock_pj

# 2022-6-3 token自动获取
这个browser_cookie3就是读取电脑浏览器（例如Chrome Firefox Opera Edge Chromium Brave）本身已经缓存的cookie，
所以，需要使用这个browser_cookie3之前，需要随便登录一个xueqiu的网址
（回答你的问题，xq_a_token不需要登录雪球，就存在xq_a_token），
所以，随便访问一下雪球的任何一个页面，浏览器就能缓存xq_a_token了，咱们就能通过browser_cookie3来获取xq_a_token
使用browsercookie获取浏览器的cookies
http://www.wjhsh.net/amiza-p-10175543.html
参考：UniversalRotation.py

# 2022-6-4 手机访问token
https://blog.csdn.net/zeh_521/article/details/123262201
mitm也可以：https://mitmproxy.org/
一般需要啥数据就从雪球App上点点 抓包看，
比如找到F10地址：https://xueqiu.com/stock/f10/compinfo.json?symbol=SZ000501




