@rem leela-zero
@if not "%BOARD_SIZE%"=="19" @(
  @set lz_cmd=c:\go\leela-zero\leelaz-%BOARD_SIZE%-
) else (
  @set lz_cmd=c:\go\leela-zero\leelaz-
)

@if not "%2"=="0.13-cpu" @(
  @set lz_para=-g -d -r%LZ_RESIGN% -t%LZ_THREAD_NUM% --noponder --timemanage off --ladder 1
) else (
  @set lz_para=-g -d -r%LZ_RESIGN% -t%LZ_THREAD_NUM% --noponder --timemanage off
)
@if not "%6"=="0.13-cpu" @(
  @set lz_para=-g -d -r%LZ_RESIGN% -t%LZ_THREAD_NUM% --noponder --timemanage off --ladder 1
) else (
  @set lz_para=-g -d -r%LZ_RESIGN% -t%LZ_THREAD_NUM% --noponder --timemanage off
)

@rem zen7 parameters
@set zen_cmd=c:\python27\python.exe c:\github\Webgo\svr\zen7.py
@set zen_para=-t%ZEN_THREAD_NUM% -r%ZEN_RESIGN% --interval %ZEN_INTERVAL%

@if "%1"=="LZ" @(
  @set lz_ver=%2
  @set lz_weight_filename=%3
  @set lz_visits=%4
  @goto set_lz_ai1
) else (
  @set zen_ver=%2
  @set zen_type=%3
  @set zen_top=%4
  @goto set_zen_ai1
)

:ai2
@if "%5"=="LZ" @(
  @set lz_ver=%6
  @set lz_weight_filename=%7
  @set lz_visits=%8
  @goto set_lz_ai2
) else (
  @set zen_ver=%6
  @set zen_type=%7
  @set zen_top=%8
  @goto set_zen_ai2
)

:set_lz_ai1
@set tmpstr=%lz_weight_filename%
:split
@for /f "tokens=1,* delims=\" %%i in ("%tmpstr%") do @(
  @set tmpstr=%%j
)
@if not "%tmpstr%"=="" set lz_weight=%tmpstr%
@if not "%tmpstr%"=="" goto split

@set ai1_prg=%lz_cmd%%lz_ver%.exe
@set ai1_para=%lz_para% -%lz_visits% -w %lz_weight_filename%
@set lz_w=%lz_weight:~0,-3%
@set ai1_label=%lz_w:~0,8%-%lz_visits%
@set ai1="%ai1_prg% %ai1_para%"

@goto ai2

:set_zen_ai1
@set ai1_prg=%zen_cmd%
@set ai1_para=%zen_para% -n%zen_type% -dc:\go\zen%zen_type%\zen.dll -s%zen_top% %ZEN_SPEC1%
@if "%ZEN_LABEL1%"=="" @(
  @set ai1_label=zen%zen_type%-s%zen_top%
) else (
  @set ai1_label=zen%zen_type%-%ZEN_LABEL1%
)
@set ai1="%ai1_prg% %ai1_para%"

@goto ai2

:set_lz_ai2
@set tmpstr=%lz_weight_filename%
:split
@for /f "tokens=1,* delims=\" %%i in ("%tmpstr%") do @(
  @set tmpstr=%%j
)
@if not "%tmpstr%"=="" set lz_weight=%tmpstr%
@if not "%tmpstr%"=="" goto split

@set ai2_prg=%lz_cmd%%lz_ver%.exe
@set ai2_para=%lz_para% -%lz_visits% -w %lz_weight_filename%
@set lz_w=%lz_weight:~0,-3%
@set ai2_label=%lz_w:~0,8%-%lz_visits%
@set ai2="%ai2_prg% %ai2_para%"

@goto match

:set_zen_ai2
@set ai2_prg=%zen_cmd%
@set ai2_para=%zen_para% -n%zen_type% -dc:\go\zen%zen_type%\zen.dll -s%zen_top% %ZEN_SPEC2%
@if "%ZEN_LABEL2%"=="" @(
  @set ai2_label=zen%zen_type%-s%zen_top%
) else (
  @set ai2_label=zen%zen_type%-%ZEN_LABEL2%
)
@set ai2="%ai2_prg% %ai2_para%"

@goto match

:match
@rem gogui-twogtp parameters
@if not "%BOARD_SIZE%"=="19" @(
  @set tmpround=%BOARD_SIZE%-%ROUND%
) else (
  @set tmpround=%ROUND%-F
)
@set para=-size %BOARD_SIZE% -komi %KOMI% -verbose -auto -games %ROUND% -time %GAME_TIME%
@set referee=-referee "c:\python27\python.exe c:\github\Webgo\svr\zen7.py -n7 -dc:\go\zen7\zen.dll --referee"
@set openings=-openings c:\go\openings\%HANDICAP%
@if "%HANDICAP%"=="" @(
  @set sgftitle=%ai1_label%_v_%ai2_label%-%tmpround%
  @set para=%para% %referee% -alternate
) else (
  @set sgftitle=%ai1_label%-%HANDICAP%_v_%ai2_label%-%tmpround%
  @set para=%para% %referee% %openings%
)
@set logfile=%sgftitle%.log

@rem echo -black %ai1%
@rem echo -white %ai2%
@rem echo %para%
@rem echo -sgffile %sgftitle%
@rem echo %logfile%

@echo.
@echo %date% %time%
gogui-twogtp.exe -black %ai1% -white %ai2% %para% -sgffile %sgftitle% 1>>%logfile% 2>&1
