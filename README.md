# auto 2048

An bot to play 2048 game.

ongoing:

- using opencv to "read" the table.
- optimize matching strategy (separate screenshot to avoid multiple comparisons)

first version:

- pyautogui for screenshot
- locate all possible blocks on screen
- calculate possible moves and score
- move

每个循环大约需要 0.8 s, 速度还明显较慢, demo 不够连贯. 猜测是截图模块较慢限制了速度.

使用 [cProfile](http://frank-the-obscure.me/2016/02/08/python-profilers/) 模块评估代码, 寻找较慢的步骤:

~~~
Thu Jan  5 23:37:29 2017    restats

         279444 function calls (276899 primitive calls) in 117.692 seconds

   Ordered by: cumulative time
   List reduced from 442 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     21/1    0.001    0.000  117.692  117.692 {built-in method builtins.exec}
        1    0.061    0.061  117.692  117.692 2048.py:182(main)
      100    0.030    0.000   84.009    0.840 2048.py:7(get_screen)
     1752    1.634    0.001   55.655    0.032 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/pyscreeze/__init__.py:101(_locateAll_opencv)
     1000   39.306    0.039   39.306    0.039 {matchTemplate}
      600   33.233    0.055   33.233    0.055 {built-in method time.sleep}
      100    0.224    0.002   28.300    0.283 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/pyscreeze/__init__.py:316(_screenshot_osx)
      100    0.026    0.000   14.630    0.146 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:552(call)
      200    0.013    0.000   14.087    0.070 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:1611(wait)
      100    0.001    0.000   14.072    0.141 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:1598(_try_wait)
      100   14.071    0.141   14.071    0.141 {built-in method posix.waitpid}
      100    0.013    0.000   13.305    0.133 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/Image.py:1017(crop)
     2000    0.052    0.000   13.254    0.007 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/pyscreeze/__init__.py:64(_load_cv2)
      100    0.031    0.000   12.947    0.129 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/ImageFile.py:120(load)
     4618   11.753    0.003   11.753    0.003 {method 'decode' of 'ImagingDecoder' objects}
     1000    6.575    0.007    6.575    0.007 {method 'copy' of 'numpy.ndarray' objects}
      100    0.001    0.000    3.501    0.035 2048.py:176(action)
     1000    0.714    0.001    3.104    0.003 {built-in method numpy.core.multiarray.array}
     1000    0.022    0.000    2.390    0.002 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/Image.py:618(__array_interface__)
     1000    0.048    0.000    2.364    0.002 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/Image.py:654(tobytes)
~~~

可以看到, 大部分时间在获取游戏进程的函数 `get_screen()`

不过, 截图函数用时并不是最多的. 平均每次用时 0.283 s. 而 locateAll 函数用时更多, 大约是截图函数的两倍.

因此, 目前代码的速度问题应从 locateAll 和 screenshot 两方面出发解决.

从 locateAll 考虑

- 剪切截图成为多个图片直接匹配
- 限制图片搜索的最大值(当数字较小时, 不必搜索较大的数字) commit 513de23

后者不需引入新函数, 因此相对较容易实现, 实现后在游戏初期提速明显(<32 时用时几乎减半), 但后期速度变化不大(128/256 时几乎没有效果了).

针对前者, 从理论上分析, 当图片减小时, 匹配的时间成本应显著下降(大约在O(mn)量级), 不妨取半屏作为对照测试.

相关用时下降近半, 但值得注意的是, cProfile 的函数调用次数随图片变小而下降, 可能与 pyscreeze 库的具体实现有关.

换用不同大小的 block 匹配, 发现 block 很小时反而会用更长的时间.


剪切截图成为多个图片, 随后从小到大匹配可能的方格:

- 建立剪切的坐标系(尽量用相对坐标系)
- 标准图片库
- 逐个匹配

建立坐标系时发现图片可能会有 1 像素的漂移, 初步实现方案中计划使用一次搜索以消除漂移的影响. 后续再研究是否可直接用绝对位置匹配.

标准图片库可用 `cv2.imread()` 方便地读取. 使用 list 保存, 从而可实现从小到大逐个比较.

初步测试平均用时迅速降低到 ~0.5s

~~~
         52360 function calls (51415 primitive calls) in 16.464 seconds

   Ordered by: cumulative time
   List reduced from 437 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     21/1    0.001    0.000   16.464   16.464 {built-in method builtins.exec}
        1    0.018    0.018   16.464   16.464 2048.py:267(main)
       20    0.037    0.002    9.657    0.483 2048.py:43(get_screen)
      120    6.646    0.055    6.646    0.055 {built-in method time.sleep}
       20    0.045    0.002    5.826    0.291 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/pyscreeze/__init__.py:316(_screenshot_osx)
     1603    3.381    0.002    3.381    0.002 {matchTemplate}
       20    0.004    0.000    2.980    0.149 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:552(call)
       40    0.002    0.000    2.897    0.072 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:1611(wait)
       20    0.000    0.000    2.895    0.145 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/subprocess.py:1598(_try_wait)
       20    2.895    0.145    2.895    0.145 {built-in method posix.waitpid}
       20    0.002    0.000    2.762    0.138 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/Image.py:1017(crop)
       20    0.007    0.000    2.678    0.134 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/PIL/ImageFile.py:120(load)
     1131    2.445    0.002    2.445    0.002 {method 'decode' of 'ImagingDecoder' objects}
       20    0.000    0.000    0.763    0.038 2048.py:255(action)
       20    0.001    0.000    0.443    0.022 /Users/mofrankhu/.pyenv/versions/3.5.1/Python.framework/Versions/3.5/lib/python3.5/site-packages/pyautogui/__init__.py:900(press)
~~~

进一步提升:

只搜索可能产生新方块的位置. 由于一次最多刷新一个 2 或 4, 因此可中途结束搜索, 总搜索成本相当低.

用时压缩到 0.3-0.4 s, 其中接近 0.3 s 被截图消耗. 暂时可优化至此.
