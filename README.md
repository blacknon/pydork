PyDork
======

## Description

Scraping and listing text and image searches on Google, Bing, DuckDuckGo, Baidu, Yahoo japan.

## Install

```bash
git clone https://github.com/blacknon/pydork
cd pydork
pip install ./
```

## How to use

### commandline tool

```shell
$ # search text at google
$ pydork search -n 10 -t google -- 'super mario'
Google: Text Search: super mario
Google: Finally got 10 links.
[GoogleSearch]: https://www.nintendo.co.jp/character/mario/
[GoogleSearch]: https://www.nintendo.co.jp/software/smb1/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/adala/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/ayama/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/aaaca/index.html
[GoogleSearch]: https://supermariorun.com/ja/
[GoogleSearch]: https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9E%E3%83%AA%E3%82%AA%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA
[GoogleSearch]: https://store-jp.nintendo.com/list/software/70010000034626.html
[GoogleSearch]: https://www.youtube.com/watch?v=z5nqRrqFFZI
[GoogleSearch]: https://www.nintendo.com/games/detail/super-mario-3d-world-plus-bowsers-fury-switch/

$ # search text at google, bing, duckduckgo, with selenium
$ pydork search -s -n 10 -t google bing duckduckgo -- 'super mario'
Google: Text Search: super mario
Bing: Text Search: super mario
DuckDuckGo: Text Search: super mario
Bing: Finally got 10 links.
[BingSearch]: https://www.nintendo.co.jp/software/smb1/index.html
[BingSearch]: https://www.nintendo.co.jp/character/mario/index.html
[BingSearch]: https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9E%E3%83%AA%E3%82%AA%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA
[BingSearch]: https://supermarioplay.com/
[BingSearch]: https://www.lego.com/ja-jp/campaigns/jp/supermario
[BingSearch]: https://supermariorun.com/ja/
[BingSearch]: https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9E%E3%83%AA%E3%82%AA%E3%83%96%E3%83%A9%E3%82%B6%E3%83%BC%E3%82%BA
[BingSearch]: https://supermariobros.io/
[BingSearch]: https://supermario-bros.co/
[BingSearch]: https://game-ac.com/free/mario/
Google: Finally got 10 links.
[GoogleSearch]: https://www.nintendo.co.jp/character/mario/
[GoogleSearch]: https://www.nintendo.co.jp/software/smb1/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/adala/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/ayama/index.html
[GoogleSearch]: https://www.nintendo.co.jp/switch/aaaca/index.html
[GoogleSearch]: https://supermariorun.com/ja/
[GoogleSearch]: https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9E%E3%83%AA%E3%82%AA%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA
[GoogleSearch]: https://store-jp.nintendo.com/list/software/70010000034626.html
[GoogleSearch]: https://store-jp.nintendo.com/feature_mar004.html
[GoogleSearch]: https://www.nintendo.com/games/detail/super-mario-3d-world-plus-bowsers-fury-switch/
DuckDuckGo: Finally got 10 links.
[DuckDuckGoSearch]: https://supermariobros.io/
[DuckDuckGoSearch]: https://supermarioplay.com/
[DuckDuckGoSearch]: https://mario.nintendo.com/
[DuckDuckGoSearch]: https://en.wikipedia.org/wiki/Super_Mario
[DuckDuckGoSearch]: https://supermario-game.com/
[DuckDuckGoSearch]: https://www.mario-flash.com/
[DuckDuckGoSearch]: https://supermario-bros.co/
[DuckDuckGoSearch]: https://www.youtube.com/watch?v=4noiYiEYg6Q
[DuckDuckGoSearch]: https://www.crazygames.com/t/mario
[DuckDuckGoSearch]: https://arcadespot.com/game/super-mario-64/

$ # search image at google, yahoo.co.jp with selenium and set html title...
$ pydork image -T -s -n 10 -t google yahoo -- 'legend of zelda'
Yahoo: Image Search: legend of zelda
Google: Image Search: legend of zelda
Yahoo: Finally got 10 links.
[YahooSearch]: Amazon.co.jp: The Legend of Zelda: Breath of the Wild ...: https://m.media-amazon.com/images/I/81iU0U8VZML._AC_SL1500_.jpg
[YahooSearch]: Amazon | Legend of Zelda Link's Awakening(輸入版:北米 ...: https://m.media-amazon.com/images/I/91z5JYtUZAS._AC_SY445_.jpg
[YahooSearch]: Amazon | The Legend of Zelda: Breath of the Wild (輸入版 ...: https://m.media-amazon.com/images/I/61wcjVPx4sL._AC_SX466_.jpg
[YahooSearch]: Amazon | The Legend of Zelda Encyclopedia | Nintendo | Video ...: https://images-na.ssl-images-amazon.com/images/I/91zJdQWSE0L.jpg
[YahooSearch]: the-legend-of-zelda-breath-of- ...: https://www.nintendo.com//content/dam/noa/en_US/games/switch/t/the-legend-of-zelda-breath-of-the-wild-switch/the-legend-of-zelda-breath-of-the-wild-switch-hero.jpg
[YahooSearch]: Amazon | The Legend of Zelda: Twilight Princess, Vol. 7 (7 ...: https://images-na.ssl-images-amazon.com/images/I/81-c6fHsctL.jpg
[YahooSearch]: The Legend of Zelda™: Breath of the Wild - My Nintendo Store: https://assets.nintendo.eu/image/upload/f_auto,q_auto,t_product_tile_desktop/MNS/NOE/70010000000023/SQ_NSwitch_TheLegendOfZeldaBreathOfTheWild_E
[YahooSearch]: Amazon | Legend of Zelda 2020 Wall Calendar | Nintendo ...: https://images-na.ssl-images-amazon.com/images/I/61R+rBBQxaL._SX258_BO1,204,203,200_.jpg
[YahooSearch]: 359点のThe Legend Of Zeldaのストックフォト - Getty Images: https://media.gettyimages.com/photos/link-figurine-from-legend-of-zelda-with-shop-staff-inside-nintendo-picture-id1231509485?s=612x612
[YahooSearch]: Evolution of Legend of Zelda 1986-2020 - YouTube: https://i.ytimg.com/vi/1FwoEgUBgE0/maxresdefault.jpg
Google: Finally got 10 links.
[GoogleSearch]: LATEST* The Legend Of Zelda Breath Of The Wild 2: Nintendo Direct E3 2021,  Release Date, Leaked Info, Gameplay, Setting, Story Info, Trailers, & More: https://cdn.realsport101.com/images/ncavvykf/realsport-production/2db4094078e3c7e7442e33afb8e8e5e6082d3849-1920x1080.png?rect=0,1,1920,1077&w=328&h=184&auto=format
[GoogleSearch]: Jual The Legend of Zelda: Breath of the Wild Special Edition [EU] - Jakarta  Barat - Lionheartno Games Store | Tokopedia: https://images.tokopedia.net/img/cache/700/product-1/2017/1/16/9470651/9470651_4508d715-ecf7-452a-8150-df1a6a0c47ab_771_424.jpg
[GoogleSearch]: The Legend of Zelda: Breath of the Wild – Link has never been set so free |  Nintendo Switch | The Guardian: https://i.guim.co.uk/img/media/22d6b308c89e62e229feb220208a639836e31fd9/60_0_1800_1080/master/1800.png?width=700&quality=85&auto=format&fit=max&s=25c588a5203feea6061c32112a66ebdc
[GoogleSearch]: Kaos The Legend of Zelda c Nintendo, Fesyen Pria, Pakaian , Atasan di  Carousell: https://media.karousell.com/media/photos/products/2021/9/22/kaos_the_legend_of_zelda_c_nin_1632313294_5b47ea62_progressive.jpg
[GoogleSearch]: Sales of The Legend of Zelda titles worldwide 2019 | Statista: https://cdn.statcdn.com/Statistic/985000/985767-blank-355.png
[GoogleSearch]: Legend Of Zelda Monsters | Minimalis: http://tse2.mm.bing.net/th?id=OIP.wUtxfbukexwonASdvmIirgHaEK&pid=15.1
[GoogleSearch]: Everything The Legend of Zelda: Breath of the Wild 2 is hiding: full  analysis - The Legend of Zelda: Breath of the Wild II - Gamereactor: https://www.gamereactor.eu/media/08/legendzelda_3500863.jpg
[GoogleSearch]: The Legend of Zelda: A Link Between Worlds (Video Game 2013) - IMDb: https://m.media-amazon.com/images/M/MV5BZDI2M2IwMDItOTU4MS00YzdjLWJmYjItMzA3MjJjMDk2YjBiXkEyXkFqcGdeQXVyNjY5NTM5MjA@._V1_.jpg
[GoogleSearch]: The Complete Chronological Order Of Legend Of Zelda Games: https://static0.gamerantimages.com/wordpress/wp-content/uploads/2021/01/Zelda-Four-Swords-Adventures-Links.jpg?q=50&fit=crop&w=1400&dpr=1.5
[GoogleSearch]: Sword Slash Png - Legend Of Zelda Skyward Sword Artwork Clipart (#1717847)  - PikPng: https://cpng.pikpng.com/pngl/s/90-907142_the-legend-of-zelda-legend-of-zelda-skyward.png

```

### python library

```python
from pydork.engine import SearchEngine

# SearchEngine
search_engine = SearchEngine()

search_engine.set('google')
search_result = search_engine.search('final fantasy')
```
