echo off
set DIR="%cd%"
set DIR="c:\www\wgo\sgf"
set name=157-p200_v_zen7-s7500-100

del cmd_sgflist

for /R %DIR% %%f in (%name%*.sgf) do ( 
echo loadsgf %%f
echo loadsgf %%f >> cmd_sgflist
)

echo quit >> cmd_sgflist

type cmd_sgflist | c:\Python27\python.exe c:\github\Webgo\svr\zen7.py > %name%.score

del cmd_sgflist